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

# --- 2. DATA ENGINES ---
@st.cache_data(ttl=60)
def get_master_data():
    df = yf.download("^DJI", period="1d", interval="1m", progress=False)
    df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
    
    # VWAP & Indicators
    df['TP'] = (df['High'] + df['Low'] + df['Close']) / 3
    df['VWAP'] = (df['TP'] * df['Volume']).cumsum() / df['Volume'].cumsum()
    df['EMA20'] = df['Close'].ewm(span=20, adjust=False).mean()
    
    # RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    df['RSI'] = 100 - (100 / (1 + (gain / loss)))
    
    # Logic
    df['Trend'] = 0
    df.loc[df['Close'] > df['EMA20'], 'Trend'] = 1
    df.loc[df['Close'] < df['EMA20'], 'Trend'] = -1
    df['Entry'] = df['Trend'].diff()
    return df

@st.cache_data(ttl=60)
def get_mtf(ticker, interval):
    data = yf.download(ticker, period="2d", interval=interval, progress=False)
    data.columns = [col[0] if isinstance(col, tuple) else col for col in data.columns]
    return "UP" if data['Close'].iloc[-1] > data['Close'].rolling(20).mean().iloc[-1] else "DOWN"

df = get_master_data()
t1, t5, t15 = get_mtf("^DJI", "1m"), get_mtf("^DJI", "5m"), get_mtf("^DJI", "15m")
sig_color = "#00ff00" if df['Trend'].iloc[-1] == 1 else "#ff4b4b"

# --- 3. UI LAYOUT ---
st.markdown(f'<div style="background-color:#1e2130; padding:15px; border-radius:10px; border-left: 10px solid {sig_color};"><h1 style="margin:0; color:#ffffff;">🛡️ PATRO AI PRO | {"BUY" if sig_color=="#00ff00" else "SELL"} MODE</h1></div>', unsafe_allow_html=True)

# NEWS GUARD
n1, n2 = st.columns(2)
n1.info("**Mon Mar 2** | ISM PMI (High Impact)")
n2.error("**Fri Mar 6** | NFP Jobs (CRITICAL)")

# --- 4. THE 3-STORY CHART (Price, Volume, RSI) ---
fig = make_subplots(rows=3, cols=1, shared_xaxes=True, 
                    row_heights=[0.6, 0.2, 0.2], vertical_spacing=0.03)

# ROW 1: PRICE + VWAP + EMA + BOX + TAGS
fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='US30'), row=1, col=1)
fig.add_trace(go.Scatter(x=df.index, y=df['VWAP'], name='VWAP', line=dict(color='#00d4ff', width=2, dash='dash')), row=1, col=1)
fig.add_trace(go.Scatter(x=df.index, y=df['EMA20'], name='EMA20', line=dict(color='orange', width=1)), row=1, col=1)

# Tags
buys = df[df['Entry'] == 2]
fig.add_trace(go.Scatter(x=buys.index, y=buys['Low']*0.9998, mode='markers+text', text="BUY", marker=dict(color='#00ff00', size=10, symbol='triangle-up')), row=1, col=1)
sells = df[df['Entry'] == -2]
fig.add_trace(go.Scatter(x=sells.index, y=sells['High']*1.0002, mode='markers+text', text="SELL", marker=dict(color='#ff4b4b', size=10, symbol='triangle-down')), row=1, col=1)

# ROW 2: VOLUME BARS
colors = ['#00ff00' if c >= o else '#ff4b4b' for c, o in zip(df['Close'], df['Open'])]
fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name='Volume', marker_color=colors), row=2, col=1)

# ROW 3: RSI
fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], name='RSI', line=dict(color='#9b59b6')), row=3, col=1)
fig.add_hline(y=70, line_dash="dot", line_color="#ff4b4b", row=3, col=1)
fig.add_hline(y=30, line_dash="dot", line_color="#00ff00", row=3, col=1)

fig.update_layout(template='plotly_dark', height=850, xaxis_rangeslider_visible=False, showlegend=False)
st.plotly_chart(fig, use_container_width=True)

# --- 5. SIDEBAR ---
with st.sidebar:
    st.markdown("<h2 style='color:#00ff00;'>🛡️ OPERATOR SOP</h2>", unsafe_allow_html=True)
    c1 = st.checkbox("Trend Matrix Confluence?")
    c2 = st.checkbox("High Volume on Entry?")
    c3 = st.checkbox("News Guard Clear?")
    if all([c1, c2, c3]): st.success("✅ PROTOCOL CLEARED")
    
    st.divider()
    st.markdown("### 📊 TREND MATRIX")
    for l, v in [("1M", t1), ("5M", t5), ("15M", t15)]:
        cc = "#00ff00" if v == "UP" else "#ff4b4b"
        st.markdown(f"<div style='border:1px solid {cc}; padding:5px; color:{cc};'><strong>{l}: {v}</strong></div>", unsafe_allow_html=True)
    
    if st.button("🔄 REFRESH"): st.rerun()
