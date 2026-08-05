import streamlit as st
import feedparser


st.set_page_config(
    page_title="News",
    layout="wide"
)


st.title("📰 Latest News")

st.caption(
    "Latest updates related to disability inclusion, development cooperation and humanitarian action."
)


NEWS_FEEDS = [

    {
        "name": "OECD",
        "url": "https://www.oecd.org/newsroom/rss.xml"
    },

    {
        "name": "UN News",
        "url": "https://news.un.org/feed/subscribe/en/news/topic/disability/feed/rss.xml"
    }

]


@st.cache_data(ttl=3600)
def load_news():

    articles = []


    for source in NEWS_FEEDS:

        feed = feedparser.parse(
            source["url"]
        )


        for entry in feed.entries:

            articles.append({

                "title": entry.title,

                "link": entry.link,

                "source": source["name"],

                "date": entry.get(
                    "published",
                    ""
                )

            })


    return articles[:20]



news = load_news()



for item in news:

    with st.container(border=True):

        st.subheader(
            item["title"]
        )

        st.caption(
            f'{item["source"]} | {item["date"]}'
        )

        st.markdown(
            f"[Read article]({item['link']})"
        )
