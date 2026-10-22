from pathlib import Path
import sys

import streamlit as st


sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import DUCKDB_DIR

st.set_page_config(page_title="DnD Creature Creator", layout="wide")

if not DUCKDB_DIR.is_file():
    st.error(f"Database not found at `{DUCKDB_DIR}`. Build the database before starting the app.")
    st.stop()

search_page = [
    st.Page("search.py", title="Search", url_path="search", default=True),
    st.Page("createcreature.py", title="Create Custom Creature", url_path="custom-creature")
    ]

reference_pages = [
    st.Page("conditions.py", title="Conditions", url_path="conditions"),
    st.Page("creaturetypes.py", title="Creature Types", url_path="creaturetypes"),
    st.Page("damagetypes.py", title="Damage Types", url_path="damagetypes"),
    st.Page("environments.py", title="Environments", url_path="environments"),
    st.Page("languages.py", title="Languages", url_path="languages"),
    st.Page("sizes.py", title="Sizes", url_path="sizes"),
]

navigation = st.navigation(
    {
        "Creatures": search_page,
        "Reference": reference_pages,
    },
    position="top",
)
navigation.run()