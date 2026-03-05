import streamlit as st
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yfinance as yf

# 1. SYSTEM SETUP
st.set_page_config(page_title="PATRO AI PRO V9.7", layout="wide")

def play_alert():
    audio_html = """<audio autoplay><source src="https://www.soundjay.com/buttons/sounds/button-3.mp3" type="audio/mpeg"></audio>"""
    st.markdown(audio_html, unsafe_allow_html=True)

# 2. DATA ENGINE
@st.cache_data(ttl=30)
def get_clean_data(ticker, interval):
    try:
        df = yf.download(ticker, period="1d", interval=interval, progress=False)
        if df.empty or len(df) < 35: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        df['SMA'] = ta.sma(df['Close'], length=20)
        df['VWAP'] = ta.vwap(df['High'], df['Low'], df['Close'], df['Volume'])
        df['Dist_Pct'] = ((df['Close'] - df['VWAP']) / df['VWAP']) * 100
        macd = ta.macd(df['Close'])
        if macd is not None:
            df['MACD_L'], df['MACD_H'], df['MACD_S'] = macd.iloc[:, 0], macd.iloc[:, 1], macd.iloc[:, 2]
        adx = ta.adx(df['High'], df['Low'], df['Close'], length=14)
        if adx is not None: df['ADX_P'] = adx.iloc[:, 0]
        return df.dropna()
    except: return None

# 3. SIDEBAR
with st.sidebar:
    st.title("🌌 PATRO CONTROL")
    if st.button("🔄 FORCE DATA SYNC"):
        st.cache_data.clear()
        st.rerun()
    
    st.divider()
    st.markdown("### ⚡ POWER & SAFETY")
    min_power = st.slider("Min Entry Power (ADX)", 15, 45, 25)
    max_gap = st.slider("Max VWAP Gap %", 0.05, 0.30, 0.15)
    sound_on = st.toggle("Enable Alert Sound", value=True)

    asset_map = {"XAUUSD (GOLD)": "GC=F", "US30 (DOW JONES)": "^DJI"}
    asset_label = st.selectbox("Asset", list(asset_map.keys()))
    ticker = asset_map[asset_label]
    selected_tf = st.radio("Display Chart", ["1m", "5m", "15m"], index=0, horizontal=True)
    show_analysis = st.toggle("Show MACD Analysis Row", value=True)

# 4. SCANNER & LOGIC
def check_trend(df):
    if df is None: return 0
    last = df.iloc[-1]
    if last['Close'] > last['VWAP'] and last['MACD_H'] > 0: return 1
    if last['Close'] < last['VWAP'] and last['MACD_H'] < 0: return -1
    return 0

df1, df5, df15 = get_clean_data(ticker, "1m"), get_clean_data(ticker, "5m"), get_clean_data(ticker, "15m")
t1, t5, t15 = check_trend(df1), check_trend(df5), check_trend(df15)
total_confluence = t1 + t5 + t15

active_df = {"1m": df1, "5m": df5, "15m": df15}[selected_tf]
signal_text, signal_clr = "⚖️ NEUTRAL / WAITING", "#808080"

if active_df is not None:
    last, prev = active_df.iloc[-1], active_df.iloc[-2]
    last_pwr = last['ADX_P']
    pwr_rising = last_pwr > prev['ADX_P']
    is_safe_gap = abs(last['Dist_Pct']) <= max_gap

    if abs(total_confluence) == 3 and last_pwr >= min_power and pwr_rising:
        if is_safe_gap:
            signal_text = "🚀 LOCKED BUY (POWER ALIGNED)" if total_confluence == 3 else "📉 LOCKED SELL (POWER ALIGNED)"
            signal_clr = "#00FF00" if total_confluence == 3 else "#FF0000"
            if sound_on: play_alert()
        else:
            signal_text, signal_clr = "⚠️ OVEREXTENDED (GAP TOO LARGE)", "#FFA500"

st.markdown(f"<h1 style='text-align: center; color: {signal_clr};'>{signal_text}</h1>", unsafe_allow_html=True)

if active_df is not None:
    with st.sidebar:
        st.divider()
        st.markdown("### 🔍 MTF STATUS")
        st.write(f"1M: {'🟢' if t1==1 else '🔴' if t1==-1 else '⚪'}")
        st.write(f"5M: {'🟢' if t5==1 else '🔴' if t5==-1 else '⚪'}")
        st.write(f"15M: {'🟢' if t15==1 else '🔴' if t15==-1 else '⚪'}")
        
        st.divider()
        # --- RESTORED POWER & ARROWS ---
        arrow = "▲" if pwr_rising else "▼"
        arrow_clr = "#00FF00" if pwr_rising else "#FF0000"
        pwr_display_clr = "#FFFF00" if last_pwr < 20 else "#00FF00" if last_pwr < 40 else "#FF0000"
        
        st.markdown(f"### ⚡ POWER: <span style='color:{pwr_display_clr}'>{last_pwr:.1f}%</span> <span style='color:{arrow_clr}'>{arrow}</span>", unsafe_allow_html=True)
        st.progress(min(max(last_pwr / 100, 0.0), 1.0))
        
        st.markdown(f"**GAP Status:** {last['Dist_Pct']:.3f}%")
        st.progress(min(max(abs(last['Dist_Pct']) / max_gap, 0.0), 1.0))

    # 6. CHARTING
    rows = 3 if show_analysis else 1
    heights = [0.5, 0.2, 0.3] if show_analysis else [1.0]
    fig = make_subplots(rows=rows, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=heights)
    fig.add_trace(go.Candlestick(x=active_df.index, open=active_df['Open'], high=active_df['High'], low=active_df['Low'], close=active_df['Close'], name="Price"), row=1, col=1)
    fig.add_trace(go.Scatter(x=active_df.index, y=active_df['VWAP'], line=dict(color='orange', width=2), name="VWAP"), row=1, col=1)
    if show_analysis:
        v_colors = ['#26A69A' if active_df['Close'][i] >= active_df['Open'][i] else '#EF5350' for i in range(len(active_df))]
        fig.add_trace(go.Bar(x=active_df.index, y=active_df['Volume'], name="Volume", marker_color=v_colors), row=2, col=1)
        h_colors = ['#26A69A' if val > 0 else '#EF5350' for val in active_df['MACD_H']]
        fig.add_trace(go.Bar(x=active_df.index, y=active_df['MACD_H'], name="Hist", marker_color=h_colors), row=3, col=1)
    fig.update_layout(height=850, template="plotly_dark", xaxis_rangeslider_visible=False, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
