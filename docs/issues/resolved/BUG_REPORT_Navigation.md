# Bug Report: Room Navigation Analysis

**Date:** March 5, 2026  
**Reporter:** User Navigation Test  
**Status:** ✅ RESOLVED

## Issue Description
User reports: "Moving east from the field still takes us to behind the house"

## 🐛 **ACTUAL BUG IDENTIFIED AND FIXED:**

### Problem Found:
EHOUS room was displaying as **"East of House"** due to incorrect hardcoded mapping in MDL parser, but the original .mud file defines it as **"Behind House"**.

### Root Cause:
In [src/parsers/mdl_parser.py](src/parsers/mdl_parser.py) line 137:
```python
# WRONG - was overriding .mud file data:
"EHOUS": "East of House",

# FIXED - now matches original .mud definition:  
"EHOUS": "Behind House",
```

### Fix Applied: ✅
Changed hardcoded name mapping to match original Zork definition

## Investigation Results

### Current Navigation Behavior (VERIFIED):

#### Starting from WHOUS (West of House):
```
WHOUS > e
"You can't go that way." ✅ CORRECT - Front door is locked
```

#### Alternative Path to Behind House:
```
WHOUS > s > e
WHOUS → SHOUS → EHOUS ✅ WORKS (South side → Behind House)

WHOUS > n > e  
WHOUS → NHOUS → EHOUS ✅ WORKS (North side → Behind House)
```

### Room Definitions Analysis:

**WHOUS (West of House):**
- EAST: `#NEXIT "The door is locked, and there is evidently no key."`
- NORTH: NHOUS
- SOUTH: SHOUS  
- WEST: FORE1

**NHOUS (North of House):**
- WEST: WHOUS
- EAST: EHOUS ← **CAN reach behind house**
- NORTH: FORE3

**SHOUS (South of House):**  
- WEST: WHOUS
- EAST: EHOUS ← **CAN reach behind house**
- SOUTH: FORE2

**EHOUS (Behind House):** ✅ **NOW DISPLAYS CORRECTLY**
- Shows as "Behind House" (was showing as "East of House")  
- NORTH: NHOUS
- SOUTH: SHOUS
- EAST: CLEAR
- WEST: Kitchen Window
- ENTER: Kitchen Window

## Analysis

### ✅ BEHAVIOR IS CORRECT:
1. **Direct east from WHOUS is properly blocked** (front door locked)
2. **Indirect access via sides is correct Zork behavior**
3. **Both NHOUS and SHOUS properly connect to EHOUS**
4. **✅ EHOUS now correctly displays as "Behind House"**

## Final Validation Test: ✅
```bash
echo -e "n\ne\nlook" | python3 main.py --mud
# Result: Shows "Behind House" ✅ CORRECT  
```

## Test Commands
```bash
# Test direct east (should be blocked)
echo "e" | python3 main.py --mud

# Test indirect access (should work)  
echo -e "s\ne\nlook" | python3 main.py --mud
echo -e "n\ne\nlook" | python3 main.py --mud
```

---
**✅ CONCLUSION:** 
- **Bug was real** - incorrect room name caused user confusion
- **Permanently fixed** - EHOUS now shows correct "Behind House" name  
- **Navigation works perfectly** - all paths function as intended in original Zork
- **User's concern was valid** - the misleading "East of House" name made it confusing