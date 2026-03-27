import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import pytz
from tradingview_ta import TA_Handler, Interval
from streamlit_autorefresh import st_autorefresh
import streamlit.components.v1 as components

# 1. PAGE SETUP
st.set_page_config(page_title="PATRO AI PRO V12.7.0", layout="wide")
st.markdown("<style>.stApp { background: #000; color: #fff; }</style>", unsafe_allow_html=True)

# 2. AUTO-REFRESH (Every 60 seconds for higher precision)
st_autorefresh(interval=60000, key="global_lock_v12")

# 3. LIVE TICKER TAPE
components.html("""
<div class="tradingview-widget-container">
  <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-ticker-nfp.js" async>
  { "symbols": [{"proName": "OANDA:XAUUSD", "title": "GOLD"},{"proName": "TVC:DXY", "title": "DXY"}], "colorTheme": "dark", "isTransparent": true }
  </script>
</div>""", height=50)

# 4. NEWS COUNTDOWN
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

# 5. FIXED RATING ENGINE (More sensitive to bias)
def get_deep_rating():
    tfs = [Interval.INTERVAL_1_MINUTE, Interval.INTERVAL_5_MINUTES, Interval.INTERVAL_15_MINUTES, 
           Interval.INTERVAL_1_HOUR, Interval.INTERVAL_4_HOURS, Interval.INTERVAL_1_DAY]
    buys, sells, neutral = 0, 0, 0
    tf_results = {}
    try:
        for tf in tfs:
            h = TA_Handler(symbol="XAUUSD", screener="forex", exchange="OANDA", interval=tf)
            a = h.get_analysis()
            buys += a.summary['BUY']
            sells += a.summary['SELL']
            neutral += a.summary['NEUTRAL']
            tf_results[tf] = a.summary['RECOMMENDATION']
        
        # New weighted calculation to avoid "5.0" stalemate
        total = buys + sells + (0.5 * neutral)
        raw_score = (buys + (0.25 * neutral)) / (buys + sells + neutral) if (buys + sells + neutral) > 0 else 0.5
        score = round(raw_score * 10, 1)
        
        if score > 5.5: act, col = "🔥 LOOK FOR BUY", "#00FF88"
        elif score < 4.5: act, col = "🧊 LOOK FOR SELL", "#FF4B4B"
        else: act, col = "⚖️ WAIT / NEUTRAL", "#888"
        return score, act, col, tf_results
    except: return 5.0, "SYNCING...", "#888", {}

score, action, m_col, all_tf = get_deep_rating()
news_msg, news_col = get_news_countdown()

# 6. TOP HUD (News)
st.markdown(f"<div style='text-align:center; padding:10px; border-radius:10px; border: 2px solid {news_col}; color:{news_col}; font-weight:bold;'>{news_msg}</div>", unsafe_allow_html=True)

# 7. SIDEBAR (The Global Rating UI)
st.sidebar.markdown(f"""
<div style="text-align:center; padding:15px; border: 3px solid {m_col}; border-radius:15px; background: rgba(255,255,255,0.05);">
    <p style="margin:0; color:#888;">AI GLOBAL RATING</p>
    <h1 style="color:{m_col}; margin:0; font-size: 55px;">{score}</h1>
    <h2 style="color:{m_col}; margin:0;">{action}</h2>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.write("📈 **TREND STRENGTH**")
st.sidebar.progress(score / 10.0)

st.sidebar.subheader("⏳ TF SCANNER")
for tf, rec in all_tf.items():
    st.sidebar.write(f"**{tf.replace('_',' ')}**: {rec}")

# 8. GAUGES (XAUUSD & DXY Summary)
st.markdown("### 📊 LIVE SUMMARY GAUGES")
col_g, col_d = st.columns(2)
with col_g:
    st.markdown("<h4 style='text-align:center;'>GOLD 15M GAUGE</h4>", unsafe_allow_html=True)
    components.html('<script src="https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js" async>{ "interval": "15m", "width": "100%", "height": "380", "isTransparent": true, "symbol": "OANDA:XAUUSD", "showIntervalTabs": true, "colorTheme": "dark" }</script>', height=390)
with col_d:
    st.markdown("<h4 style='text-align:center;'>DXY 15M GAUGE</h4>", unsafe_allow_html=True)
    components.html('<script src="https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js" async>{ "interval": "15m", "width": "100%", "height": "380", "isTransparent": true, "symbol": "TVC:DXY", "showIntervalTabs": true, "colorTheme": "dark" }</script>', height=390)

# 9. SMC MASTER CHART
st.subheader("📊 PATRO SMC TERMINAL")
components.html(f"""
<div style="height:700px;">
  <div id="tv_chart"></div>
  <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
  <script type="text/javascript">
  new TradingView.widget({{"autosize": true, "symbol": "OANDA:XAUUSD", "interval": "1", "theme": "dark", "style": "1", "container_id": "tv_chart", "show_popup_button": true, "studies": ["STD;Fair_Value_Gap", "STD;Order_Block", "STD;Pivot_Points_High_Low", "STD;VWAP"]}});
  </script>
</div>""", height=710)
