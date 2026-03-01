import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import hmac
from datetime import datetime
import pytz

# --- 1. SYSTEM CONFIG & SECURITY ---
st.set_page_config(page_title="PATRO AI PRO", layout="wide", initial_sidebar_state="expanded")

# (Keep your check_password() function here exactly as it is)

# --- 2. TIMEZONE CLOCKS ---
# Getting current time for Kenya and New York
kenya_tz = pytz.timezone('Africa/Nairobi')
ny_tz = pytz.timezone('America/New_York')

kenya_time = datetime.now(kenya_tz).strftime("%H:%M")
ny_time = datetime.now(ny_tz).strftime("%H:%M")

# --- 3. DATA ENGINE (US30 ONLY) ---
@st.cache_data(ttl=60)
def get_master_data():
    df = yf.download("^DJI", period="1d", interval="1m", progress=False)
    df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
    
    df['TP'] = (df['High'] + df['Low'] + df['Close']) / 3
    df['PV'] = df['TP'] * df['Volume']
    df['VWAP'] = df['PV'].cumsum() / df['Volume'].cumsum()
    df['EMA20'] = df['Close'].ewm(span=20, adjust=False).mean()
    
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    df['RSI'] = 100 - (100 / (1 + (gain / loss)))
    
    df['Trend'] = 0
    df.loc[df['Close'] > df['EMA20'], 'Trend'] = 1
    df.loc[df['Close'] < df['EMA20'], 'Trend'] = -1
    df['Entry'] = df['Trend'].diff()
    return df

# (Keep get_mtf function here)

df = get_master_data()
sig = "BUY" if df['Trend'].iloc[-1] == 1 else "SELL"
sig_color = "#00ff00" if sig == "BUY" else "#ff4b4b"

# --- 4. HEADER WITH DUAL CLOCKS ---
st.markdown(f"""
    <div style="background-color:#1e2130; padding:15px; border-radius:10px; border-left: 10px solid {sig_color};">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h1 style="margin:0; color:#ffffff; font-size:28px;">🛡️ PATRO AI PRO <span style="color:{sig_color};">| {sig} MODE</span></h1>
                <p style="margin:0; color:grey; font-size:12px;">Institutional Scalping Terminal v4.0</p>
            </div>
            <div style="text-align: right; color: white;">
                <p style="margin:0; font-size:14px;">🇰🇪 Nairobi: <strong>{kenya_time}</strong></p>
                <p style="margin:0; font-size:14px;">🇺🇸 New York: <strong>{ny_time}</strong></p>
                <p style="margin:0; font-size:10px; color:#00ff00;">NYSE OPENS AT 17:30 EAT</p>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

# (Rest of the script: News Guard, 3-Layer Chart, and SOP Sidebar remains identical)
