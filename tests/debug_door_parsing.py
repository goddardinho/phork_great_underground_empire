#!/usr/bin/env python3
"""
Debug DOOR parsing to understand why LROOM->CELLA connection isn't working
"""

import re
from src.parsers.mdl_parser import MDLParser

# Create test content that mimics the LROOM definition
test_content = '''
<ROOM "LROOM"
       ""
       "Living Room"
       <EXIT "EAST" "KITCH"
              "WEST" <CEXIT "MAGIC-FLAG" "BLROO" "The door is nailed shut.">
              "DOWN" <DOOR "DOOR" "LROOM" "CELLA">>
       (<GET-OBJ "WDOOR"> <GET-OBJ "DOOR"> <GET-OBJ "TCASE"> 
        <GET-OBJ "LAMP"> <GET-OBJ "RUG"> <GET-OBJ "PAPER">
        <GET-OBJ "SWORD">)
       LIVING-ROOM
       <+ ,RLANDBIT ,RLIGHTBIT ,RHOUSEBIT ,RSACREDBIT>>
'''

def debug_exit_extraction():
    parser = MDLParser()
    
    # Test the new balanced bracket extraction
    exit_content = parser._extract_balanced_brackets(test_content, "<EXIT")
    if exit_content:
        print(f"Found EXIT content using balanced brackets:")
        print(f"'{exit_content}'")
        print()
        
        # Test parsing
        exits = parser._parse_exits(exit_content, "LROOM")
        print(f"Parsed exits: {exits}")
    else:
        print("No EXIT section found using balanced brackets")
        
    # Also test the old regex method for comparison
    exit_match = re.search(r'<EXIT\s+([^>]*)>', test_content, re.DOTALL)
    if exit_match:
        exit_content_old = exit_match.group(1)
        print(f"\nOld regex method found:")
        print(f"'{exit_content_old}'")
    else:
        print("\nNo EXIT section found using old regex")

if __name__ == '__main__':
    debug_exit_extraction()