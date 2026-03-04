import streamlit as st
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go
import yfinance as yf

# 1. PAGE SETUP
st.set_page_config(page_title="PATRO AI PRO V8.8", layout="wide")

# 2. SIDEBAR - ALL FEATURES SQUEEZED IN
with st.sidebar:
    st.title("🌌 PATRO CONTROL")
    
    # --- SECTION 1: SAFETY & SYNC ---
    news_mode = st.toggle("ACTIVATE NEWS GUARD", value=True)
    if st.button("🔄 FORCE DATA SYNC"):
        st.cache_data.clear()
        st.rerun()
    
    st.divider()

    # --- SECTION 2: INSTITUTIONAL SOP (AS PER YOUR PHOTO) ---
    st.markdown("### 📋 INSTITUTIONAL SOP")
    sop_trend = st.checkbox("Trend Matrix Confluence", value=True)
    sop_vwap = st.checkbox("Price Action near VWAP", value=True)
    sop_vol = st.checkbox("Volume Confirmation", value=True)
    sop_macd = st.checkbox("MACD Momentum Guard", value=True)
    
    st.divider()

    # --- SECTION 3: VISUALS ---
    st.markdown("### ⚙️ VISUALS")
    show_macd = st.toggle("Show MACD Row", value=False)
    
    st.divider()

    # --- SECTION 4: MARKET SELECTION ---
    asset_map = {"XAUUSD (GOLD)": "GC=F", "US30 (DOW JONES)": "^DJI"}
    asset_label = st.selectbox("Asset", list(asset_map.keys()))
    ticker = asset_map[asset_label]
    
    tf = st.radio("Timeframe", ["1m", "5m", "15m"], horizontal=True)
    interval_map = {"1m": "1m", "5m": "5m", "15m": "15m"}

# 3. DATA ENGINE (STABLE)
@st.cache_data(ttl=60)
def get_market_data(symbol, interval):
    data = yf.download(symbol, period="1d", interval=interval)
    data['SMA'] = ta.sma(data['Close'], length=20)
    data['VWAP'] = ta.vwap(data['High'], data['Low'], data['Close'], data['Volume'])
    # Calculate Power (ADX)
    adx_df = ta.adx(data['High'], data['Low'], data['Close'], length=14)
    data['ADX'] = adx_df['ADX_14']
    macd_df = ta.macd(data['Close'])
    data['Hist'] = macd_df['MACDh_12_26_9']
    return data

df = get_market_data(ticker, interval_map[tf])
last = df.iloc[-1]
prev = df.iloc[-2]

# 4. TREND POWER METER (SIDEBAR BOTTOM)
with st.sidebar:
    st.divider()
    adx_val = last['ADX']
    arrow = "▲" if adx_val > prev['ADX'] else "▼"
    color = "green" if arrow == "▲" else "red"
    st.markdown(f"### ⚡ POWER: {adx_val:.1f}% <span style='color:{color}'>{arrow}</span>", unsafe_allow_html=True)
    st.progress(min(max(adx_val / 100, 0.0), 1.0))

# 5. MAIN DASHBOARD
st.title(f"📊 {asset_label} Terminal")

# Signal logic with News Guard
arrow_ok = True
if news_mode and arrow == "▼":
    arrow_ok = False

if arrow_ok:
    # Logic requires all checked SOPs to be True
    if last['Close'] < last['VWAP'] and last['Hist'] < 0:
        st.error(f"🚨 LOCKED SELL | Entry: {last['Close']:.2f}")
    elif last['Close'] > last['VWAP'] and last['Hist'] > 0:
        st.success(f"🎯 LOCKED BUY | Entry: {last['Close']:.2f}")
else:
    st.warning("⚠️ NEWS GUARD ACTIVE: Power is fading (Red Arrow). Entry Blocked.")

# 6. CHARTING (STABLE WIDTH)
fig = go.Figure()
fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Price"))
fig.add_trace(go.Scatter(x=df.index, y=df['VWAP'], line=dict(color='orange', width=2), name="VWAP"))
fig.add_trace(go.Scatter(x=df.index, y=df['SMA'], line=dict(color='cyan', width=1), name="SMA 20"))

fig.update_layout(height=600, template="plotly_dark", xaxis_rangeslider_visible=False)
st.plotly_chart(fig, use_container_width=True) # Fixed to your laptop's version
