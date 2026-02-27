import streamlit as st
import yfinance as yf
import plotly.graph_objects as go

# 1. Setup the Page
st.set_page_config(page_title="US30 AI Analyst", layout="wide")
st.title("🤖 US30 AI Trading Assistant")

# 2. Get the Data (US30 is ^DJI)
df = yf.download("^DJI", period="2d", interval="15m")

# 3. Process Data and Show Metrics
if not df.empty:
    # Use .item() to turn lists into single numbers for the AI to read
    current_price = df['Close'].iloc[-1].item()
    avg_price = df['Close'].mean().item()
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("US30 Live Price", f"${current_price:,.2f}")
    with col2:
        if current_price > avg_price:
            st.success("AI SIGNAL: 🟢 BUY")
        else:
            st.error("AI SIGNAL: 🔴 SELL")

    # 4. Professional Candlestick Chart
    st.subheader("US30 15-Minute Candlesticks")
    fig = go.Figure(data=[go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name="Market Price"
    )])
    
    # Add a Moving Average line (The AI's guideline)
    df['MA'] = df['Close'].rolling(window=5).mean()
    fig.add_trace(go.Scatter(x=df.index, y=df['MA'], line=dict(color='orange', width=2), name='Avg Price'))

    fig.update_layout(xaxis_rangeslider_visible=False, height=500)
    st.plotly_chart(fig, use_container_width=True)

else:
    st.warning("Fetching market data... If the market is closed, some data may be delayed.")
