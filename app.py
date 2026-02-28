import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- 1. SETUP & BRANDING ---
st.set_page_config(page_title="PATRO AI PRO | US30", layout="wide")

# Custom CSS for the "Patro" Branding
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .title-text {
        font-size: 45px !important;
        font-weight: 800;
        color: #00ff00;
        text-shadow: 2px 2px 10px rgba(0, 255, 0, 0.5);
        letter-spacing: 2px;
    }
    div[data-testid="stMetric"] { 
        background-color: #1e2130 !important; 
        padding: 20px; 
        border-radius: 12px; 
        border: 2px solid #00ff00;
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
    st.subheader("💰 Risk Management")
    balance = st.number_input("Balance ($)", value=1000)
    risk = st.slider("Risk (%)", 0.5, 5.0, 1.0)
    st.success(f"Risk Amount: ${balance * (risk/100):.2f}")

# --- 3. THE DATA ENGINE ---
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
    last_sig = "BUY" if df['Trend'].iloc[-1] == 1 else "SELL"

    st.markdown(f'<p class="title-text">🛡️ PATRO AI PRO: {last_sig}</p>', unsafe_allow_html=True)

    m1, m2, m3 = st.columns(3)
    m1.metric("LIVE PRICE", f"${curr_p:,.2f}")
    m2.metric("CURRENT SIGNAL", last_sig)
    m3.metric("MOMENTUM (RSI)", f"{df['RSI'].iloc[-1]:.2f}")

    # --- THE CHART ---
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                        vertical_spacing=0.03, row_heights=[0.75, 0.25])

    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='US30'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA20'], name='Patro Trend', line=dict(color='orange', width=2)), row=1, col=1)
    fig.add_hline(y=d_high, line_dash="dash", line_color="#00ffff", annotation_text="HIGH", row=1, col=1)
    fig.add_hline(y=d_low, line_dash="dash", line_color="#ff4b4b", annotation_text="LOW", row=1, col=1)

    fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], name='RSI Scale', line=dict(color='#8A2BE2')), row=2, col=1)
    fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name='Volume', marker_color='rgba(255,255,255,0.1)'), row=2, col=1)

    for i in range(1, len(df)):
        if df['Entry'].iloc[i] == 2:
            fig.add_annotation(x=df.index[i], y=df['Low'].iloc[i], text="BUY", bgcolor="green", font=dict(color="white"), ay=25)
        elif df['Entry'].iloc[i] == -2:
            fig.add_annotation(x=df.index[i], y=df['High'].iloc[i], text="SELL", bgcolor="red", font=dict(color="white"), ay=-25)

    fig.update_layout(template='plotly_dark', height=850, xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.info("Patro AI is scanning the market...")
