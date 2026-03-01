import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# 1. Setup
st.set_page_config(page_title="PATRO AI PRO | Terminal", layout="wide")
st_autorefresh(interval=30000, key="patroupdate")

# Sidebar Tools
st.sidebar.title("🛡️ OPERATOR SOP")
s1, s2, s3 = st.sidebar.checkbox("Trend Matrix?"), st.sidebar.checkbox("VWAP?"), st.sidebar.checkbox("News Clear?")

st.sidebar.divider()
st.sidebar.subheader("📉 RISK CALCULATOR")
bal = st.sidebar.number_input("Balance ($)", value=1000)
risk = st.sidebar.slider("Risk (%)", 1.0, 5.0, 1.0)
sl = st.sidebar.number_input("SL Points", value=50)
st.sidebar.info(f"Lot Size: {(bal * (risk/100)) / sl:.2f}")

# 2. Main Dashboard
st.markdown('<h1 style="text-align:center; color:#00ffcc;">🛡️ PATRO AI PRO | INSTITUTIONAL</h1>', unsafe_allow_html=True)

# Fetching Data (Fixing the Multi-Index Error)
df = yf.download("^DJI", period="1d", interval="1m", group_by='column')

if not df.empty:
    # Get values safely
    df.columns = df.columns.get_level_values(0) if isinstance(df.columns, pd.MultiIndex) else df.columns
    price = df['Close'].iloc[-1]
    avg_p = df['Close'].mean()
    
    # 3. Create the Candlestick Chart
    fig = go.Figure()

    # Add Candles
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['Open'], high=df['High'],
        low=df['Low'], close=df['Close'],
        name='US30'
    ))

    # Add AI Baseline
    fig.add_trace(go.Scatter(x=df.index, y=[avg_p]*len(df), name='AI Level', line=dict(color='orange', dash='dash')))

    # 4. Add Buy/Sell Markers (The "B" and "S")
    # Buy Marker (Green Arrow)
    if price > avg_p:
        fig.add_annotation(x=df.index[-1], y=df['Low'].iloc[-1], text="B", showarrow=True, arrowhead=2, arrowcolor="#00ff00", bgcolor="#00ff00", font=dict(color="black"))
        st.success("🚀 AI SIGNAL: BUY MODE")
    else:
        # Sell Marker (Red Arrow)
        fig.add_annotation(x=df.index[-1], y=df['High'].iloc[-1], text="S", showarrow=True, arrowhead=2, arrowcolor="#ff0000", bgcolor="#ff0000", font=dict(color="white"))
        st.error("📉 AI SIGNAL: SELL MODE")

    fig.update_layout(template="plotly_dark", height=600, xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)
    
    st.metric("Live US30", f"${price:,.2f}", delta=f"{price-avg_p:,.2f}")
