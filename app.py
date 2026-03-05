import streamlit as st
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yfinance as yf

# 1. SYSTEM SETUP
st.set_page_config(page_title="PATRO AI PRO V9.5", layout="wide")

# Function for Sound Alert
def play_alert():
    audio_html = """
    <audio autoplay>
      <source src="https://www.soundjay.com/buttons/sounds/button-3.mp3" type="audio/mpeg">
    </audio>
    """
    st.markdown(audio_html, unsafe_allow_html=True)

# 2. BULLETPROOF DATA ENGINE
@st.cache_data(ttl=30)
def get_clean_data(ticker, interval):
    try:
        df = yf.download(ticker, period="1d", interval=interval, progress=False)
        if df.empty or len(df) < 35: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        
        # CORE INDICATORS
        df['SMA'] = ta.sma(df['Close'], length=20)
        df['VWAP'] = ta.vwap(df['High'], df['Low'], df['Close'], df['Volume'])
        
        # --- NEW: DISTANCE CALCULATION ---
        # Measures how far price is from fair value (VWAP) as a %
        df['Dist_Pct'] = ((df['Close'] - df['VWAP']) / df['VWAP']) * 100
        
        macd = ta.macd(df['Close'])
        if macd is not None:
            df['MACD_L'], df['MACD_H'], df['MACD_S'] = macd.iloc[:, 0], macd.iloc[:, 1], macd.iloc[:, 2]
        
        adx = ta.adx(df['High'], df['Low'], df['Close'], length=14)
        if adx is not None: df['ADX_P'] = adx.iloc[:, 0]
        
        return df.dropna()
    except: return None

# 3. SIDEBAR - MASTER CONTROL
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
    sop_macd = st.checkbox("Momentum Guard", value=True)
    
    st.divider()
    st.markdown("### ⚡ POWER & SAFETY")
    min_power = st.slider("Min Entry Power (ADX)", 15, 45, 25)
    # --- NEW: SAFETY THRESHOLD SLIDER ---
    max_gap = st.slider("Max VWAP Gap %", 0.05, 0.30, 0.15, help="Prevents entering too far from the line")
    sound_on = st.toggle("Enable Alert Sound", value=True)

    st.divider()
    asset_map = {"XAUUSD (GOLD)": "GC=F", "US30 (DOW JONES)": "^DJI"}
    asset_label = st.selectbox("Asset", list(asset_map.keys()))
    ticker = asset_map[asset_label]
    
    st.divider()
    st.markdown("### ⚙️ VISUALS")
    show_analysis = st.toggle("Show MACD Analysis Row", value=True)
    
    st.divider()
    st.markdown("### ⏲️ MASTER TIMEFRAME")
    selected_tf = st.radio("Display Chart", ["1m", "5m", "15m"], index=0, horizontal=True)

# 4. BACKGROUND CONFLUENCE SCANNER
def check_trend(df):
    if df is None: return 0
    last = df.iloc[-1]
    if last['Close'] > last['VWAP'] and last['MACD_H'] > 0: return 1
    if last['Close'] < last['VWAP'] and last['MACD_H'] < 0: return -1
    return 0

df1 = get_clean_data(ticker, "1m")
df5 = get_clean_data(ticker, "5m")
df15 = get_clean_data(ticker, "15m")

t1, t5, t15 = check_trend(df1), check_trend(df5), check_trend(df15)
total_confluence = t1 + t5 + t15

# 5. FINAL SIGNAL LOGIC (MTF + POWER + SAFETY GAP)
active_df = {"1m": df1, "5m": df5, "15m": df15}[selected_tf]
signal_text, signal_clr = "⚖️ NEUTRAL / WAITING", "#808080"

if active_df is not None:
    last, prev = active_df.iloc[-1], active_df.iloc[-2]
    last_pwr = last['ADX_P']
    pwr_rising = last_pwr > prev['ADX_P']
    # --- SAFETY CHECK ---
    is_safe_gap = abs(last['Dist_Pct']) <= max_gap

    if abs(total_confluence) == 3 and last_pwr >= min_power and pwr_rising:
        if is_safe_gap:
            if total_confluence == 3:
                signal_text, signal_clr = "🚀 LOCKED BUY (POWER ALIGNED)", "#00FF00"
            else:
                signal_text, signal_clr = "📉 LOCKED SELL (POWER ALIGNED)", "#FF0000"
            if sound_on: play_alert()
        else:
            # TRIGGERED BUT TOO FAR FROM VWAP
            signal_text, signal_clr = "⚠️ OVEREXTENDED (GAP TOO LARGE)", "#FFA500"

# --- MAIN DASHBOARD DISPLAY ---
st.markdown(f"<h1 style='text-align: center; color: {signal_clr};'>{signal_text}</h1>", unsafe_allow_html=True)

if active_df is not None:
    # SIDEBAR STATUS UPDATES
    with st.sidebar:
        st.divider()
        st.markdown(f"### 🔍 MTF STATUS")
        st.write(f"1M: {'🟢' if t1==1 else '🔴' if t1==-1 else '⚪'}")
        st.write(f"5M: {'🟢' if t5==1 else '🔴' if t5==-1 else '⚪'}")
        st.write(f"15M: {'🟢' if t15==1 else '🔴' if t15==-1 else '⚪'}")
        st.divider()
        st.markdown(f"### 📏 GAP: {last['Dist_Pct']:.3f}%")
        st.progress(min(max(abs(last['Dist_Pct']) / max_gap, 0.0), 1.0) if is_safe_gap else 1.0)

    # 6. TRIPLE-STACK CHARTING
    rows = 3 if show_analysis else
