import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import hmac

# --- 1. SYSTEM CONFIG & SECURITY ---
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

# --- 2. SIDEBAR CONTROLS ---
with st.sidebar:
    st.markdown("<h2 style='color:#00ff00;'>📡 COMMAND CENTER</h2>", unsafe_allow_html=True)
    # The New Quick-Switch Buttons
    timeframe = st.radio("SELECT TIMEFRAME", ("1m", "5m"), horizontal=True, help="1m for entries, 5m for trend boss")
    st.divider()
    st.markdown("<h3 style='color:#00ff00;'>🛡️ OPERATOR SOP</h3>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.checkbox("Trend Matrix?"), st.checkbox("Near VWAP?"), st.checkbox("News Clear?"), st.checkbox("Risk Set?")
    if all([c1, c2, c3, c4]): st.success("✅ READY")
    else: st.warning("⚠️ STANDBY")

# --- 3. DATA ENGINE ---
@st.cache_data(ttl=60)
def get_master_data(tf):
    # If 5m, we need more days to calculate indicators correctly
    period = "1d" if tf == "1m" else "5d"
    df = yf.download("^DJI", period=period, interval=tf, progress=False)
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

df = get_master_data(timeframe)
sig = "BUY" if df['Trend'].iloc[-1] == 1 else "SELL"
sig_color = "#00ff00" if sig == "BUY" else "#ff4b4b"

# --- 4. STUDIO HEADER ---
st.markdown(f"""
    <div style="background-color:#0d1117; padding:25px; border-radius:15px; border:2px solid {sig_color}; text-align:center;">
        <h1 style="margin:0; color:white; font-size:35px; letter-spacing:2px;">👨🏾‍💻 PATRO AI | STUDIO</h1>
        <p style="margin:0; color:grey; font-size:12px;">VIEW: {timeframe.upper()} CHART | {sig} MODE</p>
    </div>
""", unsafe_allow_html=True)

# --- 5. 3-LAYER CHART ---
fig = make_subplots(rows=3, cols=1, shared_xaxes=True, row_heights=[0.6, 0.2, 0.2], vertical_spacing=0.03)
fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close']), row=1, col=1)
fig.add_trace(go.Scatter(x=df.index, y=df['EMA20'], name='EMA 20', line=dict(color='orange', width=1.2)), row=1, col=1)
fig.add_trace(go.Scatter(x=df.index, y=df['VWAP'], name='VWAP', line=dict(color='#00d4ff', width=2, dash='dash')), row=1, col=1)

# Tags
buys = df[df['Entry'] == 2]
fig.add_trace(go.Scatter(x=buys.index, y=buys['Low']*0.9998, mode='markers', marker=dict(color='#00ff00', size=12, symbol='triangle-up')), row=1, col=1)
sells = df[df['Entry'] == -2]
fig.add_trace(go.Scatter(x=sells.index, y=sells['High']*1.0002, mode='markers', marker=dict(color='#ff4b4b', size=12, symbol='triangle-down')), row=1, col=1)

# Volume & RSI
v_colors = ['#00ff00' if df['Close'].iloc[i] >= df['Open'].iloc[i] else '#ff4b4b' for i in range(len(df))]
fig.add_trace(go.Bar(x=df.index, y=df['Volume'], marker_color=v_colors), row=2, col=1)
fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], line=dict(color='#9b59b6')), row=3, col=1)

fig.update_layout(template='plotly_dark', height=800, xaxis_rangeslider_visible=False, showlegend=False)
st.plotly_chart(fig, use_container_width=True)
