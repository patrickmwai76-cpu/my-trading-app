# 1. Pulse Indicator (CSS)
st.markdown("""
    <style>
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.3; }
        100% { opacity: 1; }
    }
    .live-dot {
        height: 10px; width: 10px;
        background-color: #00ff00;
        border-radius: 50%;
        display: inline-block;
        animation: pulse 1.5s infinite;
    }
    </style>
    <h3><span class="live-dot"></span> US30 AI LIVE DASHBOARD</h3>
    """, unsafe_allow_html=True)

# 2. Add RSI Calculation (Safe Version)
delta = df['Close'].diff()
gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
rs = gain / loss
df['RSI'] = 100 - (100 / (1 + rs))

# 3. Display RSI in a metric
current_rsi = df['RSI'].iloc[-1]
st.sidebar.metric("RSI (14)", f"{current_rsi:,.2f}", "Overbought" if current_rsi > 70 else "Oversold" if current_rsi < 30 else "Neutral")
