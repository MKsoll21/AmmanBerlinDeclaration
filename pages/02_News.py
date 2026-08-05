import streamlit as st
import feedparser


st.set_page_config(
    page_title="News",
    page_icon="📰",
    layout="wide"
)


st.title("📰 Latest News")


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
        "name": "OECD Development",
        "category": "🌍 Development Cooperation",
        "url": "https://www.oecd.org/development/rss.xml"
    },

    {
        "name": "World Bank",
        "category": "🌍 Development Cooperation",
        "url": "https://www.worldbank.org/en/news/all?format=rss"
    },


    # 🚨 Humanitarian

    {
        "name": "ReliefWeb",
        "category": "🚨 Humanitarian & Middle East",
        "url": "https://reliefweb.int/rss.xml"
    },

    {
        "name": "UN OCHA",
        "category": "🚨 Humanitarian & Middle East",
        "url": "https://www.unocha.org/rss.xml"
    }

]

# ------------------------------------------------
# Load News
# ------------------------------------------------

@st.cache_data(ttl=3600)
def load_news():

    articles = []

    for source in NEWS_FEEDS:

        feed = feedparser.parse(
            source["url"]
        )
    if not feed.entries:
    continue
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

    return articles



# ------------------------------------------------
# Display
# ------------------------------------------------

news = load_news()


categories = [

    "♿ Disability Inclusion",

    "🌍 Development Cooperation",

    "🚨 Humanitarian & Middle East"

]


for category in categories:

    st.subheader(
        category
    )


    category_news = [

        item
        for item in news
        if item["category"] == category

    ]


    if category_news:

        for item in category_news:

            with st.container(border=True):

                st.markdown(
                    f"### {item['title']}"
                )

                st.caption(
                    f"{item['source']} | {item['date']}"
                )

                st.markdown(
                    f"[🔗 Read article]({item['link']})"
                )

    else:

        st.info(
            "No news available."
        )
