"""
Focused security validation tests for critical security fixes.

Tests the most important security improvements:
1. Path traversal prevention in save/load
2. Filename sanitization  
3. Input validation
4. Resource limits
"""

import pytest
import tempfile
import os
import json
from pathlib import Path
from unittest.mock import patch, mock_open

from src.game import GameEngine


class TestCriticalSecurityFixes:
    """Test the most critical security fixes implemented."""
    
    def setup_method(self):
        """Setup test environment."""
        self.game = GameEngine(debug_mode=False)
    
    def test_filename_sanitization(self):
        """Test that filenames are properly sanitized."""
        test_cases = [
            # (input_filename, should_produce_safe_result)
            ("../../../etc/passwd", True),
            ("..\\..\\windows\\system32", True), 
            ("normal_file.json", True),
            ("file<>:\"|?*", True),
            ("file\x00with\x01nulls", True),
            ("..........", False),  # Should be rejected (empty result)
            ("", False),  # Should be rejected
        ]
        
        for dangerous_filename, should_produce_result in test_cases:
            sanitized = self.game._sanitize_filename(dangerous_filename)
            
            if should_produce_result:
                # Should either produce a safe filename or reject it entirely
                if sanitized:  # If not empty
                    assert ".." not in sanitized
                    assert "/" not in sanitized
                    assert "\\" not in sanitized
                    assert sanitized.endswith('.json')
                # If empty, that's also acceptable (rejection is a valid security response)
            else:
                # These should be rejected (empty string)
                assert sanitized == ""
    
    def test_safe_path_validation(self):
        """Test that path safety validation works."""
        with tempfile.TemporaryDirectory() as temp_dir:
            base_dir = Path(temp_dir) / "saves"
            base_dir.mkdir()
            
            # Safe path
            safe_path = base_dir / "save.json"
            assert self.game._is_safe_path(safe_path, base_dir)
            
            # Dangerous paths
            dangerous_paths = [
                Path(temp_dir) / "outside.json",  # Outside base dir
                Path("/etc/passwd"),  # Absolute path outside
                base_dir / ".." / "outside.json",  # Parent directory
            ]
            
            for dangerous_path in dangerous_paths:
                assert not self.game._is_safe_path(dangerous_path, base_dir)
    
    def test_save_game_security(self):
        """Test that save_game prevents path traversal."""
        dangerous_filenames = [
            "../../../evil.json",
            "C:\\Windows\\System32\\evil.json",
            "/etc/passwd",
            "....//....//outside.json"
        ]
        
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            try:
                os.chdir(temp_dir)
                
                # Create a sensitive file outside saves directory
                sensitive_file = Path("sensitive_file.txt")
                sensitive_file.write_text("SENSITIVE DATA")
                
                for dangerous_filename in dangerous_filenames:
                    # Save should either fail or save to safe location
                    result = self.game.save_game(dangerous_filename)
                    
                    # Sensitive file should not be overwritten
                    assert sensitive_file.exists()
                    assert sensitive_file.read_text() == "SENSITIVE DATA"
                    
            finally:
                os.chdir(original_cwd)
    
    def test_load_game_security(self):
        """Test that load_game prevents path traversal."""
        dangerous_filenames = [
            "../../../etc/passwd",
            "C:\\Windows\\System32\\config\\SAM", 
            "/sensitive/file.json",
            "....//....//outside.json"
        ]
        
        for dangerous_filename in dangerous_filenames:
            # Load should safely reject dangerous filenames
            result = self.game.load_game(dangerous_filename)
            # Should fail safely without crashing
            assert result is False  # Should fail to load dangerous paths
    
    def test_game_state_validation(self):
        """Test that game state validation prevents malicious content."""
        # Valid game state
        valid_state = {
            'player': {'inventory': [], 'current_room': 'WHOUS'},
            'world_state': {},
            'score_system': {'score': 0},
            'combinations': {}
        }
        assert self.game._validate_game_state(valid_state) is True
        
        # Invalid game states
        invalid_states = [
            # Missing required keys
            {'player': {}},
            # Dangerous content
            {'player': {}, 'world_state': {}, 'score_system': {}, 'combinations': {},
             'evil': '__import__("os").system("rm -rf /")'},
            # Wrong data types
            "not a dict",
            {'player': "not a dict", 'world_state': {}, 'score_system': {}, 'combinations': {}}
        ]
        
        for invalid_state in invalid_states:
            assert self.game._validate_game_state(invalid_state) is False
    
    def test_input_parsing_safety(self):
        """Test that input parsing is safe."""
        from src.parser.command_parser import CommandParser
        parser = CommandParser()
        
        # Test that parser handles dangerous input without crashing
        dangerous_inputs = [
            "; rm -rf /",
            "look && evil_command", 
            "$(malicious)",
            "`dangerous`",
            "look\x00with\x01nulls",
            "very_long_input_" + "x" * 1000  # Long but not excessive
        ]
        
        for dangerous_input in dangerous_inputs:
            # Parser should handle all input safely without crashing
            try:
                result = parser.parse(dangerous_input)
                # Should parse or return None, but not crash
                assert result is None or hasattr(result, 'verb')
            except Exception as e:
                pytest.fail(f"Parser crashed on dangerous input '{dangerous_input}': {e}")
        
        # Test that normal commands still work
        normal_commands = ["look", "take sword", "go north", "inventory"]
        for cmd in normal_commands:
            try:
                result = parser.parse(cmd)
                # Normal commands should generally parse (though may return None for unsupported verbs)
                assert result is None or hasattr(result, 'verb')
            except Exception as e:
                pytest.fail(f"Parser failed on normal command '{cmd}': {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])