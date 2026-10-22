import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from reference_page import render_reference_page

render_reference_page(
    "Conditions",
    "Conditions that can affect a creature and their rules descriptions.",
    """ SELECT CKey AS Key, CName AS Name, CDescription AS Description
        FROM ConditionsStructured
        ORDER BY CName
    """,
    ["Key", "Name", "Description"]
)