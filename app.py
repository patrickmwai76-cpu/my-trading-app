import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import pytz
from tradingview_ta import TA_Handler, Interval
from streamlit_autorefresh import st_autorefresh
import streamlit.components.v1 as components

# 1. PAGE SETUP & THEME
st.set_page_config(page_title="PATRO AI PRO V12.5.0", layout="wide")
st.markdown("<style>.stApp { background: #000; color: #fff; }</style>", unsafe_allow_html=True)

# 2. AUTO-REFRESH (Every 2 minutes)
st_autorefresh(interval=120000, key="global_sync")

# 3. LIVE PRICE FLOW (TICKER TAPE) - HOME TOP
components.html("""
<div class="tradingview-widget-container">
  <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-ticker-nfp.js" async>
  { "symbols": [
    {"proName": "OANDA:XAUUSD", "title": "GOLD"},
    {"proName": "TVC:DXY", "title": "DXY"},
    {"proName": "FX_IDC:GBPUSD", "title": "GBP/USD"}
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

# 5. ALL-TIMEFRAME DEEP SCANNER (1m to 1M)
def get_market_analysis():
    tfs = {
        "1m": Interval.INTERVAL_1_MINUTE, "5m": Interval.INTERVAL_5_MINUTES, 
        "15m": Interval.INTERVAL_15_MINUTES, "1h": Interval.INTERVAL_1_HOUR, 
        "4h": Interval.INTERVAL_4_HOURS, "1D": Interval.INTERVAL_1_DAY, "1W": Interval.INTERVAL_1_WEEK
    }
    buys, sells = 0, 0
    tf_details = {}
    try:
        for label, tf in tfs.items():
            handler = TA_Handler(symbol="XAUUSD", screener="forex", exchange="OANDA", interval=tf)
            analysis = handler.get_analysis()
            b, s = analysis.summary['BUY'], analysis.summary['SELL']
            buys += b; sells += s
            tf_details[label] = analysis.summary['RECOMMENDATION']
        
        score = round((buys / (buys + sells)) * 10, 1) if (buys + sells) > 0 else 5.0
        if score > 7.5: action, color = "🔥 LOOK FOR BUY", "#00FF88"
        elif score < 2.5: action, color = "🧊 LOOK FOR SELL", "#FF4B4B"
        else: action, color = "⚖️ WAIT / NEUTRAL", "#FFA500"
        return score, action, color, tf_details
    except: return 5.0, "SYNCING...", "#888", {}

# Data Fetching
score, action, m_color, tf_map = get_market_analysis()
news_text, news_color = get_news_countdown()

# 6. NEWS HUD
st.markdown(f"""
    <div style="text-align:center; padding:10px; border-radius:10px; background:rgba(255,255,255,0.05); border: 1.5px solid {news_color};">
        <h3 style="margin:0; color:{news_color};">{news_text}</h3>
    </div>
""", unsafe_allow_html=True)

# 7. SIDEBAR (Rating, Trend Bar, and Full Scan)
st.sidebar.markdown(f"""
<div style="text-align:center; padding:15px; border: 2px solid {m_color}; border-radius:15px;">
    <h1 style="color:{m_color}; margin:0;">{score}</h1>
    <h3 style="color:{m_color}; margin:0;">{action}</h3>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.write("📈 **TREND STRENGTH**")
st.sidebar.progress(score / 10.0)

st.sidebar.subheader("⏳ FULL INTERVAL SCAN")
for tf, rec in tf_map.items():
    c = "#00FF88" if "BUY" in rec else "#FF4B4B" if "SELL" in rec else "#888"
    st.sidebar.markdown(f"**{tf}**: <span style='color:{c}'>{rec}</span>", unsafe_allow_html=True)

# 8. GAUGES (GOLD & DXY)
col1, col2 = st.columns(2)
with col1:
    st.markdown("<h4 style='text-align:center;'>XAUUSD SUMMARY</h4>", unsafe_allow_html=True)
    components.html('<script src="https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js" async>{ "interval": "1m", "width": "100%", "height": "380", "isTransparent": true, "symbol": "OANDA:XAUUSD", "showIntervalTabs": true, "colorTheme": "dark" }</script>', height=390)
with col2:
    st.markdown("<h4 style='text-align:center;'>DXY SUMMARY</h4>", unsafe_allow_html=True)
    components.html('<script src="https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js" async>{ "interval": "1m", "width": "100%", "height": "380", "isTransparent": true, "symbol": "TVC:DXY", "showIntervalTabs": true, "colorTheme": "dark" }</script>', height=390)

# 9. THE SMC MASTER CHART (VWAP, Pivots, FVG + Popup)
st.subheader("📊 PATRO SMC TERMINAL")
components.html(f"""
<div style="height:700px;">
  <div id="tv_main"></div>
  <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
  <script type="text/javascript">
  new TradingView.widget({{
    "autosize": true, "symbol": "OANDA:XAUUSD", "interval": "1", "theme": "dark", "style": "1",
    "container_id": "tv_main", "show_popup_button": true,
    "studies": ["STD;Fair_Value_Gap", "STD;Order_Block", "STD;Pivot_Points_High_Low", "STD;VWAP"]
  }});
  </script>
</div>""", height=710)
