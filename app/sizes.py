import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from reference_page import render_reference_page


render_reference_page(
    "Sizes", 
    "Creature size categories, space diameters, and suggested hit dice.",
    """ SELECT SKey AS Key, SName AS Name, SRank AS Rank, Diamter AS Diameter, SuggestedHitDice 
        FROM SizesStructured 
        ORDER BY SRank
    """,
    ["Key", "Name", "Rank", "Diameter", "SuggestedHitDice"]
    )