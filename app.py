import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import yfinance as yf
from gtts import gTTS  # Browser-friendly Voice Engine
import io
import base64

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="PATRO AI PRO | CROSSOVER", layout="wide")

# --- 2. BROWSER AUDIO ENGINE ---
def speak_in_browser(text_to_speak):
    """Converts text to an mp3 object and force-plays it through the browser browser using base64."""
    if text_to_speak:
        tts = gTTS(text=text_to_speak, lang='en', tld='com')
        mp3_fp = io.BytesIO()
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)
        
        # Encode audio to display inside the page cleanly
        b64 = base64.b64encode(mp3_fp.read()).decode()
        audio_html = f"""
            <audio autoplay class="stAudio" style="display:none;">
                <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
        """
        st.markdown(audio_html, unsafe_allow_html=True)

# --- 3. CROSSOVER LOGIC ENGINE ---
def get_crossover_data():
    gold = yf.Ticker("GC=F")
    df = gold.history(period="2d", interval="15m")
    
    df['EMA9'] = df['Close'].ewm(span=9, adjust=False).mean()
    df['EMA21'] = df['Close'].ewm(span=21, adjust=False).mean()
    
    df['Signal'] = 0
    df.loc[(df['EMA9'] > df['EMA21']) & (df['EMA9'].shift(1) <= df['EMA21'].shift(1)), 'Signal'] = 1
    df.loc[(df['EMA9'] < df['EMA21']) & (df['EMA9'].shift(1) >= df['EMA21'].shift(1)), 'Signal'] = -1
    
    return df.tail(100)

df = get_crossover_data()
latest_signal = df[df['Signal'] != 0].iloc[-1] if not df[df['Signal'] != 0].empty else None

# --- 4. TOP ACTION HEADER ---
if latest_signal is not None:
    action = "🚀 STRONG BUY" if latest_signal['Signal'] == 1 else "🔻 STRONG SELL"
    color = "#00FF88" if latest_signal['Signal'] == 1 else "#FF4B4B"
    st.markdown(f"""
        <div style="background:#111; padding:20px; border-radius:15px; border:2px solid {color}; text-align:center;">
            <h1 style="color:{color}; margin:0;">{action} SIGNAL DETECTED</h1>
            <p style="color:#888;">Crossover confirmed at ${latest_signal['Close']:.2f}</p>
        </div>
    """, unsafe_allow_html=True)

# --- 5. THE SMART MONEY CHART (SMC) ---
st.markdown("### 📊 SMART MONEY CHART (SMC)")

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
        "plots": {{ "0": {{ "color": "#FFEB3B" }} }}
    }},
    {{
        "id": "MASimple@tv-basicstudies",
        "inputs": {{ "length": 21 }},
        "title": "Slow EMA",
        "plots": {{ "0": {{ "color": "#FF5252" }} }}
    }}
  ]
}});
</script>
"""
components.html(chart_html, height=610)

# --- 6. SIDEBAR CHAT INTERFACE & STATS ---
with st.sidebar:
    st.title("PATRO AI PRO")
    st.write("📍 Nairobi, Kenya")
    st.divider()
    
    # Live Assistant Chat Box
    st.subheader("💬 Ask Your AI Assistant")
    user_message = st.text_input("Type your question here, Patro:", key="chat_input")
    
    if user_message:
        reply_text = ""
        msg = user_message.lower()
        
        # Friendly rule handling responses based on your system rules
        if "status" in msg or "signal" in msg:
            if latest_signal is not None:
                current_trend = "Bullish and screaming Buy" if latest_signal['Signal'] == 1 else "Bearish and showing a clean Sell setup"
                reply_text = f"Hey Patro! Looking at the M15 chart right now, the momentum is {current_trend} at {latest_signal['Close']:.2f}. Keep an eye on those lines!"
            else:
                reply_text = "Hey my friend! The market lines are running completely sideways right now. No major crossover detected yet. Keep cool and wait for the breakout."
        elif "price" in msg or "gold" in msg:
            reply_text = f"Gold is sitting right at {df['Close'].iloc[-1]:.2f} dollars per ounce right now. It is tracking perfectly on our setup."
        elif "hello" in msg or "hi" in msg:
            reply_text = "Hello Patro! I am locked and loaded. Ready to track these gold signals with you today. What are we looking at?"
        else:
            reply_text = "That is an interesting spot on the chart, my friend! Let's watch how the market handles this level over the next few candles."
            
        st.write(f"🤖 **Patro AI:** {reply_text}")
        speak_in_browser(reply_text)  # Triggers aloud audio
        
    st.divider()
    st.metric("CURRENT PRICE", f"${df['Close'].iloc[-1]:.2f}")
