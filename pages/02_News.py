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
# Disability Debrief Funktion HIER EINFÜGEN
# ------------------------------------------------

def get_disability_debrief():

    url = "https://www.disabilitydebrief.org/"

    response = requests.get(
        url,
        timeout=10
    )

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    articles = []

    for article in soup.find_all("article")[:5]:

        title = article.find("h2")
        link = article.find("a")

        if title and link:

            articles.append({

                "title": title.text.strip(),
                "link": link.get("href"),
                "source": "Disability Debrief"

            })

    return articles



# ------------------------------------------------
# RSS News Funktion (dein bestehender Code)
# ------------------------------------------------

@st.cache_data(ttl=3600)
def load_news():

    ...
    

# ------------------------------------------------
# Anzeige
# ------------------------------------------------

st.subheader("♿ Disability Debrief")

debrief_news = get_disability_debrief()


for item in debrief_news:

    with st.container(border=True):

        st.write(item["title"])

        st.caption(
            item["source"]
        )

        st.markdown(
            f"[Read article]({item['link']})"
        )


st.divider()


st.subheader("🌍 Other News Sources")

news = load_news()

if news:

    for item in news:

        with st.container(border=True):

            st.subheader(
                item["title"]
            )

            st.caption(
                f'{item["source"]} | {item.get("date","")}'
            )

            st.markdown(
                f'[Read article]({item["link"]})'
            )

else:

    st.info(
        "No news available at the moment."
    )
