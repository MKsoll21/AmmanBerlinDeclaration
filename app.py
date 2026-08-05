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

news = st.Page(
    "pages/02_News.py",
    title="News",
    icon="📰"
)

pg = st.navigation(
    {
        "": [
            dashboard,
            explorer,
            news
        ]
    }
)

pg.run()
