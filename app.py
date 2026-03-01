import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import base64

# --- 1. SETUP & THEME ---
st.set_page_config(page_title="PATRO AI PRO", layout="wide")

# --- 2. ADVANCED STUDIO HEADER (The Visual Part) ---
# We use a professional trading floor image to create the "Studio" look
studio_img = "https://images.unsplash.com/photo-1611974714024-46274452140e?q=80&w=2070&auto=format&fit=crop"

st.markdown(f"""
    <style>
    .studio-container {{
        background: linear-gradient(rgba(0,0,0,0.8), rgba(0,0,0,0.8)), url('{studio_img}');
        background-size: cover;
        background-position: center;
        padding: 60px;
        border-radius: 25px;
        border: 2px solid #00ff00;
        text-align: center;
        box-shadow: 0 20px 50px rgba(0,0,0,0.7);
    }}
    .studio-text {{
        color: white;
        font-family: 'Courier New', monospace;
        font-weight: 900;
        font-size: 50px;
        letter-spacing: 10px;
        margin: 0;
        text-shadow: 0 0 20px #00ff00;
    }}
    .operator-tag {{
        color: #00ff00;
        font-size: 16px;
        letter-spacing: 5px;
        font-weight: bold;
    }}
    </style>
    <div class="studio-container">
        <h1 class="studio-text">PATRO AI PRO</h1>
        <p class="operator-tag">SYSTEM OPERATOR: ONLINE</p>
    </div>
""", unsafe_allow_html=True)

# --- 3. DATA ENGINE (US30) ---
@st.cache_data(ttl=60)
def get_data():
    df = yf.download("^DJI", period="1d", interval="1m", progress=False)
    df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
    df['EMA20'] = df['Close'].ewm(span=20, adjust=False).mean()
    df['TP'] = (df['High'] + df['Low'] + df['Close']) / 3
    df['VWAP'] = (df['TP'] * df['Volume']).cumsum() / df['Volume'].cumsum()
    # RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    df['RSI'] = 100 - (100 / (1 + (gain / loss)))
    return df

df = get_data()

# --- 4. 3-LAYER COMMAND CHART ---
st.markdown("### 📊 LIVE US30 COMMAND FEED")
fig = make_subplots(rows=3, cols=1, shared_xaxes=True, row_heights=[0.6, 0.2, 0.2], vertical_spacing=0.03)

# Row 1: Price
fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close']), row=1, col=1)
fig.add_trace(go.Scatter(x=df.index, y=df['VWAP'], name='VWAP', line=dict(color='#00d4ff', dash='dash')), row=1, col=1)

# Row 2: Volume
v_colors = ['#00ff00' if df['Close'].iloc[i] >= df['Open'].iloc[i] else '#ff4b4b' for i in range(len(df))]
fig.add_trace(go.Bar(x=df.index, y=df['Volume'], marker_color=v_colors), row=2, col=1)

# Row 3: RSI
fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], line=dict(color='#9b59b6')), row=3, col=1)
fig.add_hline(y=70, line_dash="dot", line_color="red", row=3, col=1)
fig.add_hline(y=30, line_dash="dot", line_color="green", row=3, col=1)

fig.update_layout(template='plotly_dark', height=800, xaxis_rangeslider_visible=False, showlegend=False)
st.plotly_chart(fig, use_container_width=True)
