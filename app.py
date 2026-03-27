import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import pytz
from tradingview_ta import TA_Handler, Interval
from streamlit_autorefresh import st_autorefresh
import streamlit.components.v1 as components

# 1. PAGE SETUP
st.set_page_config(page_title="PATRO AI PRO V12.9.0", layout="wide")
st.markdown("<style>.stApp { background: #000; color: #fff; }</style>", unsafe_allow_html=True)

# 2. AUTO-REFRESH (Every 60 seconds)
st_autorefresh(interval=60000, key="global_sync_v129")

# 3. LIVE TICKER TAPE (Header)
components.html("""
<div class="tradingview-widget-container">
  <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-ticker-nfp.js" async>
  { "symbols": [
    {"proName": "OANDA:XAUUSD", "title": "GOLD"},
    {"proName": "TVC:DXY", "title": "DXY"},
    {"proName": "OANDA:GBPUSD", "title": "GBP/USD"}
  ], "colorTheme": "dark", "isTransparent": true }
  </script>
</div>""", height=50)

# 4. NEWS COUNTDOWN ENGINE
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
        return "✅ NO HIGH IMPACT USD NEWS", "#00FF88"
    except: return "📡 NEWS FEED BUSY", "#888"

# 5. RATING ENGINE (Multi-Timeframe 1m to 1D)
def get_market_rating():
    intervals = {
        "1m": Interval.INTERVAL_1_MINUTE, "5m": Interval.INTERVAL_5_MINUTES,
        "15m": Interval.INTERVAL_15_MINUTES, "1h": Interval.INTERVAL_1_HOUR,
        "4h": Interval.INTERVAL_4_HOURS, "1D": Interval.INTERVAL_1_DAY
    }
    buys, sells, neut = 0, 0, 0
    tf_summary = {}
    try:
        for label, itv in intervals.items():
            handler = TA_Handler(symbol="XAUUSD", screener="forex", exchange="OANDA", interval=itv)
            analysis = handler.get_analysis()
            b, s, n = analysis.summary['BUY'], analysis.summary['SELL'], analysis.summary['NEUTRAL']
            buys += b; sells += s; neut += n
            tf_summary[label] = analysis.summary['RECOMMENDATION']
        
        # Calculation for dynamic rating (0-10)
        total = buys + sells + neut
        raw_score = (buys + (0.4 * neut)) / total if total > 0 else 0.5
        score = round(raw_score * 10, 1)
        
        if score > 5.2: act, col = "🔥 LOOK FOR BUY", "#00FF88"
        elif score < 4.8: act, col = "🧊 LOOK FOR SELL", "#FF4B4B"
        else: act, col = "⚖️ WAIT / NEUTRAL", "#FFA500"
        return score, act, col, tf_summary
    except: return 5.0, "SYNCING...", "#888", {}

# Data Pull
score, action, m_color, tf_map = get_market_rating()
news_text, news_color = get_news_countdown()

# 6. TOP HUD (News)
st.markdown(f"""
    <div style="text-align:center; padding:10px; border-radius:10px; background:rgba(255,255,255,0.05); border: 2.5px solid {news_color}; margin-bottom: 20px;">
        <h3 style="margin:0; color:{news_color};">{news_text}</h3>
    </div>
""", unsafe_allow_html=True)

# 7. SIDEBAR (Rating & TF Scanner)
st.sidebar.markdown(f"""
<div style="text-align:center; padding:15px; border: 3px solid {m_color}; border-radius:15px; background: rgba(0,0,0,0.3);">
    <p style="margin:0; color:#888;">AI GLOBAL RATING</p>
    <h1 style="color:{m_color}; margin:0; font-size: 55px;">{score}</h1>
    <h3 style="color:{m_color}; margin:0;">{action}</h3>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.subheader("⏳ TIMEFRAME STATUS")
for tf, rec in tf_map.items():
    c = "#00FF88" if "BUY" in rec else "#FF4B4B" if "SELL" in rec else "#888"
    st.sidebar.markdown(f"**{tf}**: <span style='color:{c}'>{rec}</span>", unsafe_allow_html=True)

# 8. GAUGES (XAUUSD & DXY Summary)
st.markdown("### 📊 TECHNICAL SUMMARY GAUGES")
col_g, col_d = st.columns(2)
with col_g:
    st.markdown("<h4 style='text-align:center; color:#00FF88;'>GOLD (XAUUSD) 15M</h4>", unsafe_allow_html=True)
    components.html('<script src="https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js" async>{ "interval": "15m", "width": "100%", "height": "400", "isTransparent": true, "symbol": "OANDA:XAUUSD", "showIntervalTabs": true, "colorTheme": "dark" }</script>', height=410)
with col_d:
    st.markdown("<h4 style='text-align:center; color:#FF4B4B;'>DOLLAR (DXY) 15M</h4>", unsafe_allow_html=True)
    components.html('<script src="https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js" async>{ "interval": "15m", "width": "100%", "height": "400", "isTransparent": true, "symbol": "TVC:DXY", "showIntervalTabs": true, "colorTheme": "dark" }</script>', height=410)

# 9. THE SMC MASTER CHART
st.markdown("---")
st.subheader("📊 PATRO SMC TERMINAL")
components.html(f"""
<div style="height:750px;">
  <div id="tv_main"></div>
  <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
  <script type="text/javascript">
  new TradingView.widget({{
    "autosize": true, "symbol": "OANDA:XAUUSD", "interval": "15", "theme": "dark", "style": "1",
    "container_id": "tv_main", "show_popup_button": true,
    "studies": ["STD;Fair_Value_Gap", "STD;Order_Block", "STD;Pivot_Points_High_Low", "STD;VWAP"]
  }});
  </script>
</div>""", height=760)
