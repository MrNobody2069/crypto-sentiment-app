import streamlit as st
import requests
from textblob import TextBlob

st.set_page_config(page_title="Crypto Sentiment App", layout="centered")

st.title("🧠 Crypto Sentiment Analyzer")
st.write("Analyze real-time news sentiment for any cryptocurrency.")

# --- Input ---
coin = st.text_input("🔍 Enter a crypto keyword (e.g. Bitcoin, Ethereum):")

# --- Fetch News ---
def fetch_news(coin_name):
    api_key = "e8fe6d02a2884a3a9f7a89f2a12483ab"  # Replace this with your actual API key
    url = (
        f"https://newsapi.org/v2/everything?q={coin_name}&language=en&sortBy=publishedAt&pageSize=5&apiKey={api_key}"
    )
    response = requests.get(url)
    data = response.json()
    return data["articles"]

# --- Sentiment Analysis ---
def get_sentiment(text):
    blob = TextBlob(text)
    return blob.sentiment.polarity  # -1 (negative) to 1 (positive)

# --- Display Results ---
if coin:
    try:
        articles = fetch_news(coin)
        for article in articles:
            st.markdown(f"### {article['title']}")
            description = article["description"] or ""
            score = get_sentiment(description)
            sentiment = (
                "🟢 Positive" if score > 0 else "🔴 Negative" if score < 0 else "🟡 Neutral"
            )
            st.write("**Sentiment:**", sentiment)
            st.caption(article["publishedAt"])
            st.write("---")
    except Exception as e:
        st.error("Something went wrong. Please check your API key or connection.")
