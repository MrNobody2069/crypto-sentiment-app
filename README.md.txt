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
        f"https://newsapi.org/v2/everything?q={coin_name}&language=en&sortBy=publishedAt&pageSize=5&apiKey={api_key}"
    )
    response = requests.get(url)
    data = response.json()
    return data["articles"]

# --- Sentiment Analysis ---
def get_sentiment(text):
    blob = TextBlob(text)
    return blob.sentiment.polarity  # -1 (negative) to 1 (positive)

def classify_sentiment(score):
    if score > 0.3:
        return "🟢 Strong Positive"
    elif score > 0.05:
        return "🟡 Mild Positive"
    elif score < -0.3:
        return "🔴 Strong Negative"
    elif score < -0.05:
        return "🔴 Mild Negative"
    else:
        return "⚪️ Neutral"

# --- Display Results ---
if coin:
    try:
        articles = fetch_news(coin)
        sentiment_data = []

        for article in articles:
            title = article['title']
            description = article["description"] or ""
            score = get_sentiment(description)
            sentiment_label = classify_sentiment(score)

            st.markdown(f"### {title}")
            st.write("**Sentiment Score:**", f"{score:.2f}")
            st.write("**Sentiment:**", sentiment_label)
            st.caption(article["publishedAt"])
            st.write("---")

            sentiment_data.append({"Title": title[:60] + ("..." if len(title) > 60 else ""), "Score": score})

        # Show Bar Chart
        df = pd.DataFrame(sentiment_data)
        st.subheader("📊 Sentiment Score Comparison")
        chart = alt.Chart(df).mark_bar().encode(
            x=alt.X('Score:Q', scale=alt.Scale(domain=[-1, 1])),
            y=alt.Y('Title:N', sort='-x'),
            color=alt.condition(
                alt.datum.Score > 0, alt.value("green"), alt.value("red")
            )
        ).properties(height=300)
        st.altair_chart(chart, use_container_width=True)

    except Exception as e:
        st.error("Something went wrong. Please check your API key or connection.")
