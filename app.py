import streamlit as st
import pandas as pd
import pandas_ta as ta
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime

# --- 1. SETTINGS & UI ---
st.set_page_config(page_title="PATRO AI PRO V11.6", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .stApp { background-color: #050505; color: white; }
    header, footer, #MainMenu {visibility: hidden;}
    .signal-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 30px;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA ENGINE (The "Blank Screen" Shield) ---
@st.cache_data(ttl=30)
def get_patro_data(ticker, interval):
    try:
        # Step A: Download
        df = yf.download(ticker, period="5d", interval=interval, auto_adjust=True, progress=False)
        
        if df is None or df.empty:
            return None
            
        # Step B: FIX MULTIINDEX (The Error Killer)
        # If columns look like ('Close', 'GC=F'), this flattens them to just 'Close'
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        
        # Step C: Indicators
        df['VWAP'] = ta.vwap(df['High'], df['Low'], df['Close'], df['Volume'])
        df['ADX'] = ta.adx(df['High'], df['Low'], df['Close'])['ADX_14']
        macd = ta.macd(df['Close'])
        df['MACD_H'] = macd['MACDh_12_26_9']
        df['RSI'] = ta.rsi(df['Close'], length=14)
        
        return df.dropna()
