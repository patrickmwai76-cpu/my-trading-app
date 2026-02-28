import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import hmac

# --- 1. PRO CONFIG & SECURITY ---
st.set_page_config(page_title="PATRO AI PRO", layout="wide", initial_sidebar_state="expanded")

def check_password():
    def credentials_entered():
        if (st.session_state["username"] == st.secrets["username"] and 
            hmac.compare_digest(st.session_state["password"], st.secrets["password"])):
            st.session_state["password_correct"] = True
            del st.session_state["username"]
            del st.session_state["password"]
        else: st.session_state["password_correct"] = False
    if st.session_state.get("password_correct", False): return True
    st.markdown("<h1 style='text-align:center; color:#00ff00;'>🛡️ PATRO AI PRO</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        st.text_input("Operator ID", key="username")
        st.text_input("Access Key", type="password", key="password")
        st.button("INITIALIZE TERMINAL", on_click=credentials_entered, use_container_width=True)
    return False

if not check_password(): st.stop()

# --- 2. DATA ENGINES ---
@st.cache_data(ttl=60)
def get_institutional_data():
    df = yf.download("^DJI", period="1d", interval="1m", progress=False)
    df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
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

@st.cache_data(ttl=60)
def get_mtf(ticker, interval):
    try:
        data = yf.download(ticker, period="2d", interval=interval, progress=False)
        data.columns = [col[0] if isinstance(col, tuple) else col for col in data.columns]
        sma = data['Close'].rolling(window=20).mean()
        return "UP" if data['Close'].iloc[-1] > sma.iloc[-1] else "DOWN"
    except: return "N/A"

# DATA LOAD
df = get_institutional_data()
t1, t5, t15 = get_mtf("^DJI", "1m"), get_mtf("^DJI", "5m"), get_
