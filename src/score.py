"""Canonical Zork scoring system based on original 1978 MIT implementation."""

from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class ScoreRank(Enum):
    """Player rankings based on score percentage (from original rooms.mud)."""
    BEGINNER = "Beginner"
    INCOMPETENT = "Incompetent" 
    AMATEUR_ADVENTURER = "Amateur Adventurer"
    NOVICE_ADVENTURER = "Novice Adventurer"
    JUNIOR_ADVENTURER = "Junior Adventurer"
    ADVENTURER = "Adventurer"
    HACKER = "Hacker"
    WINNER = "Winner"
    MASTER = "Master"
    WIZARD = "Wizard"
    CHEATER = "Cheater"  # Special case for 100%


@dataclass
class TreasureScore:
    """Represents the dual scoring values for a treasure (OFVAL/OTVAL system)."""
    ofval: int = 0  # Score for finding/taking the treasure
    otval: int = 0  # Score for placing in trophy case
    found: bool = False  # Whether treasure has been found
    deposited: bool = False  # Whether treasure has been placed in trophy case
    
    @property
    def current_value(self) -> int:
        """Get current point value based on state."""
        points = 0
        if self.found:
            points += self.ofval
        if self.deposited:
            points += self.otval
        return points


class ScoreManager:
    """Manages canonical Zork scoring system with OFVAL/OTVAL mechanics."""
    
    def __init__(self):
        """Initialize with canonical treasure values from original dung.mud."""
        self.treasures: Dict[str, TreasureScore] = self._create_canonical_treasures()
        self.achievement_scores: Dict[str, int] = {}
        self.moves: int = 0
        self.raw_score: int = 0
        
    def _create_canonical_treasures(self) -> Dict[str, TreasureScore]:
        """Create treasures with authentic OFVAL/OTVAL values from original Zork."""
        # From original dung.mud source - exact values
        return {
            "JEWELED_EGG": TreasureScore(ofval=5, otval=10),  # Line 4318-4319
            "BAUBLE": TreasureScore(ofval=10, otval=10),      # Line 4647-4648  
            "BRASS_LANTERN": TreasureScore(ofval=15, otval=10), # Line 4678-4679
            "CRYSTAL_SKULL": TreasureScore(ofval=6, otval=6),   # Line 4699-4700
            "COIN": TreasureScore(ofval=10, otval=10),          # Line 4765-4766
            "PAINTING": TreasureScore(ofval=10, otval=10),      # Line 5369-5370
            "CHALICE": TreasureScore(ofval=10, otval=12),       # Line 5397-5398
            "TRIDENT": TreasureScore(ofval=15, otval=8),        # Line 5518-5519
            "BRACELET": TreasureScore(ofval=10, otval=13),      # Line 5668-5669
            "COFFIN": TreasureScore(ofval=15, otval=8),         # Line 5859-5860
            "PLATINUM_BAR": TreasureScore(ofval=15, otval=10),  # Line 6098-6099
            "DIAMOND": TreasureScore(otval=5, ofval=10),        # Line 6133-6134
        }
    
    @property
    def max_score(self) -> int:
        """Calculate maximum possible score (sum of all OFVAL + OTVAL)."""
        return sum(t.ofval + t.otval for t in self.treasures.values()) + sum(self.achievement_scores.values())
    
    @property 
    def current_score(self) -> int:
        """Calculate current total score."""
        treasure_points = sum(t.current_value for t in self.treasures.values())
        achievement_points = sum(self.achievement_scores.values())
        return treasure_points + achievement_points + self.raw_score
    
    @property
    def percentage(self) -> float:
        """Get score as percentage of maximum possible."""
        max_points = self.max_score
        return self.current_score / max_points if max_points > 0 else 0.0
    
    def find_treasure(self, treasure_id: str) -> int:
        """Award OFVAL points for finding a treasure. Returns points awarded."""
        treasure_id = treasure_id.upper()
        if treasure_id in self.treasures and not self.treasures[treasure_id].found:
            self.treasures[treasure_id].found = True
            return self.treasures[treasure_id].ofval
        return 0
    
    def deposit_treasure(self, treasure_id: str) -> int:
        """Award OTVAL points for depositing treasure in trophy case. Returns points awarded.""" 
        treasure_id = treasure_id.upper()
        if treasure_id in self.treasures and not self.treasures[treasure_id].deposited:
            self.treasures[treasure_id].deposited = True
            return self.treasures[treasure_id].otval
        return 0
    
    def add_achievement(self, achievement_id: str, points: int) -> None:
        """Add achievement-based score (like lighting shaft, solving puzzles)."""
        self.achievement_scores[achievement_id] = points
    
    def increment_moves(self) -> None:
        """Increment move counter."""
        self.moves += 1
    
    def get_rank(self) -> ScoreRank:
        """Get player ranking based on score percentage (from original rooms.mud)."""
        pct = self.percentage
        
        # Authentic ranking thresholds from original source
        if pct >= 1.0:
            return ScoreRank.CHEATER  # 100% completion
        elif pct > 0.95:
            return ScoreRank.WIZARD
        elif pct > 0.9:
            return ScoreRank.MASTER  
        elif pct > 0.8:
            return ScoreRank.WINNER
        elif pct > 0.6:
            return ScoreRank.HACKER
        elif pct > 0.4:
            return ScoreRank.ADVENTURER
        elif pct > 0.2:
            return ScoreRank.JUNIOR_ADVENTURER
        elif pct > 0.1:
            return ScoreRank.NOVICE_ADVENTURER
        elif pct > 0.05:
            return ScoreRank.AMATEUR_ADVENTURER
        elif pct == 0.0:
            return ScoreRank.BEGINNER
        else:
            return ScoreRank.INCOMPETENT
    
    def get_score_report(self) -> str:
        """Generate canonical score display matching original Zork format."""
        score = self.current_score
        max_score = self.max_score
        moves = self.moves
        rank = self.get_rank()
        
        # Authentic format from original rooms.mud SCORE function
        move_text = "move" if moves == 1 else "moves"
        
        report = f"Your score is {score} [total of {max_score} points], in {moves} {move_text}.\n"
        report += f"This score gives you the rank of {rank.value}."
        
        return report
    
    def get_treasure_status(self) -> Dict[str, Dict[str, bool]]:
        """Get status of all treasures for debugging/testing."""
        return {
            treasure_id: {
                "found": treasure.found,
                "deposited": treasure.deposited,
                "current_points": treasure.current_value
            }
            for treasure_id, treasure in self.treasures.items()
        }