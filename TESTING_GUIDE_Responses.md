# Snarky Response System - Testing Guide

## 🧪 **Comprehensive Test Scenarios**

### **1. Easter Egg Commands** (Should give special responses)
```
xyzzy         → "A hollow voice says 'Fool.'" (or variations)
plugh         → "Nothing happens." (or "A hollow voice says 'Plugh.'")
hello         → "Hello there!" / "Nice to meet you." / etc.
zork          → "At your service!" / "The Great Underground Empire lives on!"
pray          → "If you insist... but nothing happens."
curse         → "Such language in a high-class establishment like this!"
swear         → "Mind your manners!"
jump          → "You jump on the spot, to no particular effect." / "Wheeeeee!!!"
scream        → "Aargh!" / "You scream. No one seems to care."
dance         → "Dancing isn't a particularly useful skill here."
sing          → "Your singing is abominable." / "You hum a little tune."
sleep         → "You're not tired right now."
wake          → "You're already awake."
think         → "A good idea." / "You think, therefore you are."
whistle       → "You whistle a little tune."
```

### **2. Unknown Commands** (Should vary responses)
Try these multiple times to see different responses:
```
blahblah      → Various: "I don't understand that." / "Huh?" / "What?" / etc.
foobar        → Should show: "I don't know the word 'foobar'."
zxcvbnm       → Different response each time
randomword    → Random from our unknown_commands list
```

### **3. Movement Responses**
```
e             → "You can't go that way." (or variations like "There's no way to go there.")
northeast     → Should give varied "can't go" responses
up            → Test blocked movement responses
```

### **4. Object Interaction Responses**  
```
take blah     → "I don't see blah here." (or "What blah?" / "There's no blah here.")
take sword    → Different "don't see object" response
examine xyz   → Various object not found responses
drop nothing  → Should handle missing objects gracefully
```

### **5. Response Variation Testing**
Run the same command multiple times to verify randomization:
```
- Try "blahblah" 5 times → Should get different responses
- Try "e" 3 times       → Should get different "can't go" messages
- Try "take foo" 3 times → Should get different "don't see" messages
```

### **6. Working Commands** (Should work normally)
```
look          → Room description (no snarky response)
help          → Help text (normal behavior)
n             → Move north (if possible)
s             → Move south (if possible)
inventory     → Show inventory (normal)
```

## 🎯 **What to Look For:**

✅ **Variety**: No repetitive "I don't understand that"  
✅ **Personality**: Snarky, witty, Zork-like responses  
✅ **Easter Eggs**: Special commands give unique responses  
✅ **Randomization**: Same invalid command gives different responses  
✅ **Context**: Object names appear correctly in responses  

## 📋 **Quick Test Session:**
1. Start: `python3 main.py`
2. Try 3-4 Easter eggs: `xyzzy`, `hello`, `jump`, `curse`
3. Try same unknown command 3 times: `blahblah`
4. Try blocked movements: `e`, `up`, `northeast`  
5. Try missing objects: `take sword`, `examine crystal`
6. Verify normal commands still work: `look`, `help`, `n`

---
**Goal**: Confirm authentic Zork personality with varied, witty responses! 🎮