import streamlit as st
import requests
from textblob import TextBlob
import pandas as pd
import altair as alt

st.set_page_config(page_title="Crypto Sentiment App", layout="centered")

st.title("🧠 Crypto Sentiment Analyzer")
st.write("Analyze real-time news sentiment for any cryptocurrency.")

# --- Input ---
coin = st.text_input("🔍 Enter a crypto keyword (e.g. Bitcoin, Ethereum):")

# --- Fetch News ---
def fetch_news(coin_name):
    api_key = "e8fe6d02a2884a3a9f7a89f2a12483ab"  # Replace with your actual API key
    url = (
        f"https://newsapi.org/v2/everything?q={coin_name}&language=en&sortBy=publishedAt&pageSize=10&apiKey={api_key}"
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
        sentiments = []

        st.subheader("📰 News & Sentiment Scores")
        for article in articles:
            title = article['title']
            description = article['description'] or ""
            score = get_sentiment(description)
            sentiment_label = (
                "🟢 Positive" if score > 0.2 else "🔴 Negative" if score < -0.2 else "🟡 Neutral"
            )
            
            sentiments.append({"title": title, "score": score, "sentiment": sentiment_label})

            st.markdown(f"### {title}")
            st.write("**Sentiment:**", sentiment_label)
            st.write("**Score:**", f"{score:.2f}")
            st.caption(article["publishedAt"])
            st.write("---")

        # --- Summary ---
        df = pd.DataFrame(sentiments)
        total = len(df)
        pos = len(df[df['score'] > 0.2])
        neg = len(df[df['score'] < -0.2])
        neu = total - pos - neg

        st.subheader("📊 Sentiment Summary")
        chart_data = pd.DataFrame({
            "Sentiment": ["Positive", "Negative", "Neutral"],
            "Articles": [pos, neg, neu]
        })

        chart = alt.Chart(chart_data).mark_bar().encode(
            x=alt.X('Sentiment', sort=['Positive', 'Neutral', 'Negative']),
            y='Articles',
            color='Sentiment'
        )
        st.altair_chart(chart, use_container_width=True)

        # --- Recommendation ---
        st.subheader("📌 Trading Insight")
        if pos > neg and pos > neu:
            st.success("Sentiment is strongly positive — You may consider buying if technicals also align.")
        elif neg > pos and neg > neu:
            st.error("Sentiment is strongly negative — Consider waiting or looking for short opportunities.")
        else:
            st.info("Sentiment is mixed or neutral — Use caution and confirm with charts.")

    except Exception as e:
        st.error("Something went wrong. Please check your API key or connection.")
