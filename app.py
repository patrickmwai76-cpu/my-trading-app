import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- 1. SETUP & THEME ---
st.set_page_config(page_title="US30 AI Pro Terminal", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div[data-testid="stMetric"] { 
        background-color: #1e2130; 
        padding: 15px; 
        border-radius: 10px; 
        border-left: 5px solid #00ff00;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SIDEBAR (Risk & Controls) ---
with st.sidebar:
    st.header("🏢 US30 CONTROL PANEL")
    if st.button("🔄 REFRESH LIVE DATA"):
        st.cache_data.clear()
        st.rerun()
    
    st.divider()
    st.subheader("💰 Risk Calculator")
    balance = st.number_input("Account Balance ($)", value=1000, step=100)
    risk_pct = st.slider("Risk Per Trade (%)", 0.5, 5.0, 1.0, 0.5)
    risk_amt = balance * (risk_pct / 100)
    st.success(f"Risk Amount: **${risk_amt:.2f}**")
    st.info("Set your lot size based on this risk.")

# --- 3. DATA ENGINE ---
@st.cache_data(ttl=60)
def get_ultimate_data():
    df = yf.download("^DJI", period="1d", interval="1m")
    df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
    
    # Technicals
    df['SMA20'] = df['Close'].rolling(window=20).mean()
    
    # RSI 14
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    df['RSI'] = 100 - (100 / (1 + (gain / loss)))
    
    # Support & Resistance
    day_high = df['High'].max()
    day_low = df['Low'].min()
    
    # Signal Logic (Clean)
    df['Trend'] = 0
    df.loc[df['Close'] > df['SMA20'], 'Trend'] = 1
    df.loc[df['Close'] < df['SMA20'], 'Trend'] = -1
    df['Change'] = df['Trend'].diff()
    
    return df, day_high, day_low

# --- 4. MAIN DASHBOARD ---
try:
    df, d_high, d_low = get_ultimate_data()
    curr_p = df['Close'].iloc[-1]
    curr_rsi = df['RSI'].iloc[-1]
    current_sig = "BUY" if df['Trend'].iloc[-1] == 1 else "SELL"

    st.title(f"📊 US30 AI LIVE TERMINAL: {current_sig}")

    m1, m2, m3 = st.columns(3)
    m1.metric("US30 PRICE", f"${curr_p:,.2f}")
    m2.metric("CURRENT TREND", current_sig)
    m3.metric("RSI (14) MOMENTUM", f"{curr_rsi:.2f}")

    # --- 5. THE ULTIMATE CHART ---
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                        vertical_spacing=0.03, row_heights=[0.7, 0.3])

    # TOP: Price Candles, SMA, and High/Low Lines
    fig.add_trace(go.Candlestick(
        x=df.index, open=df['Open'], high=df['High'], 
        low=df['Low'], close=df['Close'], name='US30'
    ), row=1, col=1)
    
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA20'], name='Trend SMA', line=dict(color='orange', width=1.5)), row=1, col=1)
    
    # Add Support/Resistance Dashed Lines
    fig.add_hline(y=d_high, line_dash="dash", line_color="cyan", annotation_text="DAY HIGH", row=1, col=1)
    fig.add_hline(y=d_low, line_dash="dash", line_color="red", annotation_text="DAY LOW", row=1, col=1)

    # BOTTOM: RSI and Volume Bars
    fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], name='RSI', line=dict(color='#8A2BE2', width=2)), row=2, col=1)
    # Add subtle volume bars in the background of the RSI chart
    fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name='Volume', marker_color='rgba(100, 100, 100, 0.3)'), row=2, col=1)
    
    fig.add_hline(y=70, line_dash="dot", line_color="red", row=2, col=1)
    fig.add_hline(y=30, line_dash="dot", line_color="green", row=2, col=1)

    # "Clean" Entry Annotations
    for i in range(1, len(df)):
        if df['Change'].iloc[i] == 2: # BUY
            fig.add_annotation(x=df.index[i], y=df['Low'].iloc[i], text="BUY ENTRY", 
                               bgcolor="green", font=dict(color="white", size=10), ay=30, row=1, col=1)
        elif df['Change'].iloc[i] == -2: # SELL
            fig.add_annotation(x=df.index[i], y=df['High'].iloc[i], text="SELL ENTRY", 
                               bgcolor="red", font=dict(color="white", size=10), ay=-30, row=1, col=1)

    fig.update_layout(template='plotly_dark', height=850, xaxis_rangeslider_visible=False, margin=dict(l=10, r=10, t=10, b=10))
    fig.update_xaxes(tickformat="%H:%M", tickfont=dict(color='gray', size=11))

    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"Waiting for market data... {e}")
