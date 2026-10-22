import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from reference_page import render_reference_page

render_reference_page(
    "Environments",
    "Places and planes where creatures may be encountered.",
    """ SELECT EKey AS Key, EName AS Name, EDescription AS Description, 
        isAquatic AS Aquatic, isPlanar AS Planar, isInterior AS Interior
        FROM EnvironmentsStructured
        ORDER BY EName
    """,
    ["Key", "Name", "Description", "Aquatic", "Planar", "Interior"]
)