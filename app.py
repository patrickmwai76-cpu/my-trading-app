import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import yfinance as yf

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="PATRO AI PRO | CROSSOVER", layout="wide")

# --- 2. CROSSOVER LOGIC ENGINE ---
def get_crossover_data():
    # Fetching live M15 Gold data
    gold = yf.Ticker("GC=F")
    df = gold.history(period="2d", interval="15m")
    
    # EMA 9 (Fast - Yellow) and EMA 21 (Slow - Red)
    df['EMA9'] = df['Close'].ewm(span=9, adjust=False).mean()
    df['EMA21'] = df['Close'].ewm(span=21, adjust=False).mean()
    
    # Signal Logic: 1 for Buy, -1 for Sell
    df['Signal'] = 0
    # Buy when 9 crosses above 21
    df.loc[(df['EMA9'] > df['EMA21']) & (df['EMA9'].shift(1) <= df['EMA21'].shift(1)), 'Signal'] = 1
    # Sell when 9 crosses below 21
    df.loc[(df['EMA9'] < df['EMA21']) & (df['EMA9'].shift(1) >= df['EMA21'].shift(1)), 'Signal'] = -1
    
    return df.tail(100)

df = get_crossover_data()
latest_signal = df[df['Signal'] != 0].iloc[-1] if not df[df['Signal'] != 0].empty else None

# --- 3. TOP ACTION HEADER ---
if latest_signal is not None:
    action = "🚀 STRONG BUY" if latest_signal['Signal'] == 1 else "🔻 STRONG SELL"
    color = "#00FF88" if latest_signal['Signal'] == 1 else "#FF4B4B"
    st.markdown(f"""
        <div style="background:#111; padding:20px; border-radius:15px; border:2px solid {color}; text-align:center;">
            <h1 style="color:{color}; margin:0;">{action} SIGNAL DETECTED</h1>
            <p style="color:#888;">Crossover confirmed at ${latest_signal['Close']:.2f}</p>
        </div>
    """, unsafe_allow_html=True)

# --- 4. THE SMART MONEY CHART (SMC) ---
st.markdown("### 📊 SMART MONEY CHART (SMC)")

# We use TradingView's library to draw the lines and markers
chart_html = f"""
<div id="tv_chart" style="height:600px;"></div>
<script src="https://s3.tradingview.com/tv.js"></script>
<script>
new TradingView.widget({{
  "autosize": true,
  "symbol": "OANDA:XAUUSD",
  "interval": "15",
  "theme": "dark",
  "style": "1",
  "container_id": "tv_chart",
  "studies": [
    {{
        "id": "MASimple@tv-basicstudies",
        "inputs": {{ "length": 9 }},
        "title": "Fast EMA",
        "plots": {{ "0": {{ "color": "#FFEB3B" }} }}  // Yellow Line
    }},
    {{
        "id": "MASimple@tv-basicstudies",
        "inputs": {{ "length": 21 }},
        "title": "Slow EMA",
        "plots": {{ "0": {{ "color": "#FF5252" }} }}  // Red Line
    }}
  ],
  "show_popup_button": true,
  "popup_width": "1000",
  "popup_height": "650"
}});
</script>
"""
components.html(chart_html, height=610)

# --- 5. SIDEBAR STATS ---
with st.sidebar:
    st.title("PATRO AI PRO")
    st.write("📍 Nairobi, Kenya")
    st.divider()
    st.metric("CURRENT PRICE", f"${df['Close'].iloc[-1]:.2f}")
    if latest_signal is not None:
        st.write(f"**Last Cross:** {latest_signal.name.strftime('%H:%M')}")
        st.write(f"**Type:** {'Bullish' if latest_signal['Signal'] == 1 else 'Bearish'}")
