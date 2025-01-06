import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Fetch API keys from environment variables
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

# Configure Streamlit
st.set_page_config(page_title="Finance Dashboard", layout="wide")

# Fetch stock data
def fetch_stock_data(symbol, interval="1min"):
    base_url = "https://www.alphavantage.co/query"
    params = {
        "function": "TIME_SERIES_INTRADAY",
        "symbol": symbol,
        "interval": interval,
        "apikey": ALPHA_VANTAGE_API_KEY,
    }
    response = requests.get(base_url, params=params)
    data = response.json()
    if f"Time Series ({interval})" in data:
        df = pd.DataFrame(data[f"Time Series ({interval})"]).T
        df.columns = [col.split(". ")[1] for col in df.columns]
        df.index = pd.to_datetime(df.index)
        return df
    else:
        st.error("Error fetching stock data. Check the API key or symbol.")
        return pd.DataFrame()

# Fetch news
def fetch_financial_news(query="finance"):
    base_url = "https://newsapi.org/v2/everything"
    params = {
        "q": query,
        "apiKey": NEWS_API_KEY,
        "language": "en",
        "sortBy": "publishedAt",
    }
    response = requests.get(base_url, params=params)
    data = response.json()
    if "articles" in data:
        return data["articles"]
    else:
        st.error("Error fetching news. Check the API key.")
        return []

# Sidebar inputs
st.sidebar.title("Finance Dashboard")
selected_symbol = st.sidebar.text_input("Enter Stock Symbol (e.g., AAPL, TSLA):", "AAPL")
st.sidebar.markdown("---")

# Main section
st.title("Interactive Finance Dashboard")

# Display stock data
stock_data = fetch_stock_data(selected_symbol)
if not stock_data.empty:
    st.subheader(f"Stock Data for {selected_symbol}")
    st.dataframe(stock_data.head())

    # Plot stock price chart
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=stock_data.index, y=stock_data["close"], mode="lines", name="Close Price"))
    fig.update_layout(
        title=f"Stock Price for {selected_symbol}",
        xaxis_title="Time",
        yaxis_title="Price (USD)",
        template="plotly_dark",
    )
    st.plotly_chart(fig, use_container_width=True)

# Display news
st.subheader("Latest Financial News")
news_articles = fetch_financial_news()
if news_articles:
    for article in news_articles[:5]:
        st.markdown(f"### {article['title']}")
        st.markdown(f"{article['description']}")
        st.markdown(f"[Read more]({article['url']})")
        st.markdown("---")
