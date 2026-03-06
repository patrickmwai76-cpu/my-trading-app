import streamlit as st
import pandas as pd
import pandas_ta as ta
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pytz
from datetime import datetime

# 1. PAGE SETUP
st.set_page_config(page_title="PATRO AI PRO V11.6", layout="wide")

# 2. DATA ENGINE (Multi-Indicator Stable Logic)
@st.cache_data(ttl=30)
def get_patro_data(ticker, interval):
    try:
        # Requesting 5d ensures enough candles for SMA 200
        df = yf.download(ticker, period="5d", interval=interval, auto_adjust=True, progress=False)
        if df.empty: return None
        
        # Flatten MultiIndex columns (Fixes common yfinance errors)
        if isinstance(df.columns, pd.MultiIndex): 
            df.columns = df.columns.get_level_values(0)
        
        # --- TECHNICAL INDICATORS ---
        df['VWAP'] = ta.vwap(df['High'], df['Low'], df['Close'], df['Volume'])
        df['SMA200'] = ta.sma(df['Close'], length=200) # White Dashed Trend Line
        df['RSI'] = ta.rsi(df['Close'], length=14)      # Purple Momentum Line
        
        # FULL MACD (Lines + Histogram)
        macd = ta.macd(df['Close'], fast=12, slow=26, signal=9)
        df['MACD'] = macd['MACD_12_26_9']
        df['MACD_S'] = macd['MACDs_12_26_9']
        df['MACD_H'] = macd['MACDh_12_26_9']
        
        # TREND STRENGTH
        df['ADX'] = ta.adx(df['High'], df['Low'], df['Close'])['ADX_14']
        
        # VOLUME SPIKE ENGINE
        df['Vol_Avg'] = df['Volume'].rolling(window=20).mean()
        df['Is_Spike'] = df['Volume'] > (df['Vol_Avg'] * 2.5)
        
        return df.dropna()
    except: return None

# 3. SIDEBAR: SOP, NEWS & RISK
with st.sidebar:
    st.title("🌌 PATRO V11.6")
    st.warning("⚠️ **HIGH IMPACT NEWS**")
    st.markdown("**Event:** US NFP / CPI Data  \n**Impact:** 🔴 ULTRA HIGH")
    
    st.divider()
    st.markdown("### 📋 INSTITUTIONAL SOP")
    st.checkbox("Trend Matrix Confluence", value=True)
    st.checkbox("Price Action near VWAP", value=True)
    st.checkbox("Volume Confirmation", value=True)
    st.checkbox("Momentum Guard (MACD/RSI)", value=True)
    
    st.divider()
    st.markdown("### 🧮 RISK CALCULATOR")
    balance = st.number_input("Account Balance ($)", value=1000)
    risk_pct = st.slider("Risk Per Trade %", 0.5, 5.0, 1.0)
    stop_pips = st.number_input("Stop Loss (Pips/Points)", value=30)
    
    risk_dollars = balance * (risk_pct / 100)
    recommended_lots = risk_dollars / (stop_pips * 10) 
    st.success(f"Recommended Lot: {recommended_lots:.2f}")

    st.divider()
    asset_dict = {"XAUUSD": "GC=F", "US30": "^DJI", "GBPUSD": "GBPUSD=X"}
    choice = st.selectbox("Market", list(asset_dict.keys()))
    tf = st.radio("Timeframe", ["1m", "5m", "15m"], horizontal=True, index=1)

# 4. TREND CONFLUENCE & POWER LOGIC
df1 = get_patro_data(asset_dict[choice], "1m")
df5 = get_patro_data(asset_dict[choice], "5m")
df15 = get_patro_data(asset_dict[choice], "15m")

def get_bias(df):
    if df is None or df.empty: return 0
    l = df.iloc[-1]
    # Triple Confluence Logic: Price vs VWAP + MACD Hist
    if l['Close'] > l['VWAP'] and l['MACD_H'] > 0: return 1
    if l['Close'] < l['VWAP'] and l['MACD_H'] < 0: return -1
    return 0

b1, b5, b15 = get_bias(df1), get_bias(df5), get_bias(df15)
active_df = {"1m": df1, "5m": df5, "15m": df15}[tf]

# 5. HEADER: SIGNAL LOCK & POWER ARROW
if active_df is not None:
    last, prev = active_df.iloc[-1], active_df.iloc[-2]
    power_up = last['ADX'] > prev['ADX']
    arrow = "▲" if power_up else "▼"
    arrow_clr = "#00FF00" if power_up else "#FF0000"
    
    confluence = (b1 + b5 + b15)
    signal_text, signal_clr = "⚖️ SCANNING", "#808080"
    
    if abs(confluence) == 3 and last['ADX'] > 25:
        signal_text = "🚀 LOCKED BUY" if confluence == 3 else "📉 LOCKED SELL"
        signal_clr = "#00FF00" if confluence == 3 else "#FF0000"

    c1, c2 = st.columns([3, 2])
    with c1:
        st.markdown(f"<h1 style='color:{signal_clr}; font-size: 50px; margin-bottom:0;'>{signal_text}</h1>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"### ⚡ POWER: {last['ADX']:.1f}% <span style='color:{arrow_clr}'>{arrow}</span>", unsafe_allow_html=True)
        st.progress(min(last['ADX']/100, 1.0))

# 6. CHARTING: 3-ROW SYNCED LAYOUT
if active_df is not None:
    fig = make_subplots(
        rows=3, cols=1, 
        shared_xaxes=True, 
        vertical_spacing=0.02, 
        row_heights=[0.5, 0.15, 0.35]
    )
    
    # ROW 1: CANDLES + VWAP + SMA 200
    fig.add_trace(go.Candlestick(x=active_df.index, open=active_df['Open'], high=active_df['High'], low=active_df['Low'], close=active_df['Close'], name="Price"), row=1, col=1)
    fig.add_trace(go.Scatter(x=active_df.index, y=active_df['VWAP'], line=dict(color='orange', width=2), name="VWAP"), row=1, col=1)
    fig.add_trace(go.Scatter(x=active_df.index, y=active_df['SMA200'], line=dict(color='white', width=1.5, dash='dot'), name="SMA 200"), row=1, col=1)
    
    # ASIA ZONES
    asia_range = active_df.between_time('03:00', '09:00')
    if not asia_range.empty:
        a_h, a_l = asia_range['High'].max(), asia_range['Low'].min()
        fig.add_hline(y=a_h, line_dash="dot", line_color="cyan", annotation_text="ASIA H", row=1, col=1)
        fig.add_hline(y=a_l, line_dash="dot", line_color="magenta", annotation_text="ASIA L", row=1, col=1)

    # ROW 2: VOLUME SPIKES
    v_colors = ['#FFFF00' if spike else '#444444' for spike in active_df['Is_Spike']]
    fig.add_trace(go.Bar(x=active_df.index, y=active_df['Volume'], marker_color=v_colors, name="Volume"), row=2, col=1)

    # ROW 3: MACD & RSI MOMENTUM
    h_colors = ['#00FF00' if val >= 0 else '#FF0000' for val in active_df['MACD_H']]
    fig.add_trace(go.Bar(x=active_df.index, y=active_df['MACD_H'], marker_color=h_colors, name="MACD Hist"), row=3, col=1)
    fig.add_trace(go.Scatter(x=active_df.index, y=active_df['MACD'], line=dict(color='#00E5FF', width=1.5), name="MACD Line"), row=3, col=1)
    fig.add_trace(go.Scatter(x=active_df.index, y=active_df['RSI'], line=dict(color='#C084FC', width=1.5), name="RSI Overlay"), row=3, col=1)

    fig.update_layout(height=850, template="plotly_dark", xaxis_rangeslider_visible=False, hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.error("Market Data Offline. Check your connection or yfinance status.")
