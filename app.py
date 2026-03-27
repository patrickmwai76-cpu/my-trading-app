import streamlit as st
import requests
from datetime import datetime
import pytz
from tradingview_ta import TA_Handler, Interval
from streamlit_autorefresh import st_autorefresh
import streamlit.components.v1 as components

# 1. PAGE SETUP
st.set_page_config(page_title="PATRO AI PRO V12.6.9", layout="wide")
st.markdown("<style>.stApp { background: #000; color: #fff; }</style>", unsafe_allow_html=True)

# 2. REFRESH
st_autorefresh(interval=60000, key="patro_pulse")

# 3. LIVE TICKER
components.html("""
<div class="tradingview-widget-container">
  <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-ticker-nfp.js" async>
  { "symbols": [
    {"proName": "OANDA:XAUUSD", "title": "GOLD"},
    {"proName": "TVC:DXY", "title": "DXY"}
  ], "colorTheme": "dark", "isTransparent": true }
  </script>
</div>""", height=50)

# 4. AI SIGNAL ENGINE (Calculates the "NOW" logic)
def get_analysis():
    try:
        handler = TA_Handler(symbol="XAUUSD", screener="forex", exchange="OANDA", interval=Interval.INTERVAL_15_MINUTES)
        analysis = handler.get_analysis().summary['RECOMMENDATION']
        
        # If the 15m is Strong, we trigger the "NOW" signal
        if "STRONG_BUY" in analysis: return "🚀 BUY NOW", "#00FF88", 9.5
        elif "STRONG_SELL" in analysis: return "📉 SELL NOW", "#FF4B4B", 1.5
        elif "BUY" in analysis: return "🔥 BULLISH", "#00FF88", 7.0
        elif "SELL" in analysis: return "🧊 BEARISH", "#FF4B4B", 3.0
        else: return "⚖️ NEUTRAL", "#FFA500", 5.0
    except: return "SYNCING", "#888", 5.0

action, color, score = get_analysis()

# 5. SIDEBAR HUD
st.sidebar.markdown(f"""
<div style="text-align:center; padding:20px; border: 3px solid {color}; border-radius:15px; background: rgba(0,0,0,0.5);">
    <h1 style="color:{color}; margin:0; font-size:35px;">{action}</h1>
    <p style="color:#888; margin:0;">STRENGTH: {score}/10</p>
</div>
""", unsafe_allow_html=True)

# 6. THE CHART (With Built-in Buy/Sell Indicators)
st.subheader("📊 PATRO SMC MASTER CHART")

# This script now includes "Pivot Points High Low" which creates the S/R labels on chart
components.html(f"""
<div id="tv_chart_container" style="height:700px;"></div>
<script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
<script type="text/javascript">
new TradingView.widget({{
  "autosize": true,
  "symbol": "OANDA:XAUUSD",
  "interval": "15",
  "theme": "dark",
  "style": "1",
  "container_id": "tv_chart_container",
  "show_popup_button": true,
  "allow_symbol_change": true,
  "withdateranges": true,
  "details": true,
  # These specific studies force Buy/Sell/Pivot labels to appear on the candles
  "studies": [
    "STD;Pivot_Points_High_Low", 
    "STD;Bollinger_Bands%B",
    "STD;Fair_Value_Gap",
    "STD;Order_Block"
  ],
  "disabled_features": ["use_localstorage_for_settings_active_page"]
}});
</script>
""", height=720)

# 7. GAUGES & RISK
st.sidebar.markdown("---")
st.sidebar.subheader("🛡️ RISK CALCULATOR")
bal = st.sidebar.number_input("Balance", value=1000)
sl = st.sidebar.number_input("SL Pips", value=30)
st.sidebar.info(f"REC LOT: {round((bal*0.01)/(sl*10), 2)}")
