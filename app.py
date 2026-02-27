import streamlit as st
import plotly.graph_objects as go
import pandas as pd
# For indicators
import pandas_ta as ta 

# --- 1. PRO CHART SECTION ---
def style_chart(df):
    fig = go.Figure(data=[go.Candlestick(
        x=df['Date'],
        open=df['Open'], high=df['High'],
        low=df['Low'], close=df['Close'],
        name='US30'
    )])
    
    # Add a 20-period Moving Average (The "Pro" Look)
    df['MA20'] = ta.sma(df['Close'], length=20)
    fig.add_trace(go.Scatter(x=df['Date'], y=df['MA20'], line=dict(color='orange', width=1), name='MA20'))

    fig.update_layout(template='plotly_dark', xaxis_rangeslider_visible=False, height=400)
    st.plotly_chart(fig, use_container_width=True)

# --- 2. DYNAMIC AI SIGNAL CARD ---
def signal_card(confidence, trend):
    col1, col2 = st.columns([1, 3])
    with col1:
        st.metric("AI Confidence", f"{confidence}%", delta="High")
    with col2:
        if trend == "BUY":
            st.success(f"🚀 AI SIGNAL: {trend} (Strong Momentum)")
        else:
            st.error(f"📉 AI SIGNAL: {trend} (High Volatility)")

# --- 3. LIVE "TICKER" NOTIFICATIONS ---
if st.button("Simulate Price Target"):
    st.toast('Target Hit: $48,914.18', icon='🎯')
    st.balloons()
