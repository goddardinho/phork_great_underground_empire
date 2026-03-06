"""Test suite for the canonical Zork scoring system."""

import unittest
import sys
import os

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from score import ScoreManager, ScoreRank, TreasureScore


class TestScoreManager(unittest.TestCase):
    """Test the canonical Zork scoring system."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.score_manager = ScoreManager()
    
    def test_initial_state(self):
        """Test initial score manager state."""
        self.assertEqual(self.score_manager.current_score, 0)
        self.assertEqual(self.score_manager.moves, 0)
        self.assertEqual(self.score_manager.get_rank(), ScoreRank.BEGINNER)
        self.assertGreater(self.score_manager.max_score, 200)  # Should be 243+ with all treasures
    
    def test_treasure_ofval_scoring(self):
        """Test OFVAL (finding treasure) scoring."""
        initial_score = self.score_manager.current_score
        
        # Test finding a treasure
        points = self.score_manager.find_treasure("JEWELED_EGG")
        self.assertEqual(points, 5)  # From original dung.mud
        self.assertEqual(self.score_manager.current_score, initial_score + 5)
        
        # Test finding same treasure again (should not award points)
        points = self.score_manager.find_treasure("JEWELED_EGG")
        self.assertEqual(points, 0)
        self.assertEqual(self.score_manager.current_score, initial_score + 5)
    
    def test_treasure_otval_scoring(self):
        """Test OTVAL (trophy case) scoring."""
        # First find the treasure
        self.score_manager.find_treasure("JEWELED_EGG")
        initial_score = self.score_manager.current_score
        
        # Test depositing treasure
        points = self.score_manager.deposit_treasure("JEWELED_EGG")
        self.assertEqual(points, 10)  # From original dung.mud
        self.assertEqual(self.score_manager.current_score, initial_score + 10)
        
        # Test depositing same treasure again (should not award points)
        points = self.score_manager.deposit_treasure("JEWELED_EGG")
        self.assertEqual(points, 0)
        self.assertEqual(self.score_manager.current_score, initial_score + 10)
    
    def test_achievement_scoring(self):
        """Test achievement-based scoring."""
        initial_score = self.score_manager.current_score
        
        self.score_manager.add_achievement("LIGHT_SHAFT", 10)
        self.score_manager.add_achievement("PUZZLE_SOLVED", 25)
        
        expected_score = initial_score + 10 + 25
        self.assertEqual(self.score_manager.current_score, expected_score)
    
    def test_move_counting(self):
        """Test move counter functionality."""
        initial_moves = self.score_manager.moves
        
        for i in range(5):
            self.score_manager.increment_moves()
        
        self.assertEqual(self.score_manager.moves, initial_moves + 5)
    
    def test_ranking_system(self):
        """Test the canonical ranking system."""
        # Test Beginner (0% completion)
        self.assertEqual(self.score_manager.get_rank(), ScoreRank.BEGINNER)
        
        # Simulate scoring to test different ranks
        test_manager = ScoreManager()
        
        # Award significant points to test ranking progression
        test_manager.find_treasure("JEWELED_EGG")
        test_manager.deposit_treasure("JEWELED_EGG") 
        test_manager.find_treasure("BAUBLE")
        test_manager.deposit_treasure("BAUBLE")
        test_manager.find_treasure("BRASS_LANTERN")
        test_manager.deposit_treasure("BRASS_LANTERN")
        test_manager.add_achievement("PUZZLES", 50)
        
        # Should be Junior Adventurer or Adventurer with this score
        rank = test_manager.get_rank()
        self.assertIn(rank, [ScoreRank.JUNIOR_ADVENTURER, ScoreRank.ADVENTURER, ScoreRank.AMATEUR_ADVENTURER])
    
    def test_canonical_treasure_values(self):
        """Test that treasure values match original Zork."""
        # Verify some key treasure values from original dung.mud
        treasures = self.score_manager.treasures
        
        self.assertEqual(treasures["JEWELED_EGG"].ofval, 5)
        self.assertEqual(treasures["JEWELED_EGG"].otval, 10)
        
        self.assertEqual(treasures["BAUBLE"].ofval, 10)
        self.assertEqual(treasures["BAUBLE"].otval, 10)
        
        self.assertEqual(treasures["BRASS_LANTERN"].ofval, 15)
        self.assertEqual(treasures["BRASS_LANTERN"].otval, 10)
    
    def test_score_report_format(self):
        """Test that score report matches canonical format."""
        # Add some moves and score
        for _ in range(10):
            self.score_manager.increment_moves()
        self.score_manager.find_treasure("COIN")
        
        report = self.score_manager.get_score_report()
        
        # Should match format: "Your score is X [total of Y points], in Z moves."
        self.assertIn("Your score is", report)
        self.assertIn("total of", report) 
        self.assertIn("points", report)
        self.assertIn("moves", report)
        self.assertIn("This score gives you the rank of", report)
    
    def test_treasure_status_tracking(self):
        """Test treasure status tracking."""
        # Initial state - no treasures found
        status = self.score_manager.get_treasure_status()
        for treasure_id, treasure_status in status.items():
            self.assertFalse(treasure_status["found"])
            self.assertFalse(treasure_status["deposited"])
            self.assertEqual(treasure_status["current_points"], 0)
        
        # Find a treasure
        self.score_manager.find_treasure("COIN")
        status = self.score_manager.get_treasure_status()
        coin_status = status["COIN"]
        self.assertTrue(coin_status["found"])
        self.assertFalse(coin_status["deposited"])
        self.assertEqual(coin_status["current_points"], 10)  # OFVAL only
        
        # Deposit the treasure  
        self.score_manager.deposit_treasure("COIN")
        status = self.score_manager.get_treasure_status()
        coin_status = status["COIN"]
        self.assertTrue(coin_status["found"])
        self.assertTrue(coin_status["deposited"])
        self.assertEqual(coin_status["current_points"], 20)  # OFVAL + OTVAL


if __name__ == "__main__":
    unittest.main()