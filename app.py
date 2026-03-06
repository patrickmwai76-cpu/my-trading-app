import streamlit as st
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yfinance as yf
from datetime import datetime
import pytz

# --- 1. SYSTEM SETUP ---
st.set_page_config(page_title="PATRO AI PRO V10.4", layout="wide")

# Nairobi Time for Sessions
eat = pytz.timezone('Africa/Nairobi')
now_eat = datetime.now(eat).time()

# --- 2. THE BULLETPROOF DATA ENGINE ---
def get_clean_data(ticker, interval):
    try:
        # We use auto_adjust=True and multi_level=False to fix the "Black Screen" data bug
        data = yf.download(
            tickers=ticker, 
            period="2d", 
            interval=interval, 
            auto_adjust=True, 
            multi_level=False, 
            progress=False
        )
        
        if data.empty:
            return None
            
        df = data.copy()
        # Clean columns if they are Multi-Index
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
            
        # Add Indicators
        df['VWAP'] = ta.vwap(df['High'], df['Low'], df['Close'], df['Volume'])
        macd = ta.macd(df['Close'])
        df['MACD_H'] = macd.iloc[:, 1]
        df['ADX'] = ta.adx(df['High'], df['Low'], df['Close'])['ADX_14']
        
        return df.dropna()
    except Exception as e:
        st.error(f"Logic Error: {e}")
        return None

# --- 3. SIDEBAR (Full Restore) ---
with st.sidebar:
    st.title("🌌 PATRO CONTROL")
    st.divider()
    
    # INSTITUTIONAL SOP
    st.markdown("### 📋 INSTITUTIONAL SOP")
    sop1 = st.checkbox("Trend Confluence", value=True)
    sop2 = st.checkbox("Volume Check", value=True)
    
    st.divider()
    asset_dict = {"XAUUSD (GOLD)": "GC=F", "US30 (DOW)": "^DJI"}
    choice = st.selectbox("Market", list(asset_dict.keys()))
    ticker = asset_dict[choice]
    tf = st.radio("Timeframe", ["1m", "5m", "15m"], horizontal=True)

# --- 4. EXECUTION ---
df_main = get_clean_data(ticker, tf)

if df_main is not None:
    last, prev = df_main.iloc[-1], df_main.iloc[-2]
    
    # TREND & POWER LOGIC
    pwr_rising = last['ADX'] > prev['ADX']
    arrow = "▲" if pwr_rising else "▼"
    arrow_clr = "#00FF00" if pwr_rising else "#FF0000"
    
    with st.sidebar:
        st.divider()
        st.markdown(f"### ⚡ POWER: {last['ADX']:.1f}% <span style='color:{arrow_clr}'>{arrow}</span>", unsafe_allow_html=True)
        st.progress(min(last['ADX']/100, 1.0))

    # CHARTING
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.02, row_heights=[0.6, 0.1, 0.3])
    
    # Candles
    fig.add_trace(go.Candlestick(x=df_main.index, open=df_main['Open'], high=df_main['High'], low=df_main['Low'], close=df_main['Close'], name="Price"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df_main.index, y=df_main['VWAP'], line=dict(color='orange', width=2), name="VWAP"), row=1, col=1)
    
    # Volume
    fig.add_trace(go.Bar(x=df_main.index, y=df_main['Volume'], name="Volume", marker_color='gray'), row=2, col=1)
    
    # MACD
    fig.add_trace(go.Bar(x=df_main.index, y=df_main['MACD_H'], name="MACD"), row=3, col=1)
    
    fig.update_layout(height=800, template="plotly_dark", xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)
    
else:
    # THE EMERGENCY START BUTTON
    st.error("🚨 CHART ENGINE STOPPED: NO DATA FROM MARKET")
    st.info("Yahoo Finance is blocking the request. Follow the fix below:")
    if st.button("🛠️ FORCE RE-INSTALL DATA DRIVERS"):
        st.code("pip install --upgrade yfinance pandas-ta", language="bash")
