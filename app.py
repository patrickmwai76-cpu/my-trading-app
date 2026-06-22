import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import yfinance as yf
from gtts import gTTS
import io
import base64

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="PATRO AI PRO | SMC", layout="wide")

# --- 2. AUDIO GENERATION ENGINE ---
def speak_in_browser(text_to_speak):
    """Converts trade signals to explicit verbal instructions via base64 injection."""
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

# --- 3. LIQUIDITY & CROSSOVER CALCULATIONS ---
def get_market_analysis():
    # Pulling M15 Gold Data
    gold = yf.Ticker("GC=F")
    df = gold.history(period="3d", interval="15m")
    
    # 9/21 EMA Crossover Logic
    df['EMA9'] = df['Close'].ewm(span=9, adjust=False).mean()
    df['EMA21'] = df['Close'].ewm(span=21, adjust=False).mean()
    
    # Automated Liquidity Pool Tracking (Looking back 20 candles for key extremes)
    df['Recent_High'] = df['High'].shift(1).rolling(window=20).max()
    df['Recent_Low'] = df['Low'].shift(1).rolling(window=20).min()
    
    # Standard Signal Indicators
    df['Signal'] = 0
    df.loc[(df['EMA9'] > df['EMA21']) & (df['EMA9'].shift(1) <= df['EMA21'].shift(1)), 'Signal'] = 1
    df.loc[(df['EMA9'] < df['EMA21']) & (df['EMA9'].shift(1) >= df['EMA21'].shift(1)), 'Signal'] = -1
    
    return df

df_full = get_market_analysis()
df = df_full.tail(100)
latest_row = df.iloc[-1]
latest_signal = df[df['Signal'] != 0].iloc[-1] if not df[df['Signal'] != 0].empty else None

# --- 4. LIQUIDITY SWEEP DETECTOR ---
# Check if current price swept past recent structural extremes before returning
liquidity_alert = "Neutral"
voice_alert = ""

if latest_row['High'] > latest_row['Recent_High'] and latest_row['Close'] < latest_row['Recent_High']:
    liquidity_alert = "🔴 BEARISH LIQUIDITY SWEEP (Buy Orders Trapped)"
    voice_alert = "Patro, bearish liquidity sweep confirmed. High volume buyers are trapped. Prepare for a sell execution."
elif latest_row['Low'] < latest_row['Recent_Low'] and latest_row['Close'] > latest_row['Recent_Low']:
    liquidity_alert = "🟢 BULLISH LIQUIDITY SWEEP (Sell Orders Trapped)"
    voice_alert = "Patro, bullish liquidity sweep confirmed. Sell orders are trapped at the lows. Prepare for a buy entry."

# --- 5. TOP EXECUTIVE ACTION HEADER ---
if liquidity_alert != "Neutral":
    st.markdown(f"""
        <div style="background:#111; padding:25px; border-radius:15px; border:3px solid #FFC107; text-align:center;">
            <h1 style="color:#FFC107; margin:0;">⚠️ MARKET LIQUIDITY ALERT</h1>
            <p style="color:#FFF; font-size:18px; margin-top:10px; font-weight:bold;">{liquidity_alert}</p>
        </div>
    """, unsafe_allow_html=True)
elif latest_signal is not None:
    action = "🚀 STRONG BUY" if latest_signal['Signal'] == 1 else "🔻 STRONG SELL"
    color = "#00FF88" if latest_signal['Signal'] == 1 else "#FF4B4B"
    st.markdown(f"""
        <div style="background:#111; padding:20px; border-radius:15px; border:2px solid {color}; text-align:center;">
            <h1 style="color:{color}; margin:0;">{action} SIGNAL ACTIVE</h1>
            <p style="color:#888;">Crossover confirmed at ${latest_signal['Close']:.2f}</p>
        </div>
    """, unsafe_allow_html=True)

# --- 6. SMART MONEY CHART (SMC) ---
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

# --- 7. SIDEBAR MANAGEMENT PANEL ---
with st.sidebar:
    st.title("PATRO AI PRO")
    st.caption("SMC Liquidity Scanner")
    st.divider()
    
    # Audio Activation Check
    if st.button("🔊 Activate Live Audio Channel"):
        st.success("Voice Stream Connected.")
        speak_in_browser("System ready. Analyzing liquidity pools.")
        
    st.divider()
    st.metric("LIVE PRICE", f"${latest_row['Close']:.2f}")
    
    # Broadcast Area
    st.subheader("📢 Live Execution Briefing")
    if liquidity_alert != "Neutral":
        st.error(liquidity_alert)
        if voice_alert:
            speak_in_browser(voice_alert)
    else:
        st.info("Tracking market structure. No structural trap detected in this block.")
