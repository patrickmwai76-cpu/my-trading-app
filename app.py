import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import yfinance as yf
from gtts import gTTS
import io
import base64

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="PATRO AI PRO | PROFESSIONAL", layout="wide")

# --- 2. BROWSER AUDIO ENGINE ---
def speak_in_browser(text_to_speak):
    """Converts professional analytical text to high-quality speech played through the browser."""
    if text_to_speak:
        try:
            tts = gTTS(text=text_to_speak, lang='en', tld='com')
            mp3_fp = io.BytesIO()
            tts.write_to_fp(mp3_fp)
            mp3_fp.seek(0)
            b64 = base64.b64encode(mp3_fp.read()).decode()
            audio_html = f"""
                <audio autoplay style="display:none;">
                    <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                </audio>
            """
            st.markdown(audio_html, unsafe_allow_html=True)
        except Exception:
            pass

# --- 3. PROFESSIONAL ANALYTICS ENGINE ---
def get_market_analysis():
    # Fetch live M15 Gold data
    gold = yf.Ticker("GC=F")
    df = gold.history(period="3d", interval="15m")
    
    # Core Mathematical Indicators
    df['EMA9'] = df['Close'].ewm(span=9, adjust=False).mean()
    df['EMA21'] = df['Close'].ewm(span=21, adjust=False).mean()
    
    # Calculate Average True Range (ATR) for institutional risk boundaries
    high_low = df['High'] - df['Low']
    high_close = abs(df['High'] - df['Close'].shift())
    low_close = abs(df['Low'] - df['Close'].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = ranges.max(axis=1)
    df['ATR'] = true_range.rolling(14).mean()
    
    # Dynamic Trend Execution Signal
    df['Signal'] = 0
    df.loc[(df['EMA9'] > df['EMA21']) & (df['EMA9'].shift(1) <= df['EMA21'].shift(1)), 'Signal'] = 1
    df.loc[(df['EMA9'] < df['EMA21']) & (df['EMA9'].shift(1) >= df['EMA21'].shift(1)), 'Signal'] = -1
    
    return df

df_full = get_market_analysis()
df = df_full.tail(100)
latest_signal = df[df['Signal'] != 0].iloc[-1] if not df[df['Signal'] != 0].empty else None

# --- 4. TOP ACTION EXECUTIVE HEADER ---
if latest_signal is not None:
    action = "🚀 STRONG BUY" if latest_signal['Signal'] == 1 else "🔻 STRONG SELL"
    color = "#00FF88" if latest_signal['Signal'] == 1 else "#FF4B4B"
    st.markdown(f"""
        <div style="background:#111; padding:20px; border-radius:15px; border:2px solid {color}; text-align:center;">
            <h1 style="color:{color}; margin:0;">{action} SYSTEM ALERT</h1>
            <p style="color:#888; font-weight: bold; margin-top: 5px;">M15 Structure Confirmed at ${latest_signal['Close']:.2f}</p>
        </div>
    """, unsafe_allow_html=True)

# --- 5. THE SMART MONEY CHART (SMC) ---
st.markdown("### 📊 SMART MONEY CHART (SMC)")

chart_html = """
<div id="tv_chart" style="height:550px;"></div>
<script src="https://s3.tradingview.com/tv.js"></script>
<script>
new TradingView.widget({
  "autosize": true,
  "symbol": "OANDA:XAUUSD",
  "interval": "15",
  "theme": "dark",
  "style": "1",
  "container_id": "tv_chart",
  "studies": [
    { "id": "MASimple@tv-basicstudies", "inputs": { "length": 9 }, "title": "Fast EMA", "plots": { "0": { "color": "#FFEB3B" } } },
    { "id": "MASimple@tv-basicstudies", "inputs": { "length": 21 }, "title": "Slow EMA", "plots": { "0": { "color": "#FF5252" } } }
  ]
});
</script>"""
components.html(chart_html, height=560)

# --- 6. EXECUTIVE ASSISTANT SIDEBAR PANEL ---
with st.sidebar:
    st.title("PATRO AI PRO")
    st.caption("Professional Execution Interface")
    st.divider()
    
    # Real-Time Price Metrics
    current_price = df['Close'].iloc[-1]
    st.metric("LIVE XAUUSD PRICE", f"${current_price:.2f}")
    
    st.divider()
    st.subheader("📋 Executive Assistant Briefing")
    
    # Audio Initialization Button to comply with browser playback policies
    if st.button("🔊 Initialize Professional Audio Channel"):
        init_brief = "Audio alignment complete. Stand by for metric analysis."
        st.success("Audio Stream Operational.")
        speak_in_browser(init_brief)
        
    # Standard Request Dropdown to eliminate input lag and provide immediate structural analytics
    report_type = st.selectbox("Request Professional Briefing:", [
        "Select Report Type", 
        "Comprehensive Market Briefing", 
        "Risk Assessment & Trade Boundaries"
    ])
    
    if report_type == "Comprehensive Market Briefing":
        if latest_signal is not None:
            direction = "Bullish expansion" if latest_signal['Signal'] == 1 else "Bearish expansion"
            briefing_text = f"Market structure on the fifteen-minute chart indicates a verified {direction}. Crossover confirmation was achieved at {latest_signal['Close']:.2f}. Current price action is tracking at {current_price:.2f}. Prioritize execution alignment with higher timeframe order blocks."
        else:
            briefing_text = f"Gold is currently demonstrating tight consolidation around {current_price:.2f}. System suggests monitoring liquidity ranges before committing capital."
        
        st.info(briefing_text)
        speak_in_browser(briefing_text)
        
    elif report_type == "Risk Assessment & Trade Boundaries":
        current_atr = df['ATR'].iloc[-1]
        risk_text = f"Current market volatility, measured by the fourteen period ATR, stands at {current_atr:.2f} dollars. For optimum risk management, ensure stop losses are positioned safely behind structural invalidation zones."
        st.warning(risk_text)
        speak_in_browser(risk_text)
