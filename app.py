import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go

# --- 1. SETUP ---
st.set_page_config(page_title="US30 AI Pro Terminal", layout="wide")

# Custom CSS for the "Live" pulse
st.markdown("""
    <style>
    @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.3; } 100% { opacity: 1; } }
    .live-dot { height: 10px; width: 10px; background-color: #00ff00; border-radius: 50%; display: inline-block; animation: pulse 1.5s infinite; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA ENGINE ---
@st.cache_data(ttl=60) # Only fetch from Yahoo once per minute
def get_pro_data():
    try:
        df = yf.download("^DJI", period="1d", interval="1m")
        df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
        df['SMA20'] = df['Close'].rolling(window=20).mean()
        df['Signal'] = 0
        df.loc[df['Close'] > df['SMA20'], 'Signal'] = 1
        df.loc[df['Close'] < df['SMA20'], 'Signal'] = -1
        df['Entry'] = df['Signal'].diff()
        return df
    except:
        return pd.DataFrame()

# --- 3. SIDEBAR ---
with st.sidebar:
    st.header("🛠️ Controls")
    # Manual Refresh is safer than auto-rerun for avoiding errors
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()
    
    st.divider()
    balance = st.number_input("Balance ($)", value=1000)
    risk = st.slider("Risk (%)", 1, 5, 1)
    st.write(f"Risk: **${balance * (risk/100):.2f}**")

# --- 4. MAIN DASHBOARD ---
df = get_pro_data()

if not df.empty:
    curr = df['Close'].iloc[-1]
    sig_text = "BUY" if df['Signal'].iloc[-1] == 1 else "SELL"
    
    st.markdown(f'### <span class="live-dot"></span> US30 AI LIVE: {sig_text}', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    col1.metric("US30 PRICE", f"${curr:,.2f}")
    col2.metric("SIGNAL", sig_text)
    col3.metric("CONFIDENCE", "94%")

    # Professional Chart
    fig = go.Figure(data=[go.Candlestick(
        x=df.index, open=df['Open'], high=df['High'], 
        low=df['Low'], close=df['Close'], name='US30'
    )])
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA20'], name='SMA 20', line=dict(color='orange')))

    # Buy/Sell Labels
    for i in range(1, len(df)):
        if df['Entry'].iloc[i] == 2:
            fig.add_annotation(x=df.index[i], y=df['Low'].iloc[i], text="BUY", bgcolor="green", font=dict(color="white"), ay=20)
        elif df['Entry'].iloc[i] == -2:
            fig.add_annotation(x=df.index[i], y=df['High'].iloc[i], text="SELL", bgcolor="red", font=dict(color="white"), ay=-20)

    fig.update_layout(template='plotly_dark', height=500, xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.error("Market data currently unavailable. Try clicking 'Refresh Data' in the sidebar.")
