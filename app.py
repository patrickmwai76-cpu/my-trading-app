import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import pytz
from tradingview_ta import TA_Handler, Interval
from streamlit_autorefresh import st_autorefresh
import streamlit.components.v1 as components

# 1. PAGE SETUP & THEME
st.set_page_config(page_title="PATRO AI PRO V12.8.0", layout="wide")
st.markdown("""
    <style>
    .stApp { background: #000; color: #fff; }
    div[data-testid="stMetricValue"] { font-size: 45px; }
    .sidebar .sidebar-content { background-image: linear-gradient(#111,#000); }
    </style>
    """, unsafe_allow_html=True)

# 2. AUTO-REFRESH (Every 60 seconds)
st_autorefresh(interval=60000, key="patro_full_sync")

# 3. GLOBAL TICKER TAPE (Header)
components.html("""
<div class="tradingview-widget-container">
  <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-ticker-nfp.js" async>
  { "symbols": [
    {"proName": "OANDA:XAUUSD", "title": "GOLD"},
    {"proName": "TVC:DXY", "title": "DXY"},
    {"proName": "OANDA:GBPUSD", "title": "GBP/USD"},
    {"proName": "FX_IDC:USDCNY", "title": "USD/CNY"}
  ], "colorTheme": "dark", "isTransparent": true }
  </script>
</div>""", height=50)

# 4. HIGH-IMPACT NEWS TRACKER
def get_news():
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
                return f"🔔 {n['title']} in {h}h {mn}m", "#FF4B4B"
        return "✅ NO HIGH IMPACT NEWS REMAINING", "#00FF88"
    except: return "📡 NEWS SYNCING...", "#888"

news_txt, news_col = get_news()
st.markdown(f"<div style='text-align:center; padding:10px; border:1px solid {news_col}; border-radius:5px; color:{news_col}; font-weight:bold;'>{news_txt}</div>", unsafe_allow_html=True)

# 5. ENHANCED RATING ENGINE (Fixes the 5.0 Stalemate)
def get_weighted_rating():
    tfs = [Interval.INTERVAL_1_MINUTE, Interval.INTERVAL_5_MINUTES, Interval.INTERVAL_15_MINUTES, 
           Interval.INTERVAL_1_HOUR, Interval.INTERVAL_4_HOURS, Interval.INTERVAL_1_DAY]
    buys, sells, neutral = 0, 0, 0
    detailed_recs = {}
    try:
        for tf in tfs:
            handler = TA_Handler(symbol="XAUUSD", screener="forex", exchange="OANDA", interval=tf)
            analysis = handler.get_analysis()
            buys += analysis.summary['BUY']
            sells += analysis.summary['SELL']
            neutral += analysis.summary['NEUTRAL']
            detailed_recs[tf] = analysis.summary['RECOMMENDATION']
        
        # Weighted logic to ensure movement (5.0 fix)
        total_signals = buys + sells + neutral
        raw_score = (buys + (0.3 * neutral)) / total_signals if total_signals > 0 else 0.5
        score = round(raw_score * 10, 1)
        
        if score > 5.5: status, color = "STRONG BUY BIAS", "#00FF88"
        elif score < 4.5: status, color = "STRONG SELL BIAS", "#FF4B4B"
        else: status, color = "NEUTRAL / ACCUMULATION", "#FFA500"
        
        return score, status, color, detailed_recs
    except: return 5.0, "OFFLINE", "#888", {}

score, status, m_color, tf_data = get_weighted_rating()

# 6. SIDEBAR - GLOBAL RATING & TREND
st.sidebar.markdown(f"""
    <div style="text-align:center; border:2px solid {m_color}; border-radius:15px; padding:20px; background:rgba(0,0,0,0.5);">
        <h3 style="color:#888; margin:0;">GLOBAL RATING</h3>
        <h1 style="color:{m_color}; font-size:60px; margin:0;">{score}</h1>
        <p style="color:{m_color}; font-weight:bold;">{status}</p>
    </div>
    """, unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.subheader("🕒 TIMEFRAME SCANNER")
for tf, rec in tf_data.items():
    st.sidebar.write(f"**{tf.replace('INTERVAL_','')}**: {rec}")

# 7. GAUGES SECTION (XAUUSD & DXY)
st.markdown("### 📊 TECHNICAL SUMMARY GAUGES")
col1, col2 = st.columns(2)
with col1:
    st.markdown("<p style='text-align:center;'>GOLD (XAUUSD)</p>", unsafe_allow_html=True)
    components.html('<script src="https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js" async>{ "interval": "15m", "width": "100%", "height": "350", "isTransparent": true, "symbol": "OANDA:XAUUSD", "showIntervalTabs": true, "colorTheme": "dark" }</script>', height=360)
with col2:
    st.markdown("<p style='text-align:center;'>DOLLAR INDEX (DXY)</p>", unsafe_allow_html=True)
    components.html('<script src="https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js" async>{ "interval": "15m", "width": "100%", "height": "350", "isTransparent": true, "symbol": "TVC:DXY", "showIntervalTabs": true, "colorTheme": "dark" }</script>', height=360)

# 8. SMC MASTER TERMINAL
st.markdown("### 🏹 SMC MASTER TERMINAL")
components.html("""
<div style="height:700px;">
  <div id="tv_chart_smc"></div>
  <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
  <script type="text/javascript">
  new TradingView.widget({
    "autosize": true,
    "symbol": "OANDA:XAUUSD",
    "interval": "15",
    "timezone": "Etc/UTC",
    "theme": "dark",
    "style": "1",
    "locale": "en",
    "toolbar_bg": "#f1f3f6",
    "enable_publishing": false,
    "hide_side_toolbar": false,
    "allow_symbol_change": true,
    "container_id": "tv_chart_smc",
    "studies": [
      "STD;Fair_Value_Gap",
      "STD;Order_Block",
      "STD;Pivot_Points_High_Low"
    ]
  });
  </script>
</div>""", height=710)
