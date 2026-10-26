import duckdb
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