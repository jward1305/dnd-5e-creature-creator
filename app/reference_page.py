from typing import Sequence

import duckdb
import pandas as pd
import streamlit as st

from database import query_database


def render_reference_page(
    page_name: str,
    page_description: str,
    page_query: str,
    page_columns: Sequence[str],
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

    data = pd.DataFrame(rows, columns=page_columns)
    config = (
        {"Description": st.column_config.TextColumn(width="large")}
        if "Description" in data.columns
        else {}
    )
    st.dataframe(
        data,
        column_config=config,
        hide_index=True,
        height="content",
        width="stretch",
    )
