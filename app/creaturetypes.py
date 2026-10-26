import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from reference_page import render_reference_page

render_reference_page(
    "Creature types",
    "Creature classifications and their descriptions.",
    """ SELECT CTKey AS Key, CTName AS Name, CTDescription AS Description
        FROM CreatureTypesStructured
        ORDER BY CTName
    """,
    )