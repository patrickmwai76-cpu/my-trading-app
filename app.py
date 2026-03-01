import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import hmac
from datetime import datetime
import pytz

# --- 1. SETUP ---
st.set_page_config(page_title="PATRO AI PRO", layout="wide")

# --- 2. THE INSTITUTIONAL DATA ENGINE ---
@st.cache_data(ttl=60)
def get_institutional_data():
    # Fetch 1m data for the current day
    df = yf.download("^DJI", period="1d", interval="1m", progress=False)
    df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
    
    # VWAP Calculation
    # VWAP = Cumulative (Price * Volume) / Cumulative Volume
    df['Typical_Price'] = (df['High'] + df['Low'] + df['Close']) / 3
    df['Price_Vol'] = df['Typical_Price'] * df['Volume']
    df['VWAP'] = df['Price_Vol'].cumsum() / df['Volume'].cumsum()
    
    # EMA 20 & RSI
    df['EMA20'] = df['Close'].ewm(span=20, adjust=False).mean()
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    df['RSI'] = 100 - (100 / (1 + (gain / loss)))
    
    # Trend & Signals
    df['Trend'] = 0
    df.loc[df['Close'] > df['EMA20'], 'Trend'] = 1
    df.loc[df['Close'] < df['EMA20'], 'Trend'] = -1
    df['Entry'] = df['Trend'].diff()
    return df

df = get_institutional_data()
sig = "BUY" if df['Trend'].iloc[-1] == 1 else "SELL"
sig_color = "#00ff00" if sig == "BUY" else "#ff4b4b"

# --- 3. HEADER & NEWS ---
st.markdown(f"""
    <div style="background-color:#1e2130; padding:15px; border-radius:10px; border-left: 10px solid {sig_color};">
        <h1 style="margin:0; color:#ffffff; font-size:28px;">🛡️ PATRO AI PRO <span style="color:{sig_color};">| INSTITUTIONAL TERMINAL</span></h1>
    </div>
""", unsafe_allow_html=True)

# --- 4. THE CHART (WITH VWAP & SESSION BOX) ---
fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.8, 0.2], vertical_spacing=0.03)

# Candlesticks
fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='US30'), row=1, col=1)

# Institutional Lines
fig.add_trace(go.Scatter(x=df.index, y=df['EMA20'], name='EMA 20', line=dict(color='orange', width=1)), row=1, col=1)
fig.add_trace(go.Scatter(x=df.index, y=df['VWAP'], name='VWAP (Fair Value)', line=dict(color='#00d4ff', width=2, dash='dash')), row=1, col=1)

# NY Session Opening Range Box (9:30 - 10:30 EST)
# We find the min/max price during that window
ny_start = df.index[df.index.time >= datetime.strptime("09:30", "%H:%M").time()]
ny_end = ny_start[ny_start.time <= datetime.strptime("10:30", "%H:%M").time()]

if not ny_end.empty:
    box_min = df.loc[ny_end, 'Low'].min()
    box_max = df.loc[ny_end, 'High'].max()
    fig.add_vrect(x0=ny_end[0], x1=ny_end[-1], fillcolor="rgba(255, 255, 255, 0.1)", line_width=0, layer="below", row=1, col=1)
    # Add labels for the session box
    st.sidebar.info(f"NY Open Range: {box_min:,.0f} - {box_max:,.0f}")

# Signals
buys = df[df['Entry'] == 2]
fig.add_trace(go.Scatter(x=buys.index, y=buys['Low']*0.9998, mode='markers+text', text="BUY", marker=dict(color='#00ff00', size=12, symbol='triangle-up')), row=1, col=1)
sells = df[df['Entry'] == -2]
fig.add_trace(go.Scatter(x=sells.index, y=sells['High']*1.0002, mode='markers+text', text="SELL", marker=dict(color='#ff4b4b', size=12, symbol='triangle-down')), row=1, col=1)

# RSI
fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], name='RSI', line=dict(color='#9b59b6')), row=2, col=1)
fig.update_layout(template='plotly_dark', height=700, xaxis_rangeslider_visible=False, showlegend=False)

st.plotly_chart(fig, use_container_width=True)

# --- 5. SIDEBAR SOP ---
with st.sidebar:
    st.markdown("<h2 style='color:#00ff00;'>🛡️ PRO PROTOCOL</h2>", unsafe_allow_html=True)
    st.checkbox("Price near VWAP? (Don't buy overextended)")
    st.checkbox("Price broke NY Session Box?")
    st.checkbox("RSI Confluence?")
    st.divider()
    st.metric("VWAP DISTANCE", f"{df['Close'].iloc[-1] - df['VWAP'].iloc[-1]:.2f}")
    if st.button("REFRESH"): st.rerun()
