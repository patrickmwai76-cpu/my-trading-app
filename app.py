import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- 1. TERMINAL CONFIG & THEME ---
st.set_page_config(page_title="US30 AI Ultimate Terminal", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.3; } 100% { opacity: 1; } }
    .live-dot { height: 12px; width: 12px; background-color: #00ff00; border-radius: 50%; display: inline-block; animation: pulse 1.5s infinite; margin-right: 10px; }
    div[data-testid="stMetric"] { background-color: #1e2130; padding: 15px; border-radius: 10px; border-left: 5px solid #00ff00; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SIDEBAR (Risk & Controls) ---
with st.sidebar:
    st.header("🏢 CONTROL PANEL")
    if st.button("🔄 FORCE REFRESH"):
        st.cache_data.clear()
        st.rerun()
    
    st.divider()
    st.subheader("💰 Risk Calculator")
    balance = st.number_input("Account Balance ($)", value=1000, step=100)
    risk_pct = st.slider("Risk Per Trade (%)", 0.5, 5.0, 1.0, 0.5)
    risk_amt = balance * (risk_pct / 100)
    st.success(f"Risk Amount: **${risk_amt:.2f}**")
    
    st.divider()
    st.info("Interval: 1 Minute\nTicker: US30 (Dow Jones)")

# --- 3. DATA ENGINE (The Ultimate Feed) ---
@st.cache_data(ttl=60)
def get_ultimate_data():
    # Fetch Data
    df = yf.download("^DJI", period="1d", interval="1m")
    df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
    
    # 1. Trend SMA
    df['SMA20'] = df['Close'].rolling(window=20).mean()
    
    # 2. RSI Momentum
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    df['RSI'] = 100 - (100 / (1 + (gain / loss)))
    
    # 3. Daily High/Low "Walls"
    day_h = df['High'].max()
    day_l = df['Low'].min()
    
    # 4. Entry Signal Logic (Cross-only)
    df['Trend'] = 0
    df.loc[df['Close'] > df['SMA20'], 'Trend'] = 1
    df.loc[df['Close'] < df['SMA20'], 'Trend'] = -1
    df['Entry'] = df['Trend'].diff()
    
    return df, day_h, day_l

# --- 4. MAIN INTERFACE ---
try:
    df, day_high, day_low = get_ultimate_data()
    curr_p = df['Close'].iloc[-1]
    curr_rsi = df['RSI'].iloc[-1]
    status = "BUY" if df['Trend'].iloc[-1] == 1 else "SELL"

    st.markdown(f'## <span class="live-dot"></span> US30 AI ULTIMATE TERMINAL: {status}', unsafe_allow_html=True)

    # Metrics
    m1, m2, m3 = st.columns(3)
    m1.metric("US30 PRICE", f"${curr_p:,.2f}")
    m2.metric("CURRENT TREND", status)
    m3.metric("RSI MOMENTUM", f"{curr_rsi:.2f}")

    # --- 5. THE DUAL-FLOOR DASHBOARD ---
    # Top 70% for Candles, Bottom 30% for Volume & RSI
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                        vertical_spacing=0.04, row_heights=[0.7, 0.3])

    # ROW 1: Price, SMA, and High/Low Walls
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='US30'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA20'], name='SMA 20', line=dict(color='orange', width=1.5)), row=1, col=1)
    
    # Add Support/Resistance Lines
    fig.add_hline(y=day_high, line_dash="dash", line_color="cyan", annotation_text="Daily High", row=1, col=1)
    fig.add_hline(y=day_low, line_dash="dash", line_color="red", annotation_text="Daily Low", row=1, col=1)

    # ROW 2: RSI Momentum Line & Volume Bars
    fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], name='RSI', line=dict(color='#8A2BE2', width=2)), row=2, col=1)
    fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name='Volume', marker_color='rgba(100, 100, 100, 0.3)'), row=2, col=1)
    
    # RSI Boundary Lines
    fig.add_hline(y=70, line_dash="dot", line_color="red", row=2, col=1)
    fig.add_hline(y=30, line_dash="dot", line_color="green", row=2, col=1)

    # --- 6. ADD ENTRY LABELS (At Trend Cross Only) ---
    for i in range(1, len(df)):
        if df['Entry'].iloc[i] == 2: # Crossed to BUY
            fig.add_annotation(x=df.index[i], y=df['Low'].iloc[i], text="BUY ENTRY", bgcolor="green", font=dict(color="white"), ay=30, row=1, col=1)
        elif df['Entry'].iloc[i] == -2: # Crossed to SELL
            fig.add_annotation(x=df.index[i], y=df['High'].iloc[i], text="SELL ENTRY", bgcolor="red", font=dict(color="white"), ay=-30, row=1, col=1)

    # --- 7. DASHBOARD STYLING ---
    fig.update_layout(template='plotly_dark', height=850, xaxis_rangeslider_visible=False, margin=dict(l=10, r=10, t=10, b=10))
    fig.update_xaxes(tickformat="%H:%M", tickfont=dict(color='gray'))

    st.plotly_chart(fig, use_container_width=True)

    # Bottom Alert Box
    if status == "BUY":
        st.success(f"🚀 AI ANALYSIS: Market is Bullish above SMA. Watch Daily High at ${day_high:,.2f}")
    else:
        st.error(f"📉 AI ANALYSIS: Market is Bearish below SMA. Watch Daily Low at ${day_low:,.2f}")

except Exception as e:
    st.warning("Market stream initializing... Please wait 10 seconds.")
