import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import hmac
from datetime import datetime
import pytz

# --- 1. SECURITY ---
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

# --- 2. THE NEWS GUARD DATA ---
# This is a manual alert list for the upcoming high-impact week
news_events = [
    {"Time": "Mon 10:00 AM", "Event": "ISM Manufacturing PMI", "Impact": "🔥 HIGH"},
    {"Time": "Tue 10:00 AM", "Event": "Fed Williams Speech", "Impact": "Medium"},
    {"Time": "Wed 08:15 AM", "Event": "ADP Employment Change", "Impact": "🔥 HIGH"},
    {"Time": "Fri 08:30 AM", "Event": "Non-Farm Payrolls (NFP)", "Impact": "🔥🔥 CRITICAL"}
]

# --- 3. SIDEBAR & JOURNAL ---
with st.sidebar:
    st.markdown("<h2 style='color:#00ff00;'>🛠️ COMMAND</h2>", unsafe_allow_html=True)
    if st.button("🔄 REFRESH"): st.rerun()
    st.divider()
    
    # Risk Calculator
    bal = st.number_input("Balance ($)", value=1000)
    risk = st.slider("Risk (%)", 0.5, 5.0, 1.0)
    risk_usd = bal * (risk/100)
    st.warning(f"Max Risk: ${risk_usd:.2f}")
    
    st.divider()
    # Quick Journal
    st.subheader("📝 Trade Journal")
    note = st.text_input("Note (e.g. 'SMA Bounce')")
    if st.button("💾 SAVE TRADE LOG"):
        st.toast(f"Logged: {note} | Risk: ${risk_usd}", icon="✅")

# --- 4. DATA ENGINE ---
@st.cache_data(ttl=60)
def get_data():
    df = yf.download("^DJI", period="1d", interval="1m")
    df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
    df['SMA20'] = df['Close'].rolling(window=20).mean()
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    df['RSI'] = 100 - (100 / (1 + (gain / loss)))
    df['Trend'] = 0
    df.loc[df['Close'] > df['SMA20'], 'Trend'] = 1
    df.loc[df['Close'] < df['SMA20'], 'Trend'] = -1
    df['Entry'] = df['Trend'].diff()
    return df

# --- 5. MAIN DASHBOARD ---
df = get_data()
sig = "BUY" if df['Trend'].iloc[-1] == 1 else "SELL"
sig_c = "#00ff00" if sig == "BUY" else "#ff4b4b"

# Top Row: Title and News Guard
c1, c2 = st.columns([2, 1])
with c1:
    st.markdown(f"<h1 style='color:{sig_c};'>🛡️ PATRO AI PRO: {sig}</h1>", unsafe_allow_html=True)
with c2:
    st.markdown("### ⚠️ NEWS GUARD")
    for e in news_events:
        st.caption(f"**{e['Time']}** - {e['Event']} ({e['Impact']})")

st.divider()

# Chart and Metrics
m1, m2, m3 = st.columns(3)
m1.metric("US30 PRICE", f"${df['Close'].iloc[-1]:,.2f}")
m2.metric("CURRENT TREND", sig)
m3.metric("RSI (14)", f"{df['RSI'].iloc[-1]:.2f}")

# Chart
fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.7, 0.3], vertical_spacing=0.05)
fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='US30'), row=1, col=1)
fig.add_trace(go.Scatter(x=df.index, y=df['SMA20'], name='Trend', line=dict(color='orange')), row=1, col=1)

for i in range(1, len(df)):
    if df['Entry'].iloc[i] == 2:
        fig.add_annotation(x=df.index[i], y=df['Low'].iloc[i], text="BUY", bgcolor="green", font=dict(color="white"), row=1, col=1)
    elif df['Entry'].iloc[i] == -2:
        fig.add_annotation(x=df.index[i], y=df['High'].iloc[i], text="SELL", bgcolor="red", font=dict(color="white"), row=1, col=1)

fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], name='RSI', line=dict(color='purple')), row=2, col=1)
fig.update_layout(template='plotly_dark', height=700, xaxis_rangeslider_visible=False)
st.plotly_chart(fig, use_container_width=True)
