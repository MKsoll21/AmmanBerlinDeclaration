import streamlit as st
import feedparser
import requests
from bs4 import BeautifulSoup


st.set_page_config(
    page_title="News",
    page_icon="📰",
    layout="wide"
)


st.title("📰 Latest News")


# ------------------------------------------------
# Disability Debrief RSS
# ------------------------------------------------

def get_disability_debrief():

    url = "https://www.disabilitydebrief.org/rss/"

    articles = []

    try:

        feed = feedparser.parse(url)


        for entry in feed.entries[:3]:

articles.append(
    {
        "title": entry.get(
            "title",
            "No title"
        ),

        "link": entry.get(
            "link",
            "#"
        ),

        "source": source["name"],

        "category": source["category"],

        "date": entry.get(
            "published",
            ""
        )
    }
)

    except Exception as e:

        st.error(
            f"Disability Debrief error: {e}"
        )


    return articles


# ------------------------------------------------
# RSS News
# ------------------------------------------------

# ------------------------------------------------
# News Sources
# ------------------------------------------------

NEWS_FEEDS = [

    # ♿ Disability Inclusion

    {
        "name": "Disability Debrief",
        "category": "♿ Disability Inclusion",
        "url": "https://www.disabilitydebrief.org/rss/"
    },

    {
        "name": "UN Disability",
        "category": "♿ Disability Inclusion",
        "url": "https://news.un.org/feed/subscribe/en/news/topic/disability/feed/rss.xml"
    },


    # 🌍 Development Cooperation

    {
        "name": "OECD",
        "category": "🌍 Development Cooperation",
        "url": "https://www.oecd.org/newsroom/rss.xml"
    },

    {
        "name": "UNDP",
        "category": "🌍 Development Cooperation",
        "url": "https://www.undp.org/rss.xml"
    },


    # 🚨 Humanitarian

    {
        "name": "ReliefWeb",
        "category": "🚨 Humanitarian & Middle East",
        "url": "https://reliefweb.int/updates/rss.xml"
    }

]


@st.cache_data(ttl=3600)
def load_news():

    articles = []


    for source in NEWS_FEEDS:

        feed = feedparser.parse(
            source["url"]
        )


        for entry in feed.entries[:5]:

            articles.append(
                {
                    "title": entry.title,
                    "link": entry.link,
                    "source": source["name"],
                    "date": entry.get(
                        "published",
                        ""
                    )
                }
            )


    return articles



# ------------------------------------------------
# Display Disability Debrief
# ------------------------------------------------

st.subheader(
    "♿ Disability Debrief"
)


debrief_news = get_disability_debrief()


if debrief_news:

    for item in debrief_news:

        with st.container(border=True):

            st.subheader(
                item["title"]
            )

            st.caption(
                f'{item["source"]} | {item["date"]}'
            )

            st.markdown(
                f'[🔗 Read article]({item["link"]})'
            )

else:

    st.info(
        "No Disability Debrief articles found."
    )
# ------------------------------------------------
# Display other sources by category
# ------------------------------------------------

st.divider()

st.subheader(
    "🌍 Development & Humanitarian Monitoring"
)


news = load_news()


categories = [

    "♿ Disability Inclusion",

    "🌍 Development Cooperation",

    "🚨 Humanitarian & Middle East"

]


for category in categories:

    st.markdown(
        f"### {category}"
    )


    category_news = [
        item
        for item in news
        if item["category"] == category
    ]


    if category_news:

        for item in category_news:

            with st.container(border=True):

                st.subheader(
                    item["title"]
                )

                st.caption(
                    f'{item["source"]} | {item["date"]}'
                )

                st.markdown(
                    f'[🔗 Read article]({item["link"]})'
                )


    else:

        st.info(
            "No news available."
        )
