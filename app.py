import streamlit as st
import pandas as pd
import pandas_ta as ta  # MUST BE IN YOUR REQUIREMENTS.TXT
import plotly.graph_objects as go
import yfinance as yf

# 1. STABLE SETUP
st.set_page_config(page_title="PATRO AI PRO V8.8", layout="wide")

# 2. SIDEBAR - ALL FEATURES SQUEEZED
with st.sidebar:
    st.title("🌌 PATRO CONTROL")
    news_mode = st.toggle("ACTIVATE NEWS GUARD", value=True)
    if st.button("🔄 FORCE DATA SYNC"):
        st.cache_data.clear()
        st.rerun()
    
    st.divider()
    st.markdown("### 📋 INSTITUTIONAL SOP")
    sop_trend = st.checkbox("Trend Matrix Confluence", value=True)
    sop_vwap = st.checkbox("Price Action near VWAP", value=True)
    sop_vol = st.checkbox("Volume Confirmation", value=True)
    sop_macd = st.checkbox("MACD Momentum Guard", value=True)
    
    st.divider()
    asset_map = {"XAUUSD (GOLD)": "GC=F", "US30 (DOW_JONES)": "^DJI"}
    asset_label = st.selectbox("Asset", list(asset_map.keys()))
    tf = st.radio("Timeframe", ["1m", "5m", "15m"], horizontal=True)

# 3. DATA ENGINE (MULTI-INDEX FIX)
@st.cache_data(ttl=30)
def get_data(ticker, interval):
    df = yf.download(ticker, period="1d", interval=interval)
    # FIX: Flattens MultiIndex columns from Yahoo Finance
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    
    # Calculate Indicators
    df['SMA'] = ta.sma(df['Close'], length=20)
    df['VWAP'] = ta.vwap(df['High'], df['Low'], df['Close'], df['Volume'])
    adx = ta.adx(df['High'], df['Low'], df['Close'])
    df['ADX'] = adx['ADX_14']
    macd = ta.macd(df['Close'])
    df['Hist'] = macd['MACDh_12_26_9']
    return df.dropna()

try:
    df = get_data(asset_map[asset_label], tf)
    last, prev = df.iloc[-1], df.iloc[-2]
    
    # POWER METER (SIDEBAR)
    with st.sidebar:
        st.divider()
        arrow = "▲" if last['ADX'] > prev['ADX'] else "▼"
        color = "green" if arrow == "▲" else "red"
        st.markdown(f"### ⚡ POWER: {last['ADX']:.1f}% <span style='color:{color}'>{arrow}</span>", unsafe_allow_html=True)
        st.progress(min(max(last['ADX'] / 100, 0.0), 1.0))

    # MAIN CHART (STABLE WIDTH)
    fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
    fig.add_trace(go.Scatter(x=df.index, y=df['VWAP'], line=dict(color='orange', width=2), name="VWAP"))
    fig.update_layout(template="plotly_dark", height=600, xaxis_rangeslider_visible=False)
    
    # FIX: Replaced 'stretch' with compatible boolean
    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"⚠️ DATA SYNC ERROR: {e}")
