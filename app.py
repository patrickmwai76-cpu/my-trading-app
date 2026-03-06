import streamlit as st
import pandas as pd
import pandas_ta as ta
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import pytz

# 1. PAGE SETUP
st.set_page_config(page_title="PATRO AI PRO V11.1", layout="wide")

# 2. DATA ENGINE (Bulletproof)
@st.cache_data(ttl=30)
def get_patro_data(ticker, interval):
    try:
        df = yf.download(ticker, period="2d", interval=interval, auto_adjust=True, progress=False)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        
        # Technicals
        df['VWAP'] = ta.vwap(df['High'], df['Low'], df['Close'], df['Volume'])
        macd = ta.macd(df['Close'])
        df['MACD_H'] = macd.iloc[:, 1]
        df['ADX'] = ta.adx(df['High'], df['Low'], df['Close'])['ADX_14']
        return df.dropna()
    except: return None

# 3. SIDEBAR: THE INSTITUTIONAL SOP (RESTORED)
with st.sidebar:
    st.title("🌌 PATRO V11.1")
    
    st.markdown("### 📋 INSTITUTIONAL SOP")
    # Added keys so they persist during refreshes
    sop_trend = st.checkbox("Trend Matrix Confluence", value=True, key="sop_trend")
    sop_vwap = st.checkbox("Price Action near VWAP", value=True, key="sop_vwap")
    sop_vol = st.checkbox("Volume Confirmation", value=True, key="sop_vol")
    sop_macd = st.checkbox("Momentum Guard", value=True, key="sop_macd")
    
    st.divider()
    asset_dict = {"XAUUSD": "GC=F", "US30": "^DJI", "GBPUSD": "GBPUSD=X"}
    choice = st.selectbox("Select Asset", list(asset_dict.keys()))
    ticker = asset_dict[choice]
    tf = st.radio("Timeframe", ["1m", "5m", "15m"], horizontal=True, index=0)

# 4. TREND & SIGNAL LOGIC
df1, df5, df15 = get_patro_data(ticker, "1m"), get_patro_data(ticker, "5m"), get_patro_data(ticker, "15m")

def get_bias(df):
    if df is None: return 0
    l = df.iloc[-1]
    if l['Close'] > l['VWAP'] and l['MACD_H'] > 0: return 1
    if l['Close'] < l['VWAP'] and l['MACD_H'] < 0: return -1
    return 0

b1, b5, b15 = get_bias(df1), get_bias(df5), get_bias(df15)
active_df = {"1m": df1, "5m": df5, "15m": df15}[tf]

# SIGNAL FILTER (Only "LOCKED" if rules met)
signal_text, signal_clr = "⚖️ SCANNING", "#808080"
if active_df is not None:
    last, prev = active_df.iloc[-1], active_df.iloc[-2]
    power_up = last['ADX'] > prev['ADX']
    
    # Check for Confluence (1M+5M+15M) and Strength
    if (b1 + b5 + b15) == 3 and last['ADX'] > 25 and power_up:
        signal_text, signal_clr = "🚀 LOCKED BUY", "#00FF00"
    elif (b1 + b5 + b15) == -3 and last['ADX'] > 25 and power_up:
        signal_text, signal_clr = "📉 LOCKED SELL", "#FF0000"

st.markdown(f"<h1 style='text-align:center; color:{signal_clr};'>{signal_text}</h1>", unsafe_allow_html=True)

# 5. CHARTING WITH SESSION OVERLAYS (EAT TIME)
if active_df is not None:
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.6, 0.15, 0.25])
    
    # PRICE & VWAP
    fig.add_trace(go.Candlestick(x=active_df.index, open=active_df['Open'], high=active_df['High'], low=active_df['Low'], close=active_df['Close'], name="Price"), row=1, col=1)
    fig.add_trace(go.Scatter(x=active_df.index, y=active_df['VWAP'], line=dict(color='orange', width=2), name="VWAP"), row=1, col=1)
    
    # VOLUME
    v_colors = ['#00FF00' if active_df['Close'][i] >= active_df['Open'][i] else '#FF0000' for i in range(len(active_df))]
    fig.add_trace(go.Bar(x=active_df.index, y=active_df['Volume'], name="Volume", marker_color=v_colors), row=2, col=1)
    
    # MACD
    h_colors = ['#26A69A' if val > 0 else '#EF5350' for val in active_df['MACD_H']]
    fig.add_trace(go.Bar(x=active_df.index, y=active_df['MACD_H'], name="MACD Hist", marker_color=h_colors), row=3, col=1)

    # SESSION SHADING (Nairobi Time zones)
    # London: 10:00 - 19:00 EAT | NY: 15:00 - 00:00 EAT
    for i in range(0, len(active_df), 15): # Optimize loop
        dt = active_df.index[i].astimezone(pytz.timezone('Africa/Nairobi'))
        if 10 <= dt.hour < 19:
            fig.add_vrect(x0=dt, x1=dt, fillcolor="blue", opacity=0.03, layer="below", line_width=0, row=1, col=1)
        if 15 <= dt.hour < 24:
            fig.add_vrect(x0=dt, x1=dt, fillcolor="green", opacity=0.03, layer="below", line_width=0, row=1, col=1)

    fig.update_layout(height=900, template="plotly_dark", xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.error("Market Data Connection Error. Please refresh.")
