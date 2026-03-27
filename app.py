import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import pytz
from tradingview_ta import TA_Handler, Interval
from streamlit_autorefresh import st_autorefresh
import streamlit.components.v1 as components

# 1. PAGE SETUP
st.set_page_config(page_title="PATRO AI PRO V12.4.1", layout="wide")
st.markdown("<style>.stApp { background: #000; color: #fff; }</style>", unsafe_allow_html=True)

# 2. AUTO-SYNC (Refresh every 2 minutes)
st_autorefresh(interval=120000, key="data_sync")

# 3. LIVE TICKER TAPE (Price Flow on Home)
components.html("""
<div class="tradingview-widget-container">
  <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-ticker-nfp.js" async>
  { "symbols": [{"proName": "OANDA:XAUUSD", "title": "GOLD"},{"proName": "TVC:DXY", "title": "DXY"}], "colorTheme": "dark", "isTransparent": true }
  </script>
</div>""", height=50)

# 4. RESTORED NEWS COUNTDOWN
def get_news_countdown():
    try:
        r = requests.get("https://nfs.faireconomy.media/ff_calendar_thisweek.json")
        now = datetime.now(pytz.utc)
        upcoming = [n for n in r.json() if n['impact'] == 'High' and n['country'] == 'USD']
        for n in upcoming:
            ev_time = datetime.strptime(n['date'], "%Y-%m-%dT%H:%M:%S%z")
            if ev_time > now:
                diff = ev_time - now
                h, m = divmod(int(diff.total_seconds()), 3600)
                mn, _ = divmod(m, 60)
                return f"⏳ {n['title']} in {h}h {mn}m", "#FFA500"
        return "✅ NO HIGH IMPACT NEWS", "#00FF88"
    except: return "📡 NEWS OFFLINE", "#888"

# 5. DYNAMIC RATING & ACTION LOGIC
def get_deep_rating():
    tfs = [Interval.INTERVAL_1_MINUTE, Interval.INTERVAL_5_MINUTES, Interval.INTERVAL_15_MINUTES, 
           Interval.INTERVAL_1_HOUR, Interval.INTERVAL_4_HOURS, Interval.INTERVAL_1_DAY]
    buys, sells = 0, 0
    tf_results = {}
    try:
        for tf in tfs:
            h = TA_Handler(symbol="XAUUSD", screener="forex", exchange="OANDA", interval=tf)
            a = h.get_analysis()
            buys += a.summary['BUY']; sells += a.summary['SELL']
            tf_results[tf] = a.summary['RECOMMENDATION']
        score = round((buys / (buys + sells)) * 10, 1) if (buys + sells) > 0 else 5.0
        if score > 7.0: act, col = "🔥 LOOK FOR BUY", "#00FF88"
        elif score < 3.0: act, col = "🧊 LOOK FOR SELL", "#FF4B4B"
        else: act, col = "⚖️ WAIT / NEUTRAL", "#FFA500"
        return score, act, col, tf_results
    except: return 5.0, "REFRESHING...", "#888", {}

score, action, m_col, all_tf = get_deep_rating()
news_msg, news_col = get_news_countdown()

# 6. TOP HUD (News Countdown)
st.markdown(f"<div style='text-align:center; padding:10px; border-radius:10px; background:rgba(255,255,255,0.05); border: 1px solid {news_col}; color:{news_col}; font-weight:bold;'>{news_msg}</div>", unsafe_allow_html=True)

# 7. SIDEBAR (Rating + Visual Strength Bar)
st.sidebar.markdown(f"<h1 style='color:{m_col}; text-align:center; margin:0;'>{score}</h1>", unsafe_allow_html=True)
st.sidebar.markdown(f"<h3 style='color:{m_col}; text-align:center; margin:0;'>{action}</h3>", unsafe_allow_html=True)

# Custom Progress Bar (Visual Strength)
st.sidebar.markdown("---")
st.sidebar.write("📈 **TREND STRENGTH**")
st.sidebar.progress(score / 10.0) # Visual bar from 0.0 to 1.0

st.sidebar.subheader("⏳ TF SCANNER")
for tf, rec in all_tf.items():
    st.sidebar.write(f"**{tf.replace('_',' ')}**: {rec}")

# 8. POSITION SIZER
st.sidebar.markdown("---")
bal = st.sidebar.number_input("Balance", value=1000)
risk = st.sidebar.slider("Risk %", 0.5, 5.0, 1.0)
sl = st.sidebar.number_input("SL Pips", value=30)
st.sidebar.info(f"LOT SIZE: {round((bal*(risk/100))/(sl*10), 2)}")

# 9. GAUGES & CHART
c1, c2 = st.columns(2)
with c1: components.html('<script src="https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js" async>{ "interval": "1m", "width": "100%", "height": "380", "isTransparent": true, "symbol": "OANDA:XAUUSD", "showIntervalTabs": true, "colorTheme": "dark" }</script>', height=390)
with c2: components.html('<script src="https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js" async>{ "interval": "1m", "width": "100%", "height": "380", "isTransparent": true, "symbol": "TVC:DXY", "showIntervalTabs": true, "colorTheme": "dark" }</script>', height=390)

st.subheader("📊 PATRO SMC TERMINAL")
components.html(f"""
<div style="height:700px;">
  <div id="tv_chart"></div>
  <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
  <script type="text/javascript">
  new TradingView.widget({{"autosize": true, "symbol": "OANDA:XAUUSD", "interval": "1", "theme": "dark", "style": "1", "container_id": "tv_chart", "show_popup_button": true, "studies": ["STD;Fair_Value_Gap", "STD;Order_Block", "STD;Pivot_Points_High_Low", "STD;VWAP"]}});
  </script>
</div>""", height=710)
