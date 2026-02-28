import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- 1. SETUP & THEME ---
st.set_page_config(page_title="US30 AI Pro Terminal", layout="wide")

# Custom CSS to fix the metric cards and the pulse
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.3; } 100% { opacity: 1; } }
    .live-dot { height: 12px; width: 12px; background-color: #00ff00; border-radius: 50%; display: inline-block; animation: pulse 1.5s infinite; margin-right: 10px; }
    div[data-testid="stMetric"] { background-color: #1e2130; padding: 10px; border-radius: 10px; border: 1px solid #30363d; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SIDEBAR (Calculator & Tools) ---
with st.sidebar:
    st.header("🛠️ Trading Tools")
    if st.button("🔄 REFRESH TERMINAL"):
        st.cache_data.clear()
        st.rerun()
    
    st.divider()
    st.subheader("💰 Risk Calculator")
    balance = st.number_input("Account Balance ($)", value=1000, step=100)
    risk_pct = st.slider("Risk Per Trade (%)", 0.5, 5.0, 1.0, 0.5)
    risk_amt = balance * (risk_pct / 100)
    st.success(f"Recommended Risk: **${risk_amt:.2f}**")

# --- 3. DATA ENGINE ---
@st.cache_data(ttl=60)
def get_terminal_data():
    # Fetch US30 (Dow Jones) 1-minute data
    df = yf.download("^DJI", period="1d", interval="1m")
    df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
    
    # SMA 20
    df['SMA20'] = df['Close'].rolling(window=20).mean()
    
    # RSI 14 (The Momentum Scale)
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # Signal Logic
    df['Signal'] = 0
    df.loc[df['Close'] > df['SMA20'], 'Signal'] = 1
    df.loc[df['Close'] < df['SMA20'], 'Signal'] = -1
    df['Entry'] = df['Signal'].diff()
    return df

# --- 4. MAIN DASHBOARD ---
try:
    df = get_terminal_data()
    curr_p = df['Close'].iloc[-1]
    curr_rsi = df['RSI'].iloc[-1]
    last_sig = "BUY" if df['Signal'].iloc[-1] == 1 else "SELL"

    st.markdown(f'## <span class="live-dot"></span> US30 AI LIVE TERMINAL: {last_sig}', unsafe_allow_html=True)

    # Metrics Row
    m1, m2, m3 = st.columns(3)
    m1.metric("US30 PRICE", f"${curr_p:,.2f}")
    m2.metric("SIGNAL", last_sig)
    m3.metric("RSI MOMENTUM", f"{curr_rsi:.2f}")

    # --- 5. THE DUAL-SCALE CHART (Stock + RSI) ---
    # Top floor (75%) for Candles, Bottom floor (25%) for RSI
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                        vertical_spacing=0.05, row_heights=[0.75, 0.25])

    # Price & Candles (Row 1)
    fig.add_trace(go.Candlestick(
        x=df.index, open=df['Open'], high=df['High'], 
        low=df['Low'], close=df['Close'], name='US30'
    ), row=1, col=1)
    
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA20'], name='SMA 20', line=dict(color='orange', width=1)), row=1, col=1)

    # RSI Graph (Row 2)
    fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], name='RSI Scale', line=dict(color='#8A2BE2', width=2)), row=2, col=1)
    # RSI levels
    fig.add_hline(y=70, line_dash="dot", line_color="red", row=2, col=1)
    fig.add_hline(y=30, line_dash="dot", line_color="green", row=2, col=1)

    # Add Buy/Sell Annotations like the video
    for i in range(1, len(df)):
        if df['Entry'].iloc[i] == 2:
            fig.add_annotation(x=df.index[i], y=df['Low'].iloc[i], text="BUY", bgcolor="green", font=dict(color="white"), ay=20, row=1, col=1)
        elif df['Entry'].iloc[i] == -2:
            fig.add_annotation(x=df.index[i], y=df['High'].iloc[i], text="SELL", bgcolor="red", font=dict(color="white"), ay=-20, row=1, col=1)

    # Fix the Minute Scale & Formatting
    fig.update_layout(
        template='plotly_dark', 
        height=800, 
        xaxis_rangeslider_visible=False,
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis2_title="Minute-by-Minute Time Scale"
    )
    
    # Ensure the minute labels are bright and clear
    fig.update_xaxes(showticklabels=True, tickfont=dict(size=12, color='white'))

    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.info("Terminal is booting up... Fetching the latest US30 candles.")
