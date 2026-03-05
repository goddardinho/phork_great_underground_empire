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
        # Comprehensive verb synonyms based on original Zork vocabulary
        self.verb_synonyms = {
            # Movement commands (single letter shortcuts)
            "n": "north", "s": "south", "e": "east", "w": "west",
            "ne": "northeast", "nw": "northwest", "se": "southeast", "sw": "southwest",
            "u": "up", "d": "down",
            
            # Movement variations
            "go": "go", "walk": "go", "run": "go", "move": "go", "head": "go",
            "climb": "climb", "ascend": "climb", "descend": "climb",
            "enter": "enter", "exit": "exit", "leave": "exit",
            
            # Examination commands
            "l": "look", "look": "look", "gaze": "look", "stare": "look", "peer": "look",
            "examine": "examine", "x": "examine", "check": "examine", "inspect": "examine",
            "study": "examine", "search": "examine", "scan": "examine",
            
            # Inventory and item commands  
            "i": "inventory", "inv": "inventory", "inventory": "inventory",
            "take": "take", "pick": "take", "grab": "take", 
            "carry": "take", "hold": "take", "acquire": "take", "obtain": "take",
            "drop": "drop", "put": "put", "place": "put", "set": "put",
            "throw": "drop", "discard": "drop", "release": "drop", "leave": "drop",
            
            # Container interactions
            "get": "get", "retrieve": "get", "extract": "get", "remove": "get",
            "put": "put", "place": "put", "insert": "put", "stuff": "put",
            "open": "open", "close": "close", "shut": "close",
            
            # Combat and interaction
            "attack": "attack", "kill": "attack", "hit": "attack", "strike": "attack",
            "fight": "attack", "beat": "attack", "slay": "attack", "murder": "attack",
            "swing": "attack", "stab": "attack", "cut": "attack", "slash": "attack",
            
            # Reading and communication
            "read": "read", "r": "read", "peruse": "read", "scan": "read",
            "say": "say", "speak": "say", "talk": "say", "tell": "say",
            "shout": "say", "yell": "say", "scream": "say", "whisper": "say",
            
            # Manipulation commands
            "turn": "turn", "rotate": "turn", "twist": "turn", "spin": "turn",
            "push": "push", "press": "push", "shove": "push", "move": "push",
            "pull": "pull", "drag": "pull", "yank": "pull", "tug": "pull",
            "touch": "touch", "feel": "touch", "handle": "touch", "finger": "touch",
            "rub": "rub", "polish": "rub", "clean": "rub", "wipe": "rub",
            
            # Tool usage
            "use": "use", "employ": "use", "utilize": "use", "apply": "use", "wield": "use",
            "wear": "wear", "don": "wear", "put on": "wear",
            "remove": "remove", "take off": "remove", "doff": "remove",
            
            # Locks and keys
            "unlock": "unlock", "lock": "lock", "secure": "lock",
            
            # Light sources
            "light": "light", "ignite": "light", "kindle": "light", "burn": "light",
            "extinguish": "extinguish", "put out": "extinguish", "douse": "extinguish",
            "blow out": "extinguish", "quench": "extinguish", "snuff": "extinguish",
            
            # Eating and drinking
            "eat": "eat", "consume": "eat", "devour": "eat", "bite": "eat", "taste": "eat",
            "drink": "drink", "sip": "drink", "gulp": "drink", "swallow": "drink",
            
            # Game control
            "quit": "quit", "q": "quit", "exit": "quit", "bye": "quit", "goodbye": "quit",
            "save": "save", "restore": "restore", "load": "restore", 
            "restart": "restart", "again": "again", "g": "again",
            "undo": "undo", "oops": "oops", "o": "oops",
            
            # Information commands
            "help": "help", "?": "help", "hint": "help", "info": "help",
            "score": "score", "status": "score", "points": "score",
            "time": "time", "wait": "wait", "z": "wait", "rest": "wait", "sleep": "wait",
            
            # Display modes
            "brief": "brief", "terse": "brief", "short": "brief",
            "verbose": "verbose", "long": "verbose", "full": "verbose", "wordy": "verbose",
            
            # Special Zork commands
            "pray": "pray", "curse": "curse", "swear": "curse", "damn": "curse",
            "hello": "hello", "hi": "hello", "greetings": "hello",
            "diagnose": "diagnose", "health": "diagnose",
            "kiss": "kiss", "hug": "kiss", "embrace": "kiss",
            "jump": "jump", "leap": "jump", "hop": "jump", "bounce": "jump",
            
            # Navigation helpers
            "north": "north", "south": "south", "east": "east", "west": "west",
            "northeast": "northeast", "northwest": "northwest", 
            "southeast": "southeast", "southwest": "southwest",
            "up": "up", "down": "down", "in": "in", "out": "out"
        }
        
        # Noun synonyms for common objects
        self.noun_synonyms = {
            # Light sources
            "lantern": "lamp", "flashlight": "lamp", "torch": "torch", "candle": "candle",
            
            # Containers
            "box": "box", "chest": "chest", "case": "case", "bag": "bag", "sack": "bag",
            "bottle": "bottle", "jar": "bottle", "container": "box",
            
            # Weapons and tools
            "sword": "sword", "blade": "sword", "knife": "knife", "dagger": "knife",
            "axe": "axe", "hammer": "hammer", "key": "key",
            
            # Common items
            "rope": "rope", "string": "rope", "cord": "rope", "chain": "rope",
            "paper": "paper", "note": "paper", "letter": "paper", "document": "paper",
            "book": "book", "manual": "book", "tome": "book", "guide": "book",
            
            # Navigation
            "door": "door", "gate": "door", "entrance": "door", "exit": "door",
            "window": "window", "opening": "window", "hole": "opening",
            "passage": "passage", "corridor": "passage", "hallway": "passage",
            "stairs": "stairs", "steps": "stairs", "stairway": "stairs", "staircase": "stairs",
            
            # Natural features  
            "tree": "tree", "bush": "tree", "plant": "tree", "shrub": "tree",
            "rock": "rock", "stone": "rock", "boulder": "rock",
            "water": "water", "river": "water", "stream": "water", "lake": "water",
            
            # Abstract concepts
            "self": "self", "me": "self", "myself": "self",
            "all": "all", "everything": "all", "stuff": "all", "things": "all"
        }
        
        # Extended prepositions for complex commands
        self.prepositions = {
            "with", "using", "to", "at", "in", "on", "under", "beneath", "below",
            "behind", "from", "into", "onto", "upon", "off", "out", "through",
            "across", "over", "above", "beside", "near", "by", "against", "around"
        }
        
        # Multi-word verb synonyms (order matters - longer phrases first)
        self.multi_word_verbs = {
            "pick up": "take", "put out": "extinguish", "blow out": "extinguish", "snuff out": "extinguish",
            "take off": "remove", "put on": "wear",
            "throw away": "drop", "throw out": "drop", "toss away": "drop",
            "look at": "examine", "look up": "examine", "look in": "examine",
            "climb up": "climb", "climb down": "climb", "go up": "up", "go down": "down",
            "turn on": "light", "turn off": "extinguish", "switch on": "light", "switch off": "extinguish",
            "get up": "up", "sit down": "wait", "lie down": "wait", "stand up": "wait"
        }
        
        # Articles and fillers to ignore 
        self.articles = {"a", "an", "the", "my", "some", "any"}
    
    def parse(self, user_input: str) -> Optional[Command]:
        """Parse user input into a Command object."""
        if not user_input.strip():
            return None
            
        # Normalize input and handle multi-word verbs
        normalized_input = self._normalize_input(user_input.strip().lower())
        
        # Clean and tokenize input
        tokens = self._tokenize(normalized_input)
        if not tokens:
            return None
        
        # Extract verb (first meaningful word)
        verb = self._normalize_verb(tokens[0])
        
        # Parse remaining tokens for objects
        remaining_tokens = tokens[1:]
        noun, preposition, noun2 = self._extract_objects(remaining_tokens)
        
        # Apply noun synonyms
        if noun:
            noun = self._normalize_noun(noun)
        if noun2:
            noun2 = self._normalize_noun(noun2)
        
        return Command(verb, noun, preposition, noun2)
    
    def _normalize_input(self, text: str) -> str:
        """Handle multi-word verb phrases before tokenization."""
        # Replace multi-word verbs (longest first to avoid conflicts)
        for phrase, replacement in sorted(self.multi_word_verbs.items(), key=len, reverse=True):
            if text.startswith(phrase + " ") or text == phrase:
                text = text.replace(phrase, replacement, 1)
                break
        return text
    
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
    
    def _normalize_noun(self, noun: str) -> str:
        """Convert noun synonyms to standard form."""
        # Handle exact matches first
        if noun in self.noun_synonyms:
            return self.noun_synonyms[noun]
        
        # Handle partial matches for compound nouns
        words = noun.split()
        if len(words) > 1:
            # Check if any word is a synonym
            normalized_words = []
            for word in words:
                normalized_words.append(self.noun_synonyms.get(word, word))
            return " ".join(normalized_words)
        
        return noun
    
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