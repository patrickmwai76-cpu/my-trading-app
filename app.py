import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- 1. SETUP ---
st.set_page_config(page_title="US30 AI Pro Terminal", layout="wide")

st.markdown("""
    <style>
    @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.3; } 100% { opacity: 1; } }
    .live-dot { height: 12px; width: 12px; background-color: #00ff00; border-radius: 50%; display: inline-block; animation: pulse 1.5s infinite; margin-right: 10px; }
    .stMetric { background-color: #1e2130; padding: 15px; border-radius: 10px; border-left: 5px solid #00ff00; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SIDEBAR (Risk Calculator & Controls) ---
with st.sidebar:
    st.header("🛠️ Trading Tools")
    if st.button("🔄 REFRESH DATA"):
        st.cache_data.clear()
        st.rerun()
    
    st.divider()
    st.subheader("Risk Calculator")
    balance = st.number_input("Account Balance ($)", value=1000, step=100)
    risk_pct = st.slider("Risk Per Trade (%)", 0.5, 5.0, 1.0, 0.5)
    risk_amt = balance * (risk_pct / 100)
    st.info(f"Recommended Risk: **${risk_amt:.2f}**")
    
    st.divider()
    st.write("AI Model: **v3.0 Scalper**")

# --- 3. DATA ENGINE ---
@st.cache_data(ttl=60)
def get_live_market_data():
    # Fetch US30 (Dow Jones) 1-minute intervals
    df = yf.download("^DJI", period="1d", interval="1m")
    df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
    
    # Technicals: SMA 20
    df['SMA20'] = df['Close'].rolling(window=20).mean()
    
    # Technicals: RSI 14
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # Signal Logic (Price vs SMA)
    df['Signal'] = 0
    df.loc[df['Close'] > df['SMA20'], 'Signal'] = 1
    df.loc[df['Close'] < df['SMA20'], 'Signal'] = -1
    df['Entry'] = df['Signal'].diff()
    return df

# --- 4. MAIN DASHBOARD ---
try:
    df = get_live_market_data()
    curr_p = df['Close'].iloc[-1]
    curr_rsi = df['RSI'].iloc[-1]
    last_sig = "BUY" if df['Signal'].iloc[-1] == 1 else "SELL"

    st.markdown(f'## <span class="live-dot"></span> US30 AI LIVE TERMINAL: {last_sig}', unsafe_allow_html=True)

    # Top Row Metrics
    m1, m2, m3 = st.columns(3)
    m1.metric("US30 PRICE", f"${curr_p:,.2f}")
    m2.metric("CURRENT SIGNAL", last_sig)
    m3.metric("RSI (14) SCALE", f"{curr_rsi:.2f}")

    # --- 5. THE DUAL-SCALE CHART ---
    # Top for Candles, Bottom for RSI
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                        vertical_spacing=0.03, row_heights=[0.7, 0.3])

    # Price Chart (Row 1)
    fig.add_trace(go.Candlestick(
        x=df.index, open=df['Open'], high=df['High'], 
        low=df['Low'], close=df['Close'], name='US30'
    ), row=1, col=1)
    
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA20'], name='SMA 20', line=dict(color='orange', width=1.5)), row=1, col=1)

    # RSI Momentum (Row 2)
    fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], name='RSI', line=dict(color='#8A2BE2', width=2)), row=2, col=1)
    fig.add_hline(y=70, line_dash="dot", line_color="red", row=2, col=1)
    fig.add_hline(y=30, line_dash="dot", line_color="green", row=2, col=1)

    # Add Buy/Sell Annotations on Candles (Fixing the logic to avoid clutter)
    for i in range(1, len(df)):
        if df['Entry'].iloc[i] == 2: # Price crosses UP
            fig.add_annotation(x=df.index[i], y=df['Low'].iloc[i], text="BUY", bgcolor="green", font=dict(color="white"), ay=25, row=1, col=1)
        elif df['Entry'].iloc[i] == -2: # Price crosses DOWN
            fig.add_annotation(x=df.index[i], y=df['High'].iloc[i], text="SELL", bgcolor="red", font=dict(color="white"), ay=-25, row=1, col=1)

    fig.update_layout(template='plotly_dark', height=750, xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.info("Market is closed or data is initializing. Check again in a moment.")
