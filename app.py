import streamlit as st
import pandas as pd
import pandas_ta as ta
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pytz

# 1. PAGE SETUP
st.set_page_config(page_title="PATRO AI PRO V11.4", layout="wide")

# 2. LIVE MARKET LEVELS (March 6, 2026)
MARKET_LEVELS = {
    "XAUUSD": {"Pivot": 5165, "R1": 5208, "S1": 5107, "NFP_Target": 5320},
    "US30": {"Pivot": 48300, "R1": 49017, "S1": 47660, "NFP_Target": 50000}
}

# 3. SIDEBAR: RISK & NEWS
with st.sidebar:
    st.title("🌌 PATRO V11.4")
    
    # NFP COUNTDOWN ALERT
    st.error("🚨 **NFP FRIDAY ALERT**")
    st.write("**US Employment Data: 16:30 EAT**")
    st.caption("Expect $50+ swings on Gold. Tighten Stop Losses!")

    st.divider()
    st.markdown("### 📋 INSTITUTIONAL SOP")
    sop_trend = st.checkbox("Trend Matrix Confluence", value=True)
    sop_vwap = st.checkbox("Price Action near VWAP", value=True)
    sop_vol = st.checkbox("Volume Confirmation", value=True)
    
    st.divider()
    st.markdown("### 🧮 POSITION CALCULATOR")
    balance = st.number_input("Account ($)", value=1000)
    risk_pct = st.slider("Risk %", 0.5, 3.0, 1.0)
    stop_pips = st.number_input("Stop Loss (Pips)", value=30)
    
    # Lot Calculation Logic
    risk_amt = balance * (risk_pct / 100)
    lots = risk_amt / (stop_pips * 10)
    st.success(f"Recommended Lot: {lots:.2f}")

# 4. DATA & SIGNAL ENGINE
@st.cache_data(ttl=30)
def get_data(ticker, interval):
    df = yf.download(ticker, period="2d", interval=interval, auto_adjust=True, progress=False)
    if df.empty: return None
    if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
    df['VWAP'] = ta.vwap(df['High'], df['Low'], df['Close'], df['Volume'])
    df['ADX'] = ta.adx(df['High'], df['Low'], df['Close'])['ADX_14']
    return df.dropna()

asset_map = {"XAUUSD": "GC=F", "US30": "^DJI"}
choice = st.selectbox("Select Market", list(asset_map.keys()))
df = get_data(asset_map[choice], "5m")

# 5. HEADER: SIGNAL LOCK & POWER
if df is not None:
    last, prev = df.iloc[-1], df.iloc[-2]
    pwr_up = last['ADX'] > prev['ADX']
    arrow = "▲" if pwr_up else "▼"
    
    # Signal Logic
    sig_text, sig_clr = "⚖️ SCANNING", "#808080"
    if last['Close'] > last['VWAP'] and last['ADX'] > 25 and pwr_up:
        sig_text, sig_clr = "🚀 LOCKED BUY", "#00FF00"
    elif last['Close'] < last['VWAP'] and last['ADX'] > 25 and pwr_up:
        sig_text, sig_clr = "📉 LOCKED SELL", "#FF0000"

    c1, c2 = st.columns([3, 2])
    with c1: st.markdown(f"<h1 style='color:{sig_clr};'>{sig_text}</h1>", unsafe_allow_html=True)
    with c2: st.markdown(f"### POWER: {last['ADX']:.1f}% {arrow}")

# 6. CHARTING WITH PIVOT LEVELS
if df is not None:
    fig = make_subplots(rows=1, cols=1)
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Price"))
    fig.add_trace(go.Scatter(x=df.index, y=df['VWAP'], line=dict(color='orange', width=2), name="VWAP"))
    
    # Add Today's Pivot Levels
    levels = MARKET_LEVELS[choice]
    fig.add_hline(y=levels['Pivot'], line_dash="dash", line_color="white", annotation_text="PIVOT")
    fig.add_hline(y=levels['R1'], line_dash="dot", line_color="red", annotation_text="RESISTANCE (R1)")
    fig.add_hline(y=levels['S1'], line_dash="dot", line_color="green", annotation_text="SUPPORT (S1)")
    
    fig.update_layout(height=700, template="plotly_dark", xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)
