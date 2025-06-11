import streamlit as st
import requests
from textblob import TextBlob
import pandas as pd
import altair as alt
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

st.set_page_config(page_title="🚀 Crypto Sentiment Dashboard", layout="centered")

st.title("🧠 Crypto Sentiment Analyzer + Price & Trends")
st.write("Analyze real-time news sentiment, view price, and detect trading signals for any cryptocurrency.")

# --- Input ---
coin = st.text_input("🔍 Enter a crypto keyword (e.g. Bitcoin, Ethereum):")

# --- Google Sheets Auth ---
def connect_to_sheet():
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name("gspread_creds.json", scope)
        client = gspread.authorize(creds)
        sheet = client.open("CryptoSentimentLog").sheet1
        return sheet
    except:
        return None

# --- Fetch News ---
def fetch_news(coin_name):
    api_key = "e8fe6d02a2884a3a9f7a89f2a12483ab"  # Replace with your NewsAPI key
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

# --- Fetch Price from CoinGecko ---
def fetch_price(coin_name):
    try:
        coin_name_lower = coin_name.lower().replace(" ", "-")
        price_url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_name_lower}&vs_currencies=usd"
        r = requests.get(price_url)
        return r.json()[coin_name_lower]["usd"]
    except:
        return "N/A"

# --- Display Section ---
if coin:
    try:
        st.subheader("📈 Current Price")
        price = fetch_price(coin)
        st.write(f"💰 1 {coin.title()} = ${price}")

        st.subheader("📰 News & Sentiment Scores")
        articles = fetch_news(coin)
        sentiments = []

        sheet = connect_to_sheet()

        for article in articles:
            title = article['title']
            description = article['description'] or ""
            score = get_sentiment(description)
            sentiment_label = (
                "🟢 Positive" if score > 0.2 else "🔴 Negative" if score < -0.2 else "🟡 Neutral"
            )
            date_str = article["publishedAt"][:10]

            sentiments.append({
                "title": title,
                "score": score,
                "sentiment": sentiment_label,
                "date": date_str
            })

            st.markdown(f"### {title}")
            st.write("**Sentiment:**", sentiment_label)
            st.write("**Score:**", f"{score:.2f}")
            st.caption(f"🗓 {date_str}")
            st.write("---")

            # Log to Google Sheets if connected
            if sheet:
                sheet.append_row([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), coin, title, score, sentiment_label])

        # --- Summary ---
        df = pd.DataFrame(sentiments)
        pos = len(df[df['score'] > 0.2])
        neg = len(df[df['score'] < -0.2])
        neu = len(df) - pos - neg

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

        # --- Sentiment Over Time ---
        st.subheader("📅 Sentiment Over Time")
        trend_chart = alt.Chart(df).mark_line(point=True).encode(
            x='date:T',
            y='score:Q',
            tooltip=['title', 'score']
        ).properties(width=700)
        st.altair_chart(trend_chart, use_container_width=True)

        # --- Recommendation ---
        st.subheader("📌 Trading Insight")
        if pos > neg and pos > neu:
            st.success("Sentiment is strongly positive — Consider buying if price action confirms.")
        elif neg > pos and neg > neu:
            st.error("Sentiment is strongly negative — Avoid buying or consider shorting.")
        else:
            st.info("Sentiment is mixed — Wait for clearer market signals.")

    except Exception as e:
        st.error("Something went wrong. Please check your API key, crypto name, or internet connection.")
