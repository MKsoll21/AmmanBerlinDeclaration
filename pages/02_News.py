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
# Disability Debrief
# ------------------------------------------------

def get_disability_debrief():

    url = "https://www.disabilitydebrief.org/"

    articles = []

    try:

        response = requests.get(
            url,
            timeout=10
        )

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        for link in soup.find_all("a"):

            title = link.get_text(strip=True)
            href = link.get("href")

            if (
                title
                and href
                and "/story/" in href
            ):

                if href.startswith("/"):
                    href = url.rstrip("/") + href

                articles.append(
                    {
                        "title": title,
                        "link": href,
                        "source": "Disability Debrief"
                    }
                )

    except Exception as e:

        st.warning(
            f"Disability Debrief could not be loaded: {e}"
        )


    return articles[:5]



# ------------------------------------------------
# RSS News
# ------------------------------------------------

NEWS_FEEDS = [

    {
        "name": "OECD",
        "url": "https://www.oecd.org/newsroom/rss.xml"
    },

    {
        "name": "ReliefWeb",
        "url": "https://reliefweb.int/rss.xml"
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
                item["source"]
            )

            st.markdown(
                f'[Read article]({item["link"]})'
            )

else:

    st.info(
        "No Disability Debrief articles found."
    )



# ------------------------------------------------
# Display other sources
# ------------------------------------------------

st.divider()

st.subheader(
    "🌍 Other News Sources"
)


news = load_news()


if news:

    for item in news:

        with st.container(border=True):

            st.subheader(
                item["title"]
            )

            st.caption(
                f'{item["source"]} | {item["date"]}'
            )

            st.markdown(
                f'[Read article]({item["link"]})'
            )

else:

    st.info(
        "No other news available."
    )
