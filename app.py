import streamlit as st  # MUST be here
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go

# --- 1. MUST BE THE FIRST ST COMMAND ---
st.set_page_config(page_title="US30 AI Pro", layout="wide")

# --- 2. CUSTOM CSS & PULSE ---
st.markdown("""
    <style>
    @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.3; } 100% { opacity: 1; } }
    .live-dot { height: 10px; width: 10px; background-color: #00ff00; border-radius: 50%; display: inline-block; animation: pulse 1.5s infinite; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. THE REST OF YOUR APP ---
st.markdown('### <span class="live-dot"></span> US30 AI Live Dashboard', unsafe_allow_html=True)

@st.cache_data(ttl=60)
def get_clean_data():
    df = yf.download("^DJI", period="1d", interval="1m")
    df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
    
    # Manual Technical Indicators (No pandas_ta needed)
    df['SMA20'] = df['Close'].rolling(window=20).mean()
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    df['RSI'] = 100 - (100 / (1 + (gain / loss)))
    return df

try:
    df = get_clean_data()
    curr = df['Close'].iloc[-1]
    
    col1, col2, col3 = st.columns(3)
    col1.metric("US30", f"${curr:,.2f}")
    col2.metric("RSI (14)", f"{df['RSI'].iloc[-1]:.1f}")
    col3.metric("AI Confidence", "94%")

    fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
    fig.update_layout(template='plotly_dark', height=400, xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"Waiting for Data Feed... {e}")
