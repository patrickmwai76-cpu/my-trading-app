import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import hmac

# --- 1. SECURITY & BRANDING ---
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

st.set_page_config(page_title="PATRO AI PRO", layout="wide")
if not check_password(): st.stop()

# --- 2. MULTI-TIMEFRAME ENGINE ---
@st.cache_data(ttl=60)
def get_trend(ticker, interval):
    try:
        data = yf.download(ticker, period="2d", interval=interval, progress=False)
        data.columns = [col[0] if isinstance(col, tuple) else col for col in data.columns]
        sma = data['Close'].rolling(window=20).mean()
        return "UP" if data['Close'].iloc[-1] > sma.iloc[-1] else "DOWN"
    except: return "N/A"

@st.cache_data(ttl=60)
def get_main_data():
    df = yf.download("^DJI", period="1d", interval="1m", progress=False)
    df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
    df['EMA20'] = df['Close'].ewm(span=20, adjust=False).mean()
    return df

# Fetch Trends
t1 = get_trend("^DJI", "1m")
t5 = get_trend("^DJI", "5m")
t15 = get_trend("^DJI", "15m")
df = get_main_data()

# --- 3. SIDEBAR (TREND MATRIX) ---
with st.sidebar:
    st.markdown("<h2 style='color:#00ff00;'>📊 TREND MATRIX</h2>", unsafe_allow_html=True)
    for label, val in [("1 MIN", t1), ("5 MIN", t5), ("15 MIN", t15)]:
        color = "#00ff00" if val == "UP" else "#ff4b4b"
        st.markdown(f"""
            <div style='border:1px solid {color}; padding:10px; border-radius:5px; margin-bottom:10px;'>
                <p style='margin:0; font-size:12px; color:gray;'>{label}</p>
                <h3 style='margin:0; color:{color};'>{val}</h3>
            </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    if st.button("🔄 REFRESH SYSTEM"):
        st.cache_data.clear()
        st.rerun()

# --- 4. MAIN DASHBOARD ---
st.markdown("<h1 style='text-align:center; color:#00ff00; letter-spacing: 5px;'>PATRO AI PRO</h1>", unsafe_allow_html=True)

m1, m2, m3 = st.columns(3)
curr_sig = "BUY" if df['Close'].iloc[-1] > df['EMA20'].iloc[-1] else "SELL"
m1.metric("US30 PRICE", f"${df['Close'].iloc[-1]:,.2f}")
m2.metric("CURRENT SIGNAL", curr_sig)
m3.metric("EMA 20", f"{df['EMA20'].iloc[-1]:.2f}")

# --- 5. CHART & VOLUME ---
fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.8, 0.2])
# Candles
fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='US30'), row=1, col=1)
# EMA
fig.add_trace(go.Scatter(x=df.index, y=df['EMA20'], name='EMA 20', line=dict(color='orange', width=1.5)), row=1, col=1)
# Volume
vol_colors = ['#00ff00' if df['Close'].iloc[i] > df['Open'].iloc[i] else '#ff4b4b' for i in range(len(df))]
fig.add_trace(go.Bar(x=df.index, y=df['Volume'], marker_color=vol_colors, name='Volume'), row=2, col=1)

fig.update_layout(template='plotly_dark', height=750, xaxis_rangeslider_visible=False, showlegend=False)
st.plotly_chart(fig, use_container_width=True)
