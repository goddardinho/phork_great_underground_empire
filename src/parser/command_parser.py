"""Command parser - Handles user input and command interpretation."""

from typing import List, Dict, Optional, Tuple
import re


class Command:
    """Represents a parsed user command."""
    
    def __init__(self, verb: str, noun: Optional[str] = None, preposition: Optional[str] = None, 
                 noun2: Optional[str] = None):
        self.verb = verb.lower()
        self.noun = noun.lower() if noun else None
        self.preposition = preposition.lower() if preposition else None  
        self.noun2 = noun2.lower() if noun2 else None
    
    def __str__(self) -> str:
        parts = [self.verb]
        if self.noun:
            parts.append(self.noun)
        if self.preposition:
            parts.append(self.preposition)
        if self.noun2:
            parts.append(self.noun2)
        return " ".join(parts)


class CommandParser:
    """Parses user input into structured commands."""
    
    def __init__(self) -> None:
        # Basic verb synonyms - can be expanded
        self.verb_synonyms = {
            "n": "north", "s": "south", "e": "east", "w": "west",
            "ne": "northeast", "nw": "northwest", "se": "southeast", "sw": "southwest",
            "u": "up", "d": "down",
            "l": "look", "examine": "examine", "x": "examine",
            "i": "inventory", "inv": "inventory",
            "pick": "take", "grab": "take",
            "put": "put", "place": "put",
            "get": "get", "retrieve": "get",
            "quit": "q",
            # Object interactions
            "read": "read", "r": "read",
            "open": "open", "close": "close", 
            "unlock": "unlock", "lock": "lock",
            # Display modes
            "brief": "brief", "verbose": "verbose",
            # Light source commands
            "light": "light", "ignite": "light", "kindle": "light",
            "extinguish": "extinguish", "put out": "extinguish", "douse": "extinguish",
        }
        
        # Common prepositions
        self.prepositions = {
            "with", "using", "to", "at", "in", "on", "under", "behind", "from"
        }
        
        # Articles to ignore
        self.articles = {"a", "an", "the", "my"}
    
    def parse(self, user_input: str) -> Optional[Command]:
        """Parse user input into a Command object."""
        if not user_input.strip():
            return None
            
        # Clean and tokenize input
        tokens = self._tokenize(user_input.strip().lower())
        if not tokens:
            return None
        
        # Extract verb (first meaningful word)
        verb = self._normalize_verb(tokens[0])
        
        # Simple parsing - can be made more sophisticated
        remaining_tokens = tokens[1:]
        noun, preposition, noun2 = self._extract_objects(remaining_tokens)
        
        return Command(verb, noun, preposition, noun2)
    
    def _tokenize(self, text: str) -> List[str]:
        """Split text into tokens, removing punctuation and articles."""
        # Remove punctuation and split
        text = re.sub(r'[^\w\s]', ' ', text)
        tokens = text.split()
        
        # Remove articles
        tokens = [token for token in tokens if token not in self.articles]
        
        return tokens
    
    def _normalize_verb(self, verb: str) -> str:
        """Convert verb synonyms to standard form."""
        return self.verb_synonyms.get(verb, verb)
    
    def _extract_objects(self, tokens: List[str]) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """Extract noun, preposition, and second noun from remaining tokens."""
        if not tokens:
            return None, None, None
        
        # Find preposition if any
        preposition_index = None
        for i, token in enumerate(tokens):
            if token in self.prepositions:
                preposition_index = i
                break
        
        if preposition_index is None:
            # No preposition, treat all as one noun phrase
            noun = " ".join(tokens)
            return noun, None, None
        else:
            # Split around preposition
            noun1_tokens = tokens[:preposition_index]
            preposition = tokens[preposition_index]
            noun2_tokens = tokens[preposition_index + 1:]
            
            noun1 = " ".join(noun1_tokens) if noun1_tokens else None
            noun2 = " ".join(noun2_tokens) if noun2_tokens else None
            
            return noun1, preposition, noun2