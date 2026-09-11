import random
import re

@service(supports_response="optional")
def roll_dice(notation="1d20"):
    """yaml
    name: Roll Dice Notation
    description: Rolls a combination of dice (e.g., 2d12, d4+d20).
    fields:
        notation:
            description: Standard dice notation
            example: 2d12+1d4
            required: true
            selector:
                text:
    """
    if not notation:
        return {"error": "No notation provided"}

    # Clean input: remove spaces and make lowercase
    clean_notation = str(notation).lower().replace(" ", "")
    clean_notation = clean_notation.replace("plus", "+").replace("and", "+")
    clean_notation = clean_notation.replace("ad", "1d") # Converts "ad4" to "1d4"
    groups = clean_notation.split('+')
    
    valid_sides = [4, 6, 8, 10, 12, 20, 100]
    breakdown = []
    grand_total = 0

    for group in groups:
        # Match pattern for optional count + 'd' + sides (e.g., "d20" or "2d12")
        match = re.match(r'^(\d*)d(\d+)$', group)
        if not match:
            return {"error": f"Invalid format in '{group}'. Use standard notation like 2d6 or d20."}
            
        count_str = match.group(1)
        sides = int(match.group(2))
        count = int(count_str) if count_str else 1
        
        if sides not in valid_sides:
            return {"error": f"Invalid die: d{sides}. Must be one of: d4, d6, d8, d10, d12, d20, d100."}
            
        if count > 100:
            return {"error": "Maximum of 100 dice per group allowed."}

        # Generate rolls
        rolls = [random.randint(1, sides) for _ in range(count)]
        group_sum = sum(rolls)
        
        breakdown.append({
            "group": group,
            "die_type": f"d{sides}",
            "count": count,
            "individual_rolls": rolls,
            "group_total": group_sum
        })
        grand_total += group_sum

    return {
        "notation_rolled": clean_notation,
        "total": grand_total,
        "breakdown": breakdown
    }
