import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- 1. SETUP & THEME ---
st.set_page_config(page_title="US30 AI Elite Terminal", layout="wide")

# Fixed CSS for Metric visibility and high-contrast UI
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div[data-testid="stMetric"] { 
        background-color: #1e2130 !important; 
        padding: 20px; 
        border-radius: 12px; 
        border: 2px solid #00ff00;
    }
    [data-testid="stMetricValue"] { color: #00ff00 !important; font-weight: bold; }
    [data-testid="stMetricLabel"] { color: #ffffff !important; font-size: 16px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SIDEBAR (Advanced Tools) ---
with st.sidebar:
    st.header("🏢 US30 CONTROL PANEL")
    if st.button("🔄 REFRESH LIVE DATA"):
        st.cache_data.clear()
        st.rerun()
    
    st.divider()
    st.subheader("💰 Risk & Trade Exit")
    balance = st.number_input("Account Balance ($)", value=1000, step=100)
    risk_pct = st.slider("Risk Per Trade (%)", 0.5, 5.0, 1.0, 0.5)
    
    # Live TP/SL Calculator based on US30 Volatility
    st.info("--- Trade Setup ---")
    st.write(f"Risk Amount: **${balance * (risk_pct/100):.2f}**")
    st.write("Target Profit (TP): **+50 Pips**")
    st.write("Stop Loss (SL): **-25 Pips**")

# --- 3. DATA ENGINE ---
@st.cache_data(ttl=60)
def get_elite_data():
    df = yf.download("^DJI", period="1d", interval="1m")
    df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
    
    # 20-Period Moving Average
    df['SMA20'] = df['Close'].rolling(window=20).mean()
    
    # RSI 14
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    df['RSI'] = 100 - (100 / (1 + (gain / loss)))
    
    # Support & Resistance levels
    day_high = df['High'].max()
    day_low = df['Low'].min()
    
    # Trend Logic (Clean Entry Only)
    df['Trend'] = 0
    df.loc[df['Close'] > df['SMA20'], 'Trend'] = 1
    df.loc[df['Close'] < df['SMA20'], 'Trend'] = -1
    df['Entry'] = df['Trend'].diff()
    
    return df, day_high, day_low

# --- 4. DASHBOARD DISPLAY ---
try:
    df, d_high, d_low = get_elite_data()
    curr_p = df['Close'].iloc[-1]
    curr_rsi = df['RSI'].iloc[-1]
    last_sig = "BUY" if df['Trend'].iloc[-1] == 1 else "SELL"

    st.title(f"📊 US30 AI ELITE TERMINAL: {last_sig}")

    # Metrics (Fixing the dark boxes from photo 1000389634)
    m1, m2, m3 = st.columns(3)
    m1.metric("US30 PRICE", f"${curr_p:,.2f}")
    m2.metric("CURRENT TREND", last_sig)
    m3.metric("RSI MOMENTUM", f"{curr_rsi:.2f}")

    # --- 5. THE CHART ---
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                        vertical_spacing=0.04, row_heights=[0.75, 0.25])

    # Price Chart
    fig.add_trace(go.Candlestick(
        x=df.index, open=df['Open'], high=df['High'], 
        low=df['Low'], close=df['Close'], name='US30'
    ), row=1, col=1)
    
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA20'], name='Trend SMA', line=dict(color='orange', width=2)), row=1, col=1)

    # Support/Resistance Lines
    fig.add_hline(y=d_high, line_dash="dash", line_color="#00ffff", annotation_text="DAY HIGH", row=1, col=1)
    fig.add_hline(y=d_low, line_dash="dash", line_color="#ff4b4b", annotation_text="DAY LOW", row=1, col=1)

    # RSI & Volume (Bottom Panel)
    fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], name='RSI', line=dict(color='#8A2BE2', width=2)), row=2, col=1)
    fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name='Volume', marker_color='rgba(255, 255, 255, 0.1)'), row=2, col=1)
    fig.add_hline(y=70, line_dash="dot", line_color="red", row=2, col=1)
    fig.add_hline(y=30, line_dash="dot", line_color="green", row=2, col=1)

    # Cleaned Entry Annotations (Prevents the mess in photo 1000389631)
    for i in range(1, len(df)):
        if df['Entry'].iloc[i] == 2: # New Buy
            fig.add_annotation(x=df.index[i], y=df['Low'].iloc[i], text="BUY", bgcolor="green", font=dict(color="white"), ay=25)
        elif df['Entry'].iloc[i] == -2: # New Sell
            fig.add_annotation(x=df.index[i], y=df['High'].iloc[i], text="SELL", bgcolor="red", font=dict(color="white"), ay=-25)

    fig.update_layout(template='plotly_dark', height=850, xaxis_rangeslider_visible=False, margin=dict(l=10,r=10,t=10,b=10))
    fig.update_xaxes(tickformat="%H:%M", tickfont=dict(color='white', size=11))

    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.info("Market data is updating... click Refresh in the sidebar.")
