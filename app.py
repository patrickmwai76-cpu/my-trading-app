import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import hmac

# --- 1. SYSTEM CONFIG & SECURITY ---
st.set_page_config(page_title="PATRO AI PRO", layout="wide")

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
        st.button("INITIALIZE", on_click=credentials_entered, use_container_width=True)
    return False

if not check_password(): st.stop()

# --- 2. MARKET SELECTOR (SIDEBAR) ---
with st.sidebar:
    st.markdown("<h2 style='color:#00ff00;'>🌐 MARKET SELECT</h2>", unsafe_allow_html=True)
    market_options = {
        "🇺🇸 US30 (Dow Jones)": "^DJI",
        "₿ Bitcoin (24/7)": "BTC-USD",
        "💎 Ethereum (24/7)": "ETH-USD",
        "💶 EUR/USD (Forex)": "EURUSD=X",
        "🟡 GOLD": "GC=F"
    }
    selected_name = st.selectbox("Choose Asset", list(market_options.keys()))
    ticker = market_options[selected_name]

# --- 3. DATA ENGINE ---
@st.cache_data(ttl=60)
def get_master_data(symbol):
    df = yf.download(symbol, period="1d", interval="1m", progress=False)
    df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
    
    # Technicals
    df['TP'] = (df['High'] + df['Low'] + df['Close']) / 3
    df['PV'] = df['TP'] * df['Volume']
    df['VWAP'] = df['PV'].cumsum() / df['Volume'].cumsum()
    df['EMA20'] = df['Close'].ewm(span=20, adjust=False).mean()
    
    # RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    df['RSI'] = 100 - (100 / (1 + (gain / loss)))
    
    # Signals
    df['Trend'] = 0
    df.loc[df['Close'] > df['EMA20'], 'Trend'] = 1
    df.loc[df['Close'] < df['EMA20'], 'Trend'] = -1
    df['Entry'] = df['Trend'].diff()
    return df

df = get_master_data(ticker)
sig = "BUY" if df['Trend'].iloc[-1] == 1 else "SELL"
sig_color = "#00ff00" if sig == "BUY" else "#ff4b4b"

# --- 4. HEADER & CHART ---
st.markdown(f"""<div style="background-color:#1e2130; padding:15px; border-radius:10px; border-left: 10px solid {sig_color};">
    <h1 style="margin:0; color:#ffffff; font-size:28px;">🛡️ PATRO AI PRO <span style="color:{sig_color};">| {selected_name}</span></h1>
    </div>""", unsafe_allow_html=True)

fig = make_subplots(rows=3, cols=1, shared_xaxes=True, row_heights=[0.6, 0.2, 0.2], vertical_spacing=0.03)

# LAYER 1: Candles & Tags
fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='Price'), row=1, col=1)
fig.add_trace(go.Scatter(x=df.index, y=df['EMA20'], name='EMA 20', line=dict(color='orange', width=1.2)), row=1, col=1)
fig.add_trace(go.Scatter(x=df.index, y=df['VWAP'], name='VWAP', line=dict(color='#00d4ff', width=2, dash='dash')), row=1, col=1)

# Tags
buys = df[df['Entry'] == 2]
fig.add_trace(go.Scatter(x=buys.index, y=buys['Low']*0.9998, mode='markers+text', text="BUY", marker=dict(color='#00ff00', size=12, symbol='triangle-up')), row=1, col=1)
sells = df[df['Entry'] == -2]
fig.add_trace(go.Scatter(x=sells.index, y=sells['High']*1.0002, mode='markers+text', text="SELL", marker=dict(color='#ff4b4b', size=12, symbol='triangle-down')), row=1, col=1)

# LAYER 2: Volume
v_colors = ['#00ff00' if df['Close'].iloc[i] >= df['Open'].iloc[i] else '#ff4b4b' for i in range(len(df))]
fig.add_trace(go.Bar(x=df.index, y=df['Volume'], marker_color=v_colors), row=2, col=1)

# LAYER 3: RSI
fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], line=dict(color='#9b59b6')), row=3, col=1)
fig.add_hline(y=70, line_dash="dot", line_color="#ff4b4b", row=3, col=1)
fig.add_hline(y=30, line_dash="dot", line_color="#00ff00", row=3, col=1)

fig.update_layout(template='plotly_dark', height=800, xaxis_rangeslider_visible=False, showlegend=False)
st.plotly_chart(fig, use_container_width=True)

# --- 5. SOP (SIDEBAR) ---
with st.sidebar:
    st.divider()
    st.markdown("<h2 style='color:#00ff00;'>🛡️ OPERATOR SOP</h2>", unsafe_allow_html=True)
    c1 = st.checkbox("Trend Matrix Confluence?")
    c2 = st.checkbox("Price Action near VWAP?")
    c3 = st.checkbox("News Guard is CLEAR?")
    c4 = st.checkbox("Risk Management set?")
    if all([c1, c2, c3, c4]): st.success("✅ READY")
    else: st.warning("⚠️ STANDBY")
    
    if st.button("🔄 FULL REFRESH"):
        st.cache_data.clear()
        st.rerun()
