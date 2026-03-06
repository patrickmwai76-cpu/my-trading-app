import streamlit as st
import pandas as pd
import pandas_ta as ta
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime

# --- 1. SETTINGS & UI ---
st.set_page_config(page_title="PATRO AI PRO V11.6", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #050505; color: white; }
    .error-box { padding: 20px; background: #330000; border: 1px solid #ff3366; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. THE DATA FIX (Prevents Blank Screen) ---
@st.cache_data(ttl=30)
def get_safe_data(ticker, interval):
    try:
        # Fetch data
        df = yf.download(ticker, period="5d", interval=interval, auto_adjust=True, progress=False)
        
        if df is None or df.empty:
            st.warning(f"Waiting for market data for {ticker}...")
            return None
            
        # FIX: Flatten columns if yfinance returns multi-levels (Common 2026 Bug)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
            
        # Technicals
        df['VWAP'] = ta.vwap(df['High'], df['Low'], df['Close'], df['Volume'])
        df['ADX'] = ta.adx(df['High'], df['Low'], df['Close'])['ADX_14']
        macd = ta.macd(df['Close'])
        df['MACD_H'] = macd['MACDh_12_26_9']
        df['RSI'] = ta.rsi(df['Close'])
        
        return df.dropna()
    except Exception as e:
        st.error(f"Data Error: {e}")
        return None

# --- 3. THE UI & LOGIC ---
st.title("🌌 PATRO AI PRO V11.6")

# Asset selection
asset = st.selectbox("Select Asset", ["GC=F", "^DJI", "GBPUSD=X"], format_func=lambda x: "GOLD" if "GC" in x else "US30" if "^DJI" in x else "GBPUSD")

data = get_safe_data(asset, "5m")

if data is not None:
    # FILTER: "Real Signals" Only (First entry of a trend)
    data['Raw'] = 0
    data.loc[(data['Close'] > data['VWAP']) & (data['MACD_H'] > 0) & (data['ADX'] > 28) & (data['RSI'] < 70), 'Raw'] = 1
    data.loc[(data['Close'] < data['VWAP']) & (data['MACD_H'] < -0) & (data['ADX'] > 28) & (data['RSI'] > 30), 'Raw'] = -1
    
    # Only keep the change in signal
    data['Signal'] = data['Raw'].diff().fillna(0)
    
    last = data.iloc[-1]
    
    # Big Signal Card
    clr = "#00FF88" if last['Raw
