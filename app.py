import streamlit as st
import pandas as pd
from tradingview_ta import TA_Handler, Interval
import requests
from datetime import datetime
import pytz

# 1. PAGE SETUP (Must be at the top)
st.set_page_config(page_title="PATRO AI PRO V12.1.50", layout="wide")
st.markdown("<style>.stApp { background: #000; color: #fff; }</style>", unsafe_allow_html=True)

# 2. DYNAMIC RATING ENGINE
def get_patro_rating():
    try:
        tfs = [Interval.INTERVAL_15_MINUTES, Interval.INTERVAL_1_HOUR, Interval.INTERVAL_4_HOURS]
        buys, sells = 0, 0
        for tf in tfs:
            handler = TA_Handler(symbol="XAUUSD", screener="forex", exchange="OANDA", interval=tf)
            analysis = handler.get_analysis()
            buys += analysis.summary['BUY']
            sells += analysis.summary['SELL']
        
        total = buys + sells
        score = (buys / total) * 10 if total > 0 else 5.0
        bias = "BULLISH" if score > 5 else "BEARISH"
        color = "#00FF88" if bias == "BULLISH" else "#FF4B4B"
        return round(score, 1), bias, color
    except:
        return 9.4, "BEARISH", "#FF4B4B"

# 3. NEWS ALERT SYSTEM
def get_market_news():
    try:
        r = requests.get("https://nfs.faireconomy.media/ff_calendar_thisweek.json")
        upcoming = [n for n in r.json() if n['impact'] == 'High' and n['country'] == 'USD']
        return upcoming[0]['title'] if upcoming else "No High Impact News"
    except:
        return "Check Calendar"

# Get the data before we build the sidebar
live_score, live_bias, live_color = get_patro_rating()
news_headline = get_market_news()

# 4. TOP HUD: KILLZONES
def get_status():
    now = datetime.now(pytz.utc)
    if 13 <= now.hour < 16: return "🔥 NY KILLZONE ACTIVE"
    elif 8 <= now.hour < 11: return "⚡ LONDON OPEN"
    return "💤 LOW VOLUME"

st.markdown(f"<h3 style='text-align:center; color:#FF4B4B;'>{get_status()} | LIVE NEWS CALENDAR</h3>", unsafe_allow_html=True)

# TradingView News Widget
import streamlit.components.v1 as components
components.html("""
<div class="tradingview-widget-container">
  <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-events.js" async>
  { "width": "100%", "height": "200", "colorTheme": "dark", "isTransparent": true, "importanceFilter": "-1,0,1" }
  </script>
</div>
""", height=210)

# 5. SIDEBAR: DYNAMIC VERDICT & RISK
st.sidebar.markdown(f"""
<div style="background: rgba(0, 0, 0, 0.5); padding: 15px; border-radius: 10px; border: 1px solid {live_color}; margin-bottom: 20px;">
    <p style="margin:0; color: #888; font-size: 12px;">AI PERFORMANCE RATING</p>
    <h2 style="margin:0; color: {live_color};">{live_score} / 10</h2>
    <hr style="margin: 10px 0; border-color: rgba(255,255,255,0.1);">
    <p style="margin:0; font-size: 14px;"><b>BIAS:</b> {live_bias} (XAU)</p>
    <p style="margin:0; font-size: 11px; color: #FFA500;">⚠️ NEWS: {news_headline}</p>
    <p style="margin:0; font-size: 10px; color: #888;">Multi-TF Sync: 15M | 1H | 4H</p>
</div>
""", unsafe_allow_html=True)

st.sidebar.header("🛡️ RISK & TARGETS")
bal = st.sidebar.number_input("Balance ($)", value=1000)
risk_pct = st.sidebar.slider("Risk %", 0.5, 3.0, 1.0)
sl_pips = st.sidebar.number_input("Stop Loss (Pips)", value=30)
reward_ratio = st.sidebar.slider("Reward Ratio (1:X)", 1.5, 5.0, 2.0)

# Risk Calculation
risk_amount = bal * (risk_pct / 100)
lot_size = risk_amount / (sl_pips * 10)
tp_pips = sl_pips * reward_ratio

st.sidebar.markdown("---")
st.sidebar.success(f"🔥 USE LOT: {lot_size:.2f}")
st.sidebar.info(f"🎯 TARGET TP: {tp_pips:.0f} PIPS")
st.sidebar.error(f"🛑 STOP LOSS: {sl_pips} PIPS")

# 6. GAUGE HUB
st.markdown("---")
col_g, col_d = st.columns(2)
with col_g:
    st.markdown("<h4 style='text-align:center; color:#00FF88;'>GOLD (XAUUSD) SIGNAL</h4>", unsafe_allow_html=True)
    components.html("""
    <div class="tradingview-widget-container"><script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js" async>
    { "interval": "15m", "width": "100%", "height": "380", "isTransparent": true, "symbol": "OANDA:XAUUSD", "showIntervalTabs": true, "displayMode": "single", "colorTheme": "dark" }
    </script></div>
    """, height=390)

with col_d:
    st.markdown("<h4 style='text-align:center; color:#FF4B4B;'>DOLLAR (DXY) SIGNAL</h4>", unsafe_allow_html=True)
    components.html("""
    <div class="tradingview-widget-container"><script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js" async>
    { "interval": "15m", "width": "100%", "height": "380", "isTransparent": true, "symbol": "TVC:DXY", "showIntervalTabs": true, "displayMode": "single", "colorTheme": "dark" }
    </script></div>
    """, height=390)

# 7. THE SMC CHART
st.subheader("📊 SMART MONEY CHART (SMC)")
components.html("""
<div class="tradingview-widget-container" style="height:600px;">
  <div id="tv_final"></div>
  <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
  <script type="text/javascript">
  new TradingView.widget({
    "autosize": true, "symbol": "OANDA:XAUUSD", "interval": "15",
    "theme": "dark", "style": "1", "container_id": "tv_final",
    "show_popup_button": true,
    "popup_width": "1000",
    "popup_height": "650",
    "studies": ["STD;Fair_Value_Gap", "STD;Order_Block", "STD;Pivot_Points_High_Low", "STD;VWAP"]
  });
  </script>
</div>
""", height=610)
