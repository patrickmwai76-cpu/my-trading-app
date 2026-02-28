import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import hmac
from datetime import datetime
import pytz

# --- 1. THE GATEKEEPER (Keep this exactly as is) ---
def check_password():
    def credentials_entered():
        if (st.session_state["username"] == st.secrets["username"] and 
            hmac.compare_digest(st.session_state["password"], st.secrets["password"])):
            st.session_state["password_correct"] = True
            del st.session_state["password"]
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False
    if st.session_state.get("password_correct", False): return True
    st.markdown('<h1 style="color:#00ff00; text-align:center;">🛡️ PATRO AI PRO</h1>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.text_input("User Identity", key="username")
        st.text_input("Command Key", type="password", key="password")
        st.button("INITIALIZE SYSTEM", on_click=credentials_entered)
    return False

st.set_page_config(page_title="PATRO AI PRO", layout="wide")
if not check_password(): st.stop()

# --- 2. SIDEBAR (Restored) ---
with st.sidebar:
    st.markdown("<h2 style='color: #00ff00;'>PATRO AI PRO</h2>", unsafe_allow_html=True)
    if st.button("🔄 REFRESH DATA"):
        st.cache_data.clear()
        st.rerun()
    st.divider()
    balance = st.number_input("Balance ($)", value=1000)
    risk_pct = st.slider("Risk (%)", 0.5, 5.0, 1.0)
    st.info(f"Risk Amount: ${balance * (risk_pct / 100):.2f}")

# --- 3. THE RULES (THE FIX IS HERE) ---
@st.cache_data(ttl=60)
def get_patro_data():
    df = yf.download("^DJI", period="1d", interval="1m")
    df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
    
    # Rule 1: Trend Filter (SMA 20)
    df['SMA20'] = df['Close'].rolling(window=20).mean()
    
    # Rule 2: Momentum (RSI 14)
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    df['RSI'] = 100 - (100 / (1 + (gain / loss)))
    
    # Rule 3: Entry Logic (The "Golden" Rule)
    df['Trend'] = 0
    # Price > SMA means Uptrend (1), Price < SMA means Downtrend (-1)
    df.loc[df['Close'] > df['SMA20'], 'Trend'] = 1
    df.loc[df['Close'] < df['SMA20'], 'Trend'] = -1
    
    # Entry Signal (When the Trend changes)
    df['Entry'] = df['Trend'].diff() 
    
    return df, df['High'].max(), df['Low'].min()

# --- 4. MAIN DASHBOARD ---
try:
    df, d_high, d_low = get_patro_data()
    curr_p = df['Close'].iloc[-1]
    curr_rsi = df['RSI'].iloc[-1]
    
    # Determining current status for the badge
    current_trend = df['Trend'].iloc[-1]
    signal_text = "BUY" if current_trend == 1 else "SELL"
    signal_color = "#00ff00" if current_trend == 1 else "#ff4b4b"

    st.markdown(f'<h1 style="color:{signal_color};">🛡️ PATRO AI PRO: {signal_text}</h1>', unsafe_allow_html=True)

    m1, m2, m3 = st.columns(3)
    m1.metric("US30 PRICE", f"${curr_p:,.2f}")
    m2.metric("SIGNAL", signal_text)
    m3.metric("RSI (14)", f"{curr_rsi:.2f}")

    # Plotly Chart with restored Buy/Sell Markers
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.7, 0.3])
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='US30'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA20'], name='Trend Line', line=dict(color='orange', width=2)), row=1, col=1)
    
    # Restoring the Buy/Sell visual labels on the chart
    for i in range(1, len(df)):
        if df['Entry'].iloc[i] == 2: # Trend flipped from -1 to 1 (BUY)
            fig.add_annotation(x=df.index[i], y=df['Low'].iloc[i], text="BUY", bgcolor="green", font=dict(color="white"), ay=30)
        elif df['Entry'].iloc[i] == -2: # Trend flipped from 1 to -1 (SELL)
            fig.add_annotation(x=df.index[i], y=df['High'].iloc[i], text="SELL", bgcolor="red", font=dict(color="white"), ay=-30)

    fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], name='RSI', line=dict(color='#8A2BE2')), row=2, col=1)
    fig.update_layout(template='plotly_dark', height=750, xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

except Exception:
    st.info("System scan in progress...")
