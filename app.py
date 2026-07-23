import streamlit as st


dashboard = st.Page(
    "Dashboard.py",
    title="Dashboard",
    icon="📊"
)


explorer = st.Page(
    "pages/01_Data_Explorer.py",
    title="Data Explorer",
    icon="🔎"
)


pg = st.navigation(
    {
        "": [
            dashboard,
            explorer
        ]
    }
)


pg.run()

