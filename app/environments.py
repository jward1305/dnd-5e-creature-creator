import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import duckdb
import pandas as pd
import streamlit as st

from database import query_database

def render_reference_page(
    page_name: str,
    page_description: str,
    page_query: str,
) -> None:
    st.title(page_name)
    st.caption(page_description)

    try:
        rows = query_database(page_query)
    except duckdb.Error as error:
        st.error(f"Could not load {page_name.lower()} data: {error}")
        st.stop()

    if not rows:
        st.info(f"No {page_name.lower()} data is available.")
        return

    for item in rows:
        st.subheader(item[1])
        st.write(item[2])
        data = pd.DataFrame({"Aquatic": item[3], "Planar": item[4], "Interior": item[5]}, index=[1])
        st.dataframe(data, hide_index=True, width="content")

render_reference_page(
    "Environments",
    "Places and planes where creatures may be encountered.",
    """ SELECT EKey AS Key, EName AS Name, EDescription AS Description, 
        isAquatic AS Aquatic, isPlanar AS Planar, isInterior AS Interior
        FROM EnvironmentsStructured
        ORDER BY EName
    """,
)