import streamlit as st
import pandas as pd
import pandas_ta as ta
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

# --- 1. PREMIUM PAGE SETUP ---
st.set_page_config(page_title="PATRO AI PRO V11.6", layout="wide", initial_sidebar_state="expanded")

# Glassmorphism & Neon CSS
st.markdown("""
    <style>
    .stApp { background-color: #050505; color: white; }
    header, footer, #MainMenu {visibility: hidden;}
    
    .signal-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 25px;
        padding: 30px;
        text-align: center;
        box-shadow: 0 15px 35px rgba(0,0,0,0.8);
        margin-bottom: 20px;
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] { background-color: #0a0a0a !important; border-right: 1px solid #222; }
    .stCheckbox { font-size: 12px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA ENGINE (Cloud Stable) ---
@st.cache_data(ttl=20)
def get_patro_data(ticker, interval):
    try:
        df = yf.download(ticker, period="5d", interval=interval, auto_adjust=True, progress=False)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): 
            df.columns = df.columns.get_level_values(0)
        
        # Technicals
        df['VWAP'] = ta.vwap(df['High'], df['Low'], df['Close'], df['Volume'])
        df['SMA200'] = ta.sma(df['Close'], length=200)
        df['ADX'] = ta.adx(df['High'], df['Low'], df['Close'])['ADX_14']
        macd = ta.macd(df['Close'])
        df['MACD_H'] = macd['MACDh_12_26_9']
        df['RSI'] = ta.rsi(df['Close'], length=14)
        
        # Signal Logic (Clean Filter)
        df['Raw'] = 0
        df.loc[(df['Close'] > df['VWAP']) & (df['MACD_H'] > 0) & (df['ADX'] > 28), 'Raw'] = 1
        df.loc[(df['Close'] < df['VWAP']) & (df['MACD_H'] < 0) & (df['ADX'] > 28), 'Raw'] = -1
        df['Entry'] = df['Raw'].diff().fillna(0)
        
        return df.dropna()
    except: return None

# --- 3. THE INSTITUTIONAL SIDEBAR ---
with st.sidebar:
    st.title("🌌 PATRO V11.6")
    st.error("⚠️ **HIGH IMPACT NEWS**\nCheck ForexFactory for NFP/CPI.")
    
    st.divider()
    st.markdown("### 📋 INSTITUTIONAL SOP")
    sop1 = st.checkbox("Trend Matrix Confluence", value=True)
    sop2 = st.checkbox("Price Action near VWAP", value=True)
    sop3 = st.checkbox("Volume Confirmation", value=True)
    sop4 = st.checkbox("Momentum Guard (MACD/RSI)", value=True)
    
    st.divider()
    st.markdown("### 🧮 RISK CALCULATOR")
    balance = st.number_input("Account Balance ($)", value=1000)
    risk_pct = st.slider("Risk Per Trade %", 0.5, 5.0, 1.0)
    sl_pips = st.number_input("Stop Loss (Pips)", value=30)
    
    # Lot Calculation Logic
    risk_amount = balance * (risk_pct / 100)
    rec_lots = risk_amount / (sl_pips * 10) if sl_pips > 0 else 0.01
    st.success(f"Recommended Lot: **{rec_lots:.2f}**")

    st.divider()
    asset_map = {"XAUUSD": "GC=F", "US30": "^DJI", "GBPUSD": "GBPUSD=X"}
