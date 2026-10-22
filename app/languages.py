import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from reference_page import render_reference_page

render_reference_page(
    "Languages",
    "Languages spoken or understood by creatures.",
    """ SELECT LKey AS Key, LName AS Name, LDescription AS Description, LScript AS Script,
        isExotic AS Exotic, isSecret AS Secret
        FROM LanguagesStructured
        ORDER BY LName
    """,
    ["Key", "Name", "Description", "Script", "Exotic", "Secret"]
    )