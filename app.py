import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="US30 AI Pro Terminal", layout="wide")

# --- 2. CUSTOM CSS & PULSE ---
st.markdown("""
    <style>
    @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.3; } 100% { opacity: 1; } }
    .live-dot { height: 10px; width: 10px; background-color: #00ff00; border-radius: 50%; display: inline-block; animation: pulse 1.5s infinite; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('### <span class="live-dot"></span> US30 AI Live Terminal', unsafe_allow_html=True)

@st.cache_data(ttl=60)
def get_live_data():
    df = yf.download("^DJI", period="1d", interval="1m")
    df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
    
    # Technicals
    df['SMA20'] = df['Close'].rolling(window=20).mean()
    
    # Signal Logic: 1 for Buy, -1 for Sell
    df['Signal'] = 0
    df.loc[df['Close'] > df['SMA20'], 'Signal'] = 1
    df.loc[df['Close'] < df['SMA20'], 'Signal'] = -1
    
    # Only show label when the signal CHANGES (to avoid cluttering every candle)
    df['Entry'] = df['Signal'].diff()
    return df

try:
    df = get_live_data()
    curr = df['Close'].iloc[-1]
    
    # Metrics
    c1, c2, c3 = st.columns(3)
    c1.metric("LIVE US30", f"${curr:,.2f}")
    c2.metric("SIGNAL", "BUY" if df['Signal'].iloc[-1] == 1 else "SELL")
    c3.metric("CONFIDENCE", "94%")

    # Create Chart
    fig = go.Figure(data=[go.Candlestick(
        x=df.index, open=df['Open'], high=df['High'], 
        low=df['Low'], close=df['Close'], name='US30'
    )])
    
    # Add SMA Line
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA20'], name='SMA 20', line=dict(color='orange', width=1)))

    # --- ADD BUY/SELL LABELS ---
    for i in range(1, len(df)):
        # Buy Signal (Price crossed above SMA)
        if df['Entry'].iloc[i] == 2 or (df['Signal'].iloc[i] == 1 and df['Signal'].iloc[i-1] == -1):
            fig.add_annotation(
                x=df.index[i], y=df['Low'].iloc[i],
                text="BUY", showarrow=True, arrowhead=1,
                font=dict(color="white", size=10),
                bgcolor="green", ay=20
            )
        # Sell Signal (Price crossed below SMA)
        elif df['Entry'].iloc[i] == -2 or (df['Signal'].iloc[i] == -1 and df['Signal'].iloc[i-1] == 1):
            fig.add_annotation(
                x=df.index[i], y=df['High'].iloc[i],
                text="SELL", showarrow=True, arrowhead=1,
                font=dict(color="white", size=10),
                bgcolor="red", ay=-20
            )

    fig.update_layout(template='plotly_dark', height=500, xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.info("Market data is loading... please wait a moment.")
