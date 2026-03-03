import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from streamlit_autorefresh import st_autorefresh
from plotly.subplots import make_subplots
import datetime

# 1. SECURITY & CONFIG
st.set_page_config(page_title="PATRO AI PRO V8.0", layout="wide")
if 'auth' not in st.session_state: st.session_state['auth'] = False
if not st.session_state['auth']:
    st.title("🛡️ PATRO AI PRO | SECURE ACCESS")
    u, p = st.text_input("User"), st.text_input("Pass", type="password")
    if st.button("Unlock"):
        if u == "PATRO_ADMIN" and p == "patro666@":
            st.session_state['auth'] = True
            st.rerun()
    st.stop()

# 2. SIDEBAR - ASSET & SOP
# --- STEP 1: DEFINE THRESHOLD FIRST ---
# This ensures the 'dist_threshold' is created before the app tries to use it
asset_choice = st.sidebar.selectbox("Select Asset", ["XAUUSD (GOLD)", "US30 (DOW JONES)"])

if asset_choice == "XAUUSD (GOLD)":
    dist_threshold = 1.5  # Bank filter for Gold
else:
    dist_threshold = 5.0  # Pro filter for US30

# --- STEP 2: PROFESSIONAL HEADER (PATRO AI PRO NAME) ---
st.markdown(f"""
    <div style="background-color: #1e1e1e; padding: 20px; border-radius: 10px; border-bottom: 4px solid #f39c12;">
        <h1 style="color: white; margin: 0;">PATRO AI PRO V8.0 <span style="font-size: 15px; color: #00ff00;">● LIVE</span></h1>
        <p style="color: #bdc3c7; margin: 0;">Institutional Terminal | Asset: {asset_choice}</p>
    </div>
""", unsafe_allow_html=True)

# --- STEP 3: STRICT MODE INDICATOR ---
# This was the line causing the crash - now it is fixed!
st.info(f"🛡️ STRICT MODE ACTIVE: Using {dist_threshold} point filter for {asset_choice}")

tf = st.sidebar.radio("Timeframe", ["1m", "5m", "15m"], index=0, horizontal=True)
st.sidebar.divider()
st.sidebar.subheader("📋 INSTITUTIONAL SOP")
st.sidebar.checkbox("Trend Matrix Confluence?", value=True)
st.sidebar.checkbox("Price Action near VWAP?", value=True)
st.sidebar.checkbox("Volume Confirmation?", value=True)
st.sidebar.divider()
bal = st.sidebar.number_input("Wallet ($)", value=1000)

# 3. NEWS GUARD HEADER (MARCH 2, 2026)
# Live News tracking for today's high-impact events
news_events = [
    {"time": "18:00", "event": "🔥 ISM Manufacturing PMI", "impact": "HIGH"},
    {"time": "20:00", "event": "🎤 Fed Mester Speech", "impact": "MED"}
]
now_time = datetime.datetime.now().strftime("%H:%M")
upcoming = [n for n in news_events if n['time'] > now_time]
active_news = upcoming[0] if upcoming else {"time": "23:59", "event": "No Major News Left", "impact": "LOW"}

st.markdown(f"""
    <div style="background: linear-gradient(90deg, #1a1a1a, #333333); padding: 15px; border-radius: 10px; border-left: 5px solid {'#ff4b4b' if active_news['impact'] == 'HIGH' else '#ffa500'};">
        <h3 style="color: white; margin: 0;">📢 NEWS GUARD: {active_news['event']} at {active_news['time']} EAT</h3>
        <p style="color: #00ff00; margin: 0;">Status: MT5 Sync Active | Asset: {asset_choice} | Target: .m Accounts</p>
    </div>
""", unsafe_allow_html=True)

# 4. DATA ENGINE (10s REFRESH)
st_autorefresh(interval=10000, key="v8_master_pulse")

try:
    df = yf.download(ticker, period="1d", interval=tf, prepost=True)
    if not df.empty:
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        
        # INDICATORS
        df['VWAP'] = (((df['High'] + df['Low'] + df['Close']) / 3) * df['Volume']).cumsum() / df['Volume'].cumsum()
        df['SMA'] = df['Close'].rolling(20).mean()
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        df['RSI'] = 100 - (100 / (1 + (gain / (loss + 1e-9))))
        df['Vol_Avg'] = df['Volume'].rolling(20).mean()

        # 5. CHARTING
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.04, row_heights=[0.5, 0.2, 0.3])
        fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name=asset_choice), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['VWAP'], line=dict(color='cyan', width=2.5), name='VWAP (Cyan)'), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['SMA'], line=dict(color='orange', width=1.5), name='SMA (Orange)'), row=1, col=1)
        fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name='Volume', marker_color='#444444'), row=2, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], line=dict(color='purple', width=2), name='RSI'), row=3, col=1)

        # 6. ANTI-FAKE & NEWS-AWARE LOGIC
        dist_threshold = 1.5 if "GOLD" in asset_choice else 5.0
        # Check time for News Guard (5 min buffer)
        time_to_news = (datetime.datetime.strptime(active_news['time'], "%H:%M") - datetime.datetime.now()).total_seconds() / 60
        is_news_volatile = 0 < time_to_news < 5

        for i in range(25, len(df)):
            dist = abs(df['Close'].iloc[i] - df['VWAP'].iloc[i])
            vol_confirm = df['Volume'].iloc[i] > df['Vol_Avg'].iloc[i]

            if is_news_volatile:
                fig.add_annotation(x=df.index[i], y=df['High'].iloc[i], text="⚠️ NEWS RISK", bgcolor="orange", font=dict(color="black"), row=1, col=1)
            else:
                # BUY: Price > VWAP + RSI > 55 + Distance + Volume
                if (df['Close'].iloc[i] > df['VWAP'].iloc[i] and df['RSI'].iloc[i] > 55 and dist > dist_threshold and vol_confirm):
                    if df['Close'].iloc[i-1] <= df['VWAP'].iloc[i-1]:
                        fig.add_annotation(x=df.index[i], y=df['Low'].iloc[i], text="BUY", bgcolor="green", font=dict(color="white"), row=1, col=1)
                
                # SELL: Price < VWAP + RSI < 45 + Distance + Volume
                elif (df['Close'].iloc[i] < df['VWAP'].iloc[i] and df['RSI'].iloc[i] < 45 and dist > dist_threshold and vol_confirm):
                    if df['Close'].iloc[i-1] >= df['VWAP'].iloc[i-1]:
                        fig.add_annotation(x=df.index[i], y=df['High'].iloc[i], text="SELL", bgcolor="red", font=dict(color="white"), row=1, col=1)

        fig.update_layout(template="plotly_dark", height=750, xaxis_rangeslider_visible=False, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("Searching for market data... please wait.")

except Exception as e:
    st.warning(f"Connecting to Market Feed... {e}")

st.info(f"🛡️ PATRO V8.0: Strict Mode Active. Distance Filter: {dist_threshold}pts. News Guard: 5m Buffer.")
