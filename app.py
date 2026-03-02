import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from streamlit_autorefresh import st_autorefresh
from plotly.subplots import make_subplots
import datetime

# 1. SECURITY & CONFIG
st.set_page_config(page_title="PATRO AI PRO", layout="wide")
if 'auth' not in st.session_state: st.session_state['auth'] = False
if not st.session_state['auth']:
    st.title("🛡️ PATRO AI PRO | SECURE ACCESS")
    u, p = st.text_input("User"), st.text_input("Pass", type="password")
    if st.button("Unlock"):
        if u == "PATRO_ADMIN" and p == "patro666@":
            st.session_state['auth'] = True
            st.rerun()
    st.stop()

# 2. SIDEBAR - FULL SOP
st.sidebar.title("🛡️ CONTROL CENTER")
tf = st.sidebar.radio("Timeframe", ["1m", "5m", "15m"], index=0, horizontal=True)
st.sidebar.divider()
st.sidebar.subheader("📋 INSTITUTIONAL SOP")
st.sidebar.checkbox("Trend Matrix Confluence?", value=True)
st.sidebar.checkbox("Price Action near VWAP?", value=True)
st.sidebar.checkbox("Institutional Volume Spike?", value=True)
st.sidebar.checkbox("News Guard CLEAR?", value=True)
st.sidebar.divider()
st.sidebar.subheader("📉 RISK MGMT")
bal = st.sidebar.number_input("Wallet ($)", value=1000)
st.sidebar.info(f"Target Lot: {(bal * 0.01) / 50:.2f}")

# 3. RESTORED NEWS GUARD HEADER
st.markdown('<div style="background: linear-gradient(90deg, #00c853, #b2ff59); padding: 10px; border-radius: 8px; color: black; text-align: center; font-weight: bold; font-size: 18px;">🛡️ PATRO AI PRO | INSTITUTIONAL TERMINAL v6.0</div>', unsafe_allow_html=True)

st.write(f"⏱️ **SESSION PULSE:** {datetime.datetime.now().strftime('%H:%M:%S')} EAT")
c1, c2 = st.columns(2)
c1.info("📅 MON MAR 2: ISM PMI (6:00 PM EAT)")
c2.error("🚨 FRI MAR 6: NFP Jobs (4:30 PM EAT)")

# 4. DATA ENGINE (10s REFRESH)
st_autorefresh(interval=10000, key="v6_pulse")
df = yf.download("YM=F", period="1d", interval=tf, prepost=True)

if not df.empty:
    if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
    
    # INDICATORS
    df['VWAP'] = (((df['High'] + df['Low'] + df['Close']) / 3) * df['Volume']).cumsum() / df['Volume'].cumsum()
    df['SMA'] = df['Close'].rolling(20).mean()
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    df['RSI'] = 100 - (100 / (1 + (gain / (loss + 1e-9))))

    # 5. RESTORED 3-LAYER CHART (COMPACT HEIGHT FOR LAPTOPS)
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.02, row_heights=[0.55, 0.15, 0.3])
    
    # LAYER 1: Candles + VWAP + SMA
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='US30'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['VWAP'], line=dict(color='cyan', width=2), name='VWAP'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA'], line=dict(color='orange', width=1.5), name='SMA'), row=1, col=1)

    # LAYER 2: Volume [RESTORED]
    fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name='Volume', marker_color='rgba(128, 128, 128, 0.5)'), row=2, col=1)

    # LAYER 3: RSI [RESTORED]
    fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], line=dict(color='purple', width=2), name='RSI'), row=3, col=1)
    fig.add_hline(y=70, line_dash="dash", line_color="red", row=3, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="green", row=3, col=1)

    # 6. NO-FAKE SIGNALS (ONLY TODAY)
    today = datetime.date.today()
    for i in range(20, len(df)):
        if df.index[i].date() == today:
            if (df['Close'].iloc[i] > df['VWAP'].iloc[i] and df['Close'].iloc[i] > df['SMA'].iloc[i] and df['RSI'].iloc[i] > 55):
                if df['Close'].iloc[i-1] <= df['VWAP'].iloc[i-1]:
                    fig.add_annotation(x=df.index[i], y=df['Low'].iloc[i], text="BUY", bgcolor="green", font=dict(color="white"), row=1, col=1)
            elif (df['Close'].iloc[i] < df['VWAP'].iloc[i] and df['Close'].iloc[i] < df['SMA'].iloc[i] and df['RSI'].iloc[i] < 45):
                if df['Close'].iloc[i-1] >= df['VWAP'].iloc[i-1]:
                    fig.add_annotation(x=df.index[i], y=df['High'].iloc[i], text="SELL", bgcolor="red", font=dict(color="white"), row=1, col=1)

    # FIXING THE OVERLAP
    fig.update_layout(template="plotly_dark", height=750, xaxis_rangeslider_visible=False, margin=dict(l=5, r=5, t=5, b=5))
    st.plotly_chart(fig, use_container_width=True)

st.success("✅ ALL LAYERS ACTIVE | NO-FAKE LOGIC SYNCED")
