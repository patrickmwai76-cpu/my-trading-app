import streamlit as st
import yfinance as yf
import mplfinance as mpf

st.set_page_config(page_title="US30 AI Pro", layout="wide")
st.title("🤖 US30 AI Pro Dashboard")

# --- 1. RISK CALCULATOR (Sidebar) ---
st.sidebar.header("Risk Calculator")
balance = st.sidebar.number_input("Account Balance ($)", value=1000.0)
risk_percent = st.sidebar.slider("Risk Per Trade (%)", 0.5, 5.0, 1.0)
stop_loss_pips = st.sidebar.number_input("Stop Loss (Points/Pips)", value=50)

# Calculate Lot Size (Simplified for US30)
risk_amount = balance * (risk_percent / 100)
suggested_lot = risk_amount / (stop_loss_pips * 10) # Adjust based on your broker's US30 contract
st.sidebar.success(f"Risk Amount: ${risk_amount:.2f}")
st.sidebar.info(f"Suggested Lot: {max(0.01, suggested_lot):.2f}")

# --- 2. MARKET DATA & CHART ---
df = yf.download("^DJI", period="2d", interval="15m")

if not df.empty:
    price = df['Close'].iloc[-1].item()
    avg_price = df['Close'].rolling(window=20).mean().iloc[-1] # 20-period Moving Average
    
    col1, col2 = st.columns(2)
    col1.metric("Current US30", f"${price:,.2f}")
    
    # AI Signal Logic
    if price > avg_price:
        col2.success("AI SIGNAL: BUY (Trending Up)")
    else:
        col2.error("AI SIGNAL: SELL (Trending Down)")

    # Professional Candlestick Chart
    st.subheader("15-Minute Candlestick Chart (with 20-MA)")
    fig, ax = mpf.plot(df, type='candle', style='charles', 
                       mav=(20), # Adds the Moving Average line
                       returnfig=True, figsize=(12, 6))
    st.pyplot(fig)
else:
    st.warning("Fetching market data...")
