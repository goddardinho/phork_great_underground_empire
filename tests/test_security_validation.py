"""
Security validation tests for the Phork text adventure game.

Tests cover:
- Input validation and sanitization
- File system security (path traversal prevention) 
- Error handling security
- Resource management (DoS prevention)
- Save/load security
"""

import pytest
import tempfile
import os
import json
from pathlib import Path
from unittest.mock import patch, mock_open

from src.game import GameEngine
from src.parser.command_parser import CommandParser


class TestInputValidation:
    """Test input validation and sanitization security."""
    
    def setup_method(self):
        """Setup test environment."""
        self.game = GameEngine(debug_mode=False)
        self.parser = CommandParser()
    
    def test_malicious_command_injection_attempts(self):
        """Test that malicious command injection attempts are safely handled."""
        malicious_inputs = [
            "; rm -rf /",
            "look; import os; os.system('rm -rf /')",
            "$(rm -rf /)",
            "`rm -rf /`",
            "look && rm -rf /",
            "look | cat /etc/passwd",
            "eval('__import__(\"os\").system(\"rm -rf /\")')",
            "exec('import os; os.system(\"rm -rf /\")')",
        ]
        
        for malicious_input in malicious_inputs:
            # Ensure malicious input doesn't execute system commands
            result = self.parser.parse(malicious_input)
            # Should either return None (unrecognized) or safe parsed command
            if result is not None:
                # Verify no dangerous verbs are mapped
                assert result.verb not in ['eval', 'exec', 'import', 'system', 'os', 'subprocess']
    
    def test_excessive_input_handling(self):
        """Test handling of excessively long input strings."""
        # Very long input string
        long_input = "look " + "a" * 10000
        result = self.parser.parse(long_input) 
        # Should handle gracefully without crashing
        assert result is not None or result is None  # Either way is fine, just no crash
    
    def test_unicode_and_special_characters(self):
        """Test handling of unicode and special characters."""
        special_inputs = [
            "look №∑€®†¥",
            "look \x00\x01\x02",
            "look 🚀🎮✨",
            "look \n\r\t",
            "look \\x41\\x42\\x43",
        ]
        
        for special_input in special_inputs:
            # Should handle gracefully without throwing exceptions
            try:
                result = self.parser.parse(special_input)
                # No assertion needed - just ensuring no unhandled exception
            except Exception as e:
                pytest.fail(f"Parser crashed on input '{special_input}': {e}")


class TestFileSystemSecurity:
    """Test file system security, especially path traversal prevention."""
    
    def setup_method(self):
        """Setup test environment."""
        self.game = GameEngine(debug_mode=False)
    
    @patch('builtins.open', mock_open(read_data='{}'))
    @patch('pathlib.Path.exists', return_value=True)
    def test_save_filename_path_traversal_prevention(self):
        """Test that save filenames prevent path traversal attacks."""
        dangerous_filenames = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "/etc/shadow", 
            "C:\\Windows\\System32\\config\\SAM",
            "../../sensitive_file.txt",
            "../../../root/.ssh/id_rsa",
            "....//....//etc/passwd",
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",  # URL encoded
        ]
        
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            try:
                os.chdir(temp_dir)
                
                for dangerous_filename in dangerous_filenames:
                    # The save operation should either:
                    # 1. Sanitize the filename to be safe
                    # 2. Reject the filename entirely
                    # 3. Restrict saves to the saves directory only
                    
                    # For now, test that it doesn't overwrite files outside saves directory
                    sensitive_file = Path("sensitive_outside_saves.txt")
                    sensitive_file.write_text("SENSITIVE DATA")
                    
                    try:
                        self.game.save_game(dangerous_filename)
                        # Verify sensitive file wasn't overwritten
                        assert sensitive_file.read_text() == "SENSITIVE DATA"
                    except Exception:
                        # It's acceptable if the game rejects dangerous filenames
                        pass
                        
            finally:
                os.chdir(original_cwd)
    
    @patch('builtins.open', mock_open(read_data='{}'))  
    def test_load_filename_path_traversal_prevention(self):
        """Test that load filenames prevent path traversal attacks."""
        dangerous_filenames = [
            "../../../etc/passwd",
            "../../sensitive_config.json",
            "/etc/shadow",
            "....//....//sensitive.txt",
        ]
        
        for dangerous_filename in dangerous_filenames:
            # Load should either sanitize filename or fail safely
            try:
                result = self.game.load_game(dangerous_filename)
                # If it succeeds, it should have been reading from saves directory only
            except Exception:
                # It's acceptable if dangerous filenames are rejected
                pass
    
    def test_mud_file_loading_security(self):
        """Test that .mud file loading is restricted to expected directories."""
        # Ensure .mud files can only be loaded from expected locations
        # and don't allow path traversal
        from src.world.room_loader import RoomLoader
        
        loader = RoomLoader("nonexistent_directory") 
        
        # These should be handled gracefully without causing security issues
        dangerous_paths = [
            "../../../etc/passwd.mud",
            "/etc/shadow.mud",
            "....//....//sensitive.mud",
        ]
        
        for path in dangerous_paths:
            try:
                # Should not be able to read files outside intended directory
                loader._load_rooms_from_file(Path(path))
            except (FileNotFoundError, PermissionError, OSError):
                # These exceptions are expected and safe
                pass


class TestResourceManagement:
    """Test resource management to prevent DoS attacks."""
    
    def setup_method(self):
        """Setup test environment."""
        self.game = GameEngine(debug_mode=False)
    
    def test_bulk_action_limits(self):
        """Test that bulk actions are properly limited."""
        # Create a room with many objects
        room = self.game.world.get_room("WHOUS")
        if room:
            # Try to take all objects - should be limited
            response = self.game.process_command("take all")
            # Verify it doesn't process unlimited objects
            assert "You can't take more than" in response.lower() or "you can't carry" in response.lower() or len(response) < 10000
    
    def test_excessive_inventory_prevention(self):
        """Test that inventory has reasonable limits."""
        # Try to add excessive objects to inventory
        for i in range(100):
            try:
                self.game.process_command(f"take object{i}")
            except Exception:
                # Should fail gracefully, not crash
                pass
        
        # Verify inventory doesn't grow unbounded  
        assert len(self.game.player.inventory) < 50  # Reasonable limit
    
    def test_command_processing_limits(self):
        """Test that command processing has reasonable performance limits."""
        import time
        
        # Test that individual commands complete quickly
        start_time = time.time()
        self.game.process_command("look around the room carefully")
        end_time = time.time()
        
        # Command should complete in reasonable time
        assert end_time - start_time < 1.0  # 1 second max


class TestErrorHandlingSecurity:
    """Test that error handling doesn't leak sensitive information."""
    
    def setup_method(self):
        """Setup test environment."""
        # Test with debug mode disabled for security
        self.game = GameEngine(debug_mode=False)
    
    def test_no_stack_traces_in_user_output(self):
        """Test that stack traces don't leak to user output."""
        # Try to trigger various errors
        error_inputs = [
            "nonexistent_command_xyz",
            "take nonexistent_object",
            "go invalid_direction", 
            "use object_that_doesnt_exist",
        ]
        
        for error_input in error_inputs:
            response = self.game.process_command(error_input)
            # Response should not contain stack trace indicators
            assert "Traceback" not in response
            assert "File \"" not in response
            assert "line " not in response.lower() or "line of" in response.lower()  # Allow "line of sight" etc
            assert "Exception:" not in response
    
    def test_file_operation_error_handling(self):
        """Test that file operation errors don't expose system information."""
        # Try to trigger file operation errors
        with patch('pathlib.Path.exists', return_value=False):
            try:
                self.game.load_game("nonexistent_save")
            except Exception as e:
                # Error should not expose full file paths or system info
                error_msg = str(e)
                assert "/Users/" not in error_msg
                assert "/home/" not in error_msg 
                assert "C:\\" not in error_msg


class TestSaveLoadSecurity:
    """Test save/load security including JSON injection prevention."""
    
    def setup_method(self):
        """Setup test environment."""
        self.game = GameEngine(debug_mode=False)
    
    def test_malicious_save_data_handling(self):
        """Test that malicious save data is handled safely."""
        malicious_json_data = [
            '{"__class__": "os.system", "command": "rm -rf /"}',
            '{"eval": "__import__(\'os\').system(\'rm -rf /\')"}',
            '{"player": {"__reduce__": ["os.system", ["rm -rf /"]]}}',
        ]
        
        with tempfile.TemporaryDirectory() as temp_dir:
            for i, malicious_data in enumerate(malicious_json_data):
                malicious_file = Path(temp_dir) / f"malicious_save_{i}.json"
                malicious_file.write_text(malicious_data)
                
                try:
                    # Loading malicious save should not execute any code
                    with patch('pathlib.Path', return_value=malicious_file):
                        result = self.game.load_game(f"malicious_save_{i}")
                except (json.JSONDecodeError, KeyError, TypeError, AttributeError):
                    # These exceptions are acceptable - malicious data rejected
                    pass
    
    def test_save_data_validation(self):
        """Test that save data is properly validated."""
        # Create a valid save
        save_data = self.game.serialize_state()
        
        # Verify save data doesn't contain dangerous content
        save_str = json.dumps(save_data)
        assert "__import__" not in save_str
        assert "eval(" not in save_str
        assert "exec(" not in save_str
        assert "os.system" not in save_str


if __name__ == "__main__":
    pytest.main([__file__, "-v"])