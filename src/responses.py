"""Response system - Provides witty, authentic Zork-style responses."""

import random
from typing import List, Dict


class ZorkResponses:
    """Collection of authentic Zork-style snarky responses."""
    
    def __init__(self) -> None:
        # Unknown command responses - CANONICAL ZORK RESPONSES
        # Based on original parser.mud and action files  
        self.unknown_commands = [
            "Huh?",  # parser.mud line 327 - most common response
            "What?",  # close variant used in original
            "I beg your pardon?",  # parser.mud line 79 - for empty input
            "That doesn't make sense!", # parser.mud line 377 - exact quote
            "I don't know how to do that.", # act3.mud line 335 - exact quote
            "I don't understand that.", 
            "Come again?", 
            "I don't know the word \"{word}\".", # word-specific response
            "That's not a verb I recognize.",
            "I'm afraid I don't understand.",  
            "You can't do that here.",
            "That's not something you can do.",
        ]
        
        # Can't go that way responses
        self.cant_go_responses = [
            "You can't go that way.",
            "You can't go in that direction.",
            "There's no way to go there.",
            "That way is blocked.",
            "I don't see any path in that direction.",
            "There's nothing in that direction.",
            "You bump into something solid.",
        ]
        
        # Don't see object responses  
        self.dont_see_object = [
            "I don't see {object} here.",
            "There's no {object} here.",
            "I can't find {object} anywhere.",
            "What {object}?",
            "I don't see any {object} around.",
            "{object}? What {object}?",
        ]
        
        # Can't do that responses
        self.cant_do_that = [
            "I can't do that.",
            "That's not possible.",
            "You can't do that here.",
            "That doesn't work.",
            "Nice try, but that won't work.",
            "I'm afraid that's not feasible.",
        ]
        
        # Special command responses (Easter eggs)
        self.special_commands = {
            "xyzzy": [
                "Nothing happens.",
                "A hollow voice says \"Fool.\"",
                "The air shimmers for a moment.",
            ],
            "plugh": [
                "Nothing happens.",
                "A hollow voice says \"Plugh.\"",
            ],
            "hello": [
                "Hello there!",
                "Nice to meet you.",
                "How do you do?",
                "Greetings!",
            ],
            "zork": [
                "At your service!",
                "Zork is a registered trademark of Infocom, Inc.",
                "The Great Underground Empire lives on!",
            ],
            "pray": [
                "If you insist... but nothing happens.",
                "Your prayers are answered - nothing happens.",
                "The gods ignore your pleas.",
            ],
            "curse": [
                "Such language in a high-class establishment like this!",
                "Watch your tongue!",
                "Really now!",
            ],
            "swear": [
                "Such language in a high-class establishment like this!",
                "Mind your manners!",
            ],
            "jump": [
                "You jump on the spot, to no particular effect.",
                "Wheeeeee!!!",
                "Very good. Now you can go to the Olympics.",
            ],
            "scream": [
                "Aargh!",
                "*AAAAARRRRRRGGGGGGHHHHHHH*",
                "You scream. No one seems to care.",
            ],
            "dance": [
                "Dancing isn't a particularly useful skill here.",
                "You dance a little jig.",
                "Nice moves!",
            ],
            "sing": [
                "Your singing is abominable.",  
                "You hum a little tune.",
                "La de da de dum...",
            ],
            "sleep": [
                "You're not tired right now.",
                "This is no time for sleeping!",
                "You'd better stay alert.",
            ],
            "wake": [
                "You're already awake.",
                "I don't understand why you want to wake up; you're not asleep.",
            ],
            "swim": [
                "Swimming isn't possible here.",
                "There's no water here deep enough to swim in.",
            ],
            "cry": [
                "Crying isn't going to help matters.",
                "Boo hoo hoo.",
                "There's nothing to cry about here.",
            ],
            "laugh": [
                "That's not particularly funny.",
                "What's so amusing?",
                "Ha ha ha.",
            ],
            "think": [
                "A good idea.",
                "You think, therefore you are.",
                "I'm glad to see you're using your head.",
            ],
            "whistle": [
                "You whistle a little tune.",
                "*whistle*",
                "How melodious.",
            ],
        }
        
        # Inventory-related responses
        self.inventory_responses = {
            "empty_inventory": [
                "You are empty-handed.",
                "You aren't carrying anything.",
                "Your hands are empty.", 
                "You have nothing.",
            ],
            "already_have": [
                "You already have {object}.",
                "You're already carrying {object}.",
                "{object} is already in your possession.",
            ],
            "dont_have": [
                "You don't have that.",
                "You aren't carrying that.",
                "You don't seem to have that.",
                "That's not in your inventory.",
            ],
            "hands_full": [
                "Your hands are full.",
                "You're carrying too many things already.",
                "You can't carry any more.",
            ]
        }
        
        # Action-specific responses
        self.action_responses = {
            "already_open": [
                "It's already open.",
                "{object} is already open.",
            ],
            "already_closed": [
                "It's already closed.",
                "{object} is already closed.",
            ],
            "cant_open": [
                "You can't open {object}.",
                "{object} won't open.",
                "It doesn't open.",
            ],
            "cant_close": [
                "You can't close {object}.", 
                "{object} won't close.",
                "It doesn't close.",
            ],
            "not_container": [
                "{object} isn't something you can put things in.",
                "You can't put anything in {object}.",
                "That's not a container.",
            ],
            "nothing_inside": [
                "There's nothing in {object}.",
                "{object} is empty.",
                "You don't find anything inside.",
            ]
        }

    def get_unknown_command_response(self, input_text: str = "") -> str:
        """Get a random response for unknown commands."""
        response = random.choice(self.unknown_commands)
        if "{word}" in response and input_text:
            # Extract first word for the response
            first_word = input_text.split()[0] if input_text.split() else input_text
            response = response.replace("{word}", first_word)
        return response
    
    def get_special_command_response(self, command: str) -> str:
        """Get response for special Easter egg commands."""
        if command.lower() in self.special_commands:
            return random.choice(self.special_commands[command.lower()])
        return self.get_unknown_command_response(command)
    
    def get_cant_go_response(self) -> str:
        """Get a random 'can't go that way' response."""
        return random.choice(self.cant_go_responses)
    
    def get_dont_see_object_response(self, object_name: str) -> str:
        """Get a random 'don't see object' response."""
        response = random.choice(self.dont_see_object)
        return response.replace("{object}", object_name)
    
    def get_cant_do_that_response(self) -> str:
        """Get a random 'can't do that' response."""
        return random.choice(self.cant_do_that)
    
    def get_inventory_response(self, response_type: str, object_name: str = "") -> str:
        """Get inventory-related responses."""
        if response_type in self.inventory_responses:
            response = random.choice(self.inventory_responses[response_type])
            return response.replace("{object}", object_name)
        return "Something happened."
    
    def get_action_response(self, action_type: str, object_name: str = "") -> str:
        """Get action-specific responses."""
        if action_type in self.action_responses:
            response = random.choice(self.action_responses[action_type])
            return response.replace("{object}", object_name)
        return "Something happened."
    
    def is_special_command(self, command: str) -> bool:
        """Check if command is a special Easter egg command."""
        return command.lower() in self.special_commands


# Global response instance
responses = ZorkResponses()