import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd

# 1. Setup the Page
st.set_page_config(page_title="US30 AI Pro Dashboard", layout="wide")
st.title("🤖 US30 AI Pro Dashboard")

# 2. Sidebar - Risk Calculator
st.sidebar.header("🧮 Risk Calculator")
balance = st.sidebar.number_input("Account Balance ($)", value=1000)
risk_percent = st.sidebar.slider("Risk Per Trade (%)", 1, 5, 1)
stop_loss_pips = st.sidebar.number_input("Stop Loss (Points)", value=50)

# Calculate Lot Size (Simplified for US30)
risk_amount = balance * (risk_percent / 100)
if stop_loss_pips > 0:
    recommended_lot = risk_amount / stop_loss_pips
    st.sidebar.success(f"Risk Amount: ${risk_amount:.2f}")
    st.sidebar.warning(f"Suggested Lot: {recommended_lot:.2f}")

# 3. Get the Data
df = yf.download("^DJI", period="2d", interval="15m")

if not df.empty:
    # 4. Indicators (AI Brain)
    price = df['Close'].iloc[-1].item()
    avg_price = df['Close'].mean().item()
    resistance = df['High'].max().item()
    support = df['Low'].min().item()

    # 5. Top Metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Current Price", f"${price:,.2f}")
    col2.metric("Daily High (Res)", f"${resistance:,.2f}")
    col3.metric("Daily Low (Sup)", f"${support:,.2f}")

    # 6. AI Signal Box
    if price > avg_price:
        st.success(f"🚀 AI SIGNAL: BUY (Price is above ${avg_price:,.2f})")
    else:
        st.error(f"📉 AI SIGNAL: SELL (Price is below ${avg_price:,.2f})")

    # 7. Professional Interactive Chart
    fig = go.Figure()
    # Market Price
    fig.add_trace(go.Scatter(x=df.index, y=df['Close'], name="Market Price", line=dict(color='orange', width=2)))
    # Support & Resistance Lines
    fig.add_hline(y=resistance, line_dash="dash", line_color="red", annotation_text="Resistance")
    fig.add_hline(y=support, line_dash="dash", line_color="green", annotation_text="Support")
    
    fig.update_layout(title="US30 Price Action & AI Levels", template="plotly_dark", height=500)
    st.plotly_chart(fig, use_container_width=True)

else:
    st.write("Market data currently unavailable. Check back in a moment!")
