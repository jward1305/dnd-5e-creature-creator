import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from reference_page import render_reference_page

render_reference_page(
    "Damage types",
    "Damage categories and their descriptions.",
    """ SELECT DTKey AS Key, DTName AS Name, DTDescription AS Description
        FROM DamageTypesStructured
        ORDER BY DTName
    """,
    ["Key", "Name", "Description"]
)