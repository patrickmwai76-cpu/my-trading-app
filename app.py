import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- 1. SETUP & THEME (FIXED FOR DARK BOXES) ---
st.set_page_config(page_title="PATRO AI PRO | US30", layout="wide")

st.markdown("""
    <style>
    /* Force the background to be dark */
    .stApp { background-color: #0e1117; }
    
    /* FIX FOR DARK METRIC BOXES */
    [data-testid="stMetric"] {
        background-color: #161b22 !important; /* Deep charcoal background */
        border: 2px solid #00ff00 !important; /* Neon green border */
        border-radius: 10px !important;
        padding: 15px !important;
    }
    
    /* FIX FOR BLACK/DARK TEXT IN BOXES */
    [data-testid="stMetricValue"] {
        color: #00ff00 !important; /* Force neon green numbers */
        font-weight: bold !important;
    }
    [data-testid="stMetricLabel"] {
        color: #ffffff !important; /* Force white titles */
        font-size: 18px !important;
    }
    
    .title-text {
        font-size: 40px !important;
        font-weight: 800;
        color: #00ff00;
        text-shadow: 2px 2px 8px rgba(0, 255, 0, 0.4);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SIDEBAR ---
with st.sidebar:
    st.markdown("<h1 style='color: #00ff00;'>PATRO AI PRO</h1>", unsafe_allow_html=True)
    if st.button("🔄 REFRESH SYSTEM"):
        st.cache_data.clear()
        st.rerun()
    st.divider()
    balance = st.number_input("Balance ($)", value=1000)
    risk = st.slider("Risk (%)", 0.5, 5.0, 1.0)
    st.success(f"Risk Amount: ${balance * (risk/100):.2f}")

# --- 3. DATA ENGINE ---
@st.cache_data(ttl=60)
def get_patro_data():
    df = yf.download("^DJI", period="1d", interval="1m")
    df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
    
    df['SMA20'] = df['Close'].rolling(window=20).mean()
    
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    df['RSI'] = 100 - (100 / (1 + (gain / loss)))
    
    day_high, day_low = df['High'].max(), df['Low'].min()
    
    df['Trend'] = 0
    df.loc[df['Close'] > df['SMA20'], 'Trend'] = 1
    df.loc[df['Close'] < df['SMA20'], 'Trend'] = -1
    df['Entry'] = df['Trend'].diff()
    
    return df, day_high, day_low

# --- 4. MAIN TERMINAL ---
try:
    df, d_high, d_low = get_patro_data()
    curr_p = df['Close'].iloc[-1]
    curr_rsi = df['RSI'].iloc[-1]
    last_sig = "BUY" if df['Trend'].iloc[-1] == 1 else "SELL"

    st.markdown(f'<p class="title-text">🛡️ PATRO AI PRO: {last_sig}</p>', unsafe_allow_html=True)

    # These columns were dark before - they are now fixed with CSS above
    m1, m2, m3 = st.columns(3)
    m1.metric("LIVE PRICE", f"${curr_p:,.2f}")
    m2.metric("CURRENT SIGNAL", last_sig)
    m3.metric("MOMENTUM (RSI)", f"{curr_rsi:.2f}")

    # --- THE CHART ---
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                        vertical_spacing=0.03, row_heights=[0.75, 0.25])

    # Price Trace
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='US30'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA20'], name='Patro Trend', line=dict(color='orange', width=2)), row=1, col=1)
    
    # Levels
    fig.add_hline(y=d_high, line_dash="dash", line_color="#00ffff", annotation_text="HIGH", row=1, col=1)
    fig.add_hline(y=d_low, line_dash="dash", line_color="#ff4b4b", annotation_text="LOW", row=1, col=1)

    # RSI & Volume Panel
    fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], name='RSI', line=dict(color='#8A2BE2')), row=2, col=1)
    fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name='Volume', marker_color='rgba(255,255,255,0.1)'), row=2, col=1)
    fig.add_hline(y=70, line_dash="dot", line_color="red", row=2, col=1)
    fig.add_hline(y=30, line_dash="dot", line_color="green", row=2, col=1)

    # Fixed Labels (Clear text)
    for i in range(1, len(df)):
        if df['Entry'].iloc[i] == 2:
            fig.add_annotation(x=df.index[i], y=df['Low'].iloc[i], text="BUY", bgcolor="green", font=dict(color="white", size=12), ay=25)
        elif df['Entry'].iloc[i] == -2:
            fig.add_annotation(x=df.index[i], y=df['High'].iloc[i], text="SELL", bgcolor="red", font=dict(color="white", size=12), ay=-25)

    fig.update_layout(template='plotly_dark', height=800, xaxis_rangeslider_visible=False, margin=dict(l=10,r=10,t=10,b=10))
    fig.update_xaxes(tickformat="%H:%M", tickfont=dict(color='white'))

    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.info("Patro AI is scanning the market...")
