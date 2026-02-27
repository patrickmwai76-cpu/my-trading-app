import streamlit as st
import yfinance as yf
import mplfinance as mpf
import pandas as pd

# 1. Dashboard Logic
def run_ai_dashboard():
    st.set_page_config(page_title="US30 AI Analyst", layout="wide")
    st.title("🤖 US30 AI Trading Assistant")
    
    # Sidebar
    st.sidebar.header("Settings")
    symbol = st.sidebar.text_input("Ticker", "^DJI")
    timeframe = st.sidebar.selectbox("Interval", ["5m", "15m", "1h", "1d"])
    
    # Load Data
    data = yf.download(symbol, period='2d', interval=timeframe)
    
    if not data.empty:
        # Get the very last price as a single number
        last_price = data['Close'].iloc[-1].item()
        st.metric(f"Current {symbol} Price", f"${last_price:,.2f}")
        
        # Simple AI Signal
        avg_price = data['Close'].mean().item()
        if last_price > avg_price:
            st.success("AI SIGNAL: BUY")
        else:
            st.error("AI SIGNAL: SELL")
            
        # Chart
        st.subheader("Market Chart")
        fig, ax = mpf.plot(data, type='candle', style='charles', returnfig=True)
        st.pyplot(fig)
    else:
        st.warning("Waiting for market data... check your internet or ticker symbol.")

# 2. THE START COMMAND (Must be at the very far left!)
if __name__ == "__main__":
    run_ai_dashboard()
