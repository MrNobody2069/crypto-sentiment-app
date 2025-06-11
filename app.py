import streamlit as st
import snscrape.modules.twitter as sntwitter
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import matplotlib.pyplot as plt

st.set_page_config(page_title="Crypto Sentiment Analyzer", layout="centered")
st.title("📊 Crypto Sentiment Analyzer")
st.markdown("Enter a keyword (like `Bitcoin`, `ETH`, `Solana`) to see recent Twitter sentiment.")

query = st.text_input("Search Term", value="Bitcoin")
tweet_count = st.slider("Number of Tweets", 10, 100, 50)

if st.button("Analyze Sentiment") and query:
    analyzer = SentimentIntensityAnalyzer()
    tweets_data = []

    for i, tweet in enumerate(sntwitter.TwitterSearchScraper(query + ' lang:en').get_items()):
        if i >= tweet_count:
            break
        score = analyzer.polarity_scores(tweet.content)['compound']
        sentiment = 'Positive' if score > 0.2 else 'Negative' if score < -0.2 else 'Neutral'
        tweets_data.append([tweet.date, tweet.user.username, tweet.content, sentiment])

    df = pd.DataFrame(tweets_data, columns=["Date", "User", "Tweet", "Sentiment"])
    st.write("### Sentiment Breakdown")
    st.dataframe(df)

    sentiment_counts = df['Sentiment'].value_counts()
    fig, ax = plt.subplots()
    sentiment_counts.plot.pie(autopct='%1.1f%%', ax=ax)
    ax.set_ylabel('')
    st.pyplot(fig)
