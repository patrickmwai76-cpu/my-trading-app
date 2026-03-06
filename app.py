import streamlit as st
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yfinance as yf
from datetime import datetime
import pytz

# 1. SYSTEM SETUP
st.set_page_config(page_title="PATRO AI PRO V10.3", layout="wide")

# 2. SESSION CLOCK (Nairobi Time)
eat = pytz.timezone('Africa/Nairobi')
now_eat = datetime.now(eat).time()

def get_session_status():
    if datetime.strptime("03:00", "%H:%M").time() <= now_eat < datetime.strptime("10:00", "%H:%M").time():
        return "🔵 ASIA (TOKYO)", "Low Volatility - Watch for Traps", "#1E90FF"
    elif datetime.strptime("10:00", "%H:%M").time() <= now_eat < datetime.strptime("15:00", "%H:%M").time():
        return "🟢 LONDON OPEN", "High Volume - Trend Formation", "#00FF00"
    elif datetime.strptime("15:00", "%H:%M").time() <= now_eat < datetime.strptime("19:00", "%H:%M").time():
        return "🔥 THE OVERLAP", "MAX VOLATILITY", "#FF4500"
    else:
        return "🔴 NEW YORK / NIGHT", "Fast Moves - Watch Reversals", "#FF0000"

session_name, session_vibe, session_clr = get_session_status()

# 3. DATA ENGINE
@st.cache_data(ttl=30)
def get_full_data(ticker, interval):
    try:
        df = yf.download(ticker, period="1d", interval=interval, progress=False)
        if df.empty or len(df) < 35: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        df['VWAP'] = ta.vwap(df['High'], df['Low'], df['Close'], df['Volume'])
        macd = ta.macd(df['Close'])
        df['MACD'], df['MACD_H'], df['MACD_S'] = macd.iloc[:, 0], macd.iloc[:, 1], macd.iloc[:, 2]
        df['ADX'] = ta.adx(df['High'], df['Low'], df['Close'])['ADX_14']
        return df.dropna()
    except: return None

# 4. SIDEBAR - MASTER CONTROL
with st.sidebar:
    st.markdown(f"<h2 style='color:{session_clr}; text-align:center;'>{session_name}</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center;'>{session_vibe}</p>", unsafe_allow_html=True)
    
    st.divider()
    # RESTORED: INSTITUTIONAL SOP CHECKLIST
    st.markdown("### 📋 INSTITUTIONAL SOP")
    sop_trend = st.checkbox("Trend Matrix Confluence", value=True)
    sop_vwap = st.checkbox("Price Action near VWAP", value=True)
    sop_vol = st.checkbox("Volume Confirmation", value=True)
    sop_macd = st.checkbox("Momentum Guard", value=True)
    
    st.divider()
    asset_map = {"XAUUSD (GOLD)": "GC=F", "US30 (DOW JONES)": "^DJI"}
    asset_label = st.selectbox("Select Asset", list(asset_map.keys()))
    ticker = asset_map[asset_label]
    selected_tf = st.radio("Timeframe", ["1m", "5m", "15m"], index=0, horizontal=True)
    
    # 5. RESTORED TREND MATRIX & DATA
    df1, df5, df15 = get_full_data(ticker, "1m"), get_full_data(ticker, "5m"), get_full_data(ticker, "15m")
    
    if df1 is not None:
        last, prev = df1.iloc[-1], df1.iloc[-2]
        st.divider()
        st.markdown("### 🔍 TREND MATRIX")
        def check_trend(df):
            if df is None: return 0
            l = df.iloc[-1]
            if l['Close'] > l['VWAP'] and l['MACD_H'] > 0: return 1
            if l['Close'] < l['VWAP'] and l['MACD_H'] < 0: return -1
            return 0
        
        t1, t5, t15 = check_trend(df1), check_trend(df5), check_trend(df15)
        st.write(f"1M: {'🟢' if t1==1 else '🔴' if t1==-1 else '⚪'}")
        st.write(f"5M: {'🟢' if t5==1 else '🔴' if t5==-1 else '⚪'}")
        st.write(f"15M: {'🟢' if t15==1 else '🔴' if t15==-1 else '⚪'}")
        
        st.divider()
        # RESTORED: POWER & ARROWS
        pwr_rising = last['ADX'] > prev['ADX']
        arrow = "▲" if pwr_rising else "▼"
        arrow_clr = "#00FF00" if pwr_rising else "#FF0000"
        st.markdown(f"### ⚡ POWER: {last['ADX']:.1f}% <span style='color:{arrow_clr}'>{arrow}</span>", unsafe_allow_html=True)
        st.progress(min(last['ADX']/100, 1.0))

# 6. SIGNAL LOGIC & MAIN CHART
active_df = {"1m": df1, "5m": df5, "15m": df15}[selected_tf]
signal_text, signal_clr = "⚖️ NEUTRAL / WAITING", "#808080"

if active_df is not None:
    last = active_df.iloc[-1]
    # RESTORED: TRIPLE-LOCK SIGNAL LOGIC
    if abs(t1 + t5 + t15) == 3 and last['ADX'] >= 25 and pwr_rising:
        signal_text = "🚀 LOCKED BUY" if (t1+t5+t15) == 3 else "📉 LOCKED SELL"
        signal_clr = "#00FF00" if (t1+t5+t15) == 3 else "#FF0000"

st.markdown(f"<h1 style='text-align:center; color:{signal_clr};'>{signal_text}</h1>", unsafe_allow_html=True)

if active_df is not None:
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.6, 0.15, 0.25])
    
    # [Price, Volume, and MACD Traces]
    fig.add_trace(go.Candlestick(x=active_df.index, open=active_df['Open'], high=active_df['High'], low=active_df['Low'], close=active_df['Close'], name="Price"), row=1, col=1)
    fig.add_trace(go.Scatter(x=active_df.index, y=active_df['VWAP'], line=dict(color='orange', width=2), name="VWAP"), row=1, col=1)
    
    v_colors = ['#00FF00' if active_df['Close'][i] >= active_df['Open'][i] else '#FF0000' for i in range(len(active_df))]
    fig.add_trace(go.Bar(x=active_df.index, y=active_df['Volume'], name="Volume", marker_color=v_colors), row=2, col=1)
    
    h_colors = ['#26A69A' if val > 0 else '#EF5350' for val in active_df['MACD_H']]
    fig.add_trace(go.Bar(x=active_df.index, y=active_df['MACD_H'], name="MACD Hist", marker_color=h_colors), row=3, col=1)

    fig.update_layout(height=900, template="plotly_dark", xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)
