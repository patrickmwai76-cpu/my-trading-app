import streamlit as st
import yfinance as yf

# 1. Setup the Page
st.title("US30 AI Live Feed")

# 2. Get the Data
df = yf.download("^DJI", period="1d", interval="15m")

# 3. Check if we have data and show it
if not df.empty:
    price = df['Close'].iloc[-1].item()
    st.metric("US30 Current Price", f"${price:,.2f}")
    st.line_chart(df['Close'])
    
    # AI Signal Logic
    if price > df['Close'].mean().item():
        st.success("AI SIGNAL: BUY")
    else:
        st.error("AI SIGNAL: SELL")
else:
    st.write("Market is closed or data is loading...")
