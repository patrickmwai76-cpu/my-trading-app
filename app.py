import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import hmac

# --- 1. BOOT SEQUENCE & SECURITY ---
st.set_page_config(page_title="PATRO AI PRO", layout="wide")

def check_password():
    def credentials_entered():
        if (st.session_state["username"] == st.secrets["username"] and 
            hmac.compare_digest(st.session_state["password"], st.secrets["password"])):
            st.session_state["password_correct"] = True
            del st.session_state["password"]
            del st.session_state["username"]
        else: st.session_state["password_correct"] = False
    
    if st.session_state.get("password_correct", False): return True
    
    st.markdown('<h1 style="color:#00ff00; text-align:center;">🛡️ PATRO AI PRO</h1>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.text_input("User Identity", key="username")
        st.text_input("Command Key", type="password", key="password")
        st.button("INITIALIZE SYSTEM", on_click=credentials_entered, use_container_width=True)
    return False

if not check_password(): st.stop()

# --- 2. THE ENGINE ---
@st.cache_data(ttl=60)
def get_all_data():
    try:
        df = yf.download("^DJI", period="1d", interval="1m", progress=False)
        df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
        
        # Indicators
        df['EMA20'] = df['Close'].ewm(span=20, adjust=False).mean()
        
        # RSI Calculation
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # Signal Logic
        df['Trend'] = 0
        df.loc[df['Close'] > df['EMA20'], 'Trend'] = 1
        df.loc[df['Close'] < df['EMA20'], 'Trend'] = -1
        df['Entry'] = df['Trend'].diff()
        return df
    except Exception as e:
        st.error(f"Connection Error: {e}")
        return None

df = get_all_data()

if df is not None:
    # --- 3. TOP ROW METRICS ---
    sig = "BUY" if df['Trend'].iloc[-1] == 1 else "SELL"
    sig_c = "#00ff00" if sig == "BUY" else "#ff4b4b"
    
    st.markdown(f"<h1 style='text-align:center; color:{sig_c};'>LIVE SIGNAL: {sig}</h1>", unsafe_allow_html=True)
    
    m1, m2, m3 = st.columns(3)
    m1.metric("US30 PRICE", f"${df['Close'].iloc[-1]:,.2f}")
    m2.metric("CURRENT RSI", f"{df['RSI'].iloc[-1]:.2f}")
    m3.metric("EMA 20", f"{df['EMA20'].iloc[-1]:.2f}")

    # --- 4. THE CHART (PRICE + VOLUME + RSI) ---
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, 
                        vertical_spacing=0.02, 
                        row_heights=[0.6, 0.2, 0.2])

    # Candlesticks
    fig.add_trace(go.Candlestick(
        x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
        name='Price', increasing_line_color='#00ff00', decreasing_line_color='#ff4b4b'
    ), row=1, col=1)

    # BUY/SELL Tags
    buys = df[df['Entry'] == 2]
    fig.add_trace(go.Scatter(x=buys.index, y=bu
