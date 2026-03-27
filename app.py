import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import pytz
from tradingview_ta import TA_Handler, Interval
from streamlit_autorefresh import st_autorefresh
import streamlit.components.v1 as components

# 1. PAGE SETUP (Black Theme) - UNCHANGED
st.set_page_config(page_title="PATRO AI PRO V12.6.1", layout="wide")
st.markdown("<style>.stApp { background: #000; color: #fff; }</style>", unsafe_allow_html=True)

# 2. AUTO-REFRESH - UNCHANGED
st_autorefresh(interval=120000, key="global_refresh_lock")

# 3. LIVE TICKER TAPE - UNCHANGED
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

# 4. NEWS COUNTDOWN ENGINE - UNCHANGED
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
                return f"⏳ NEWS: {n['title']} in {h}h {mn}m", "#FFA500"
        return "✅ NO HIGH IMPACT USD NEWS", "#00FF88"
    except: return "📡 NEWS FEED BUSY", "#888"

# 5. DEEP SCANNER - UPDATED RATING LOGIC ONLY
def get_market_analysis():
    tfs = {
        "1m": Interval.INTERVAL_1_MINUTE, "5m": Interval.INTERVAL_5_MINUTES, 
        "15m": Interval.INTERVAL_15_MINUTES, "1h": Interval.INTERVAL_1_HOUR, 
        "4h": Interval.INTERVAL_4_HOURS, "1D": Interval.INTERVAL_1_DAY
    }
    buys, sells, neutrals = 0, 0, 0
    tf_details = {}
    try:
        for label, tf in tfs.items():
            handler = TA_Handler(symbol="XAUUSD", screener="forex", exchange="OANDA", interval=tf)
            analysis = handler.get_analysis()
            
            # Grabbing full signal spectrum
            b = analysis.summary['BUY']
            s = analysis.summary['SELL']
            n = analysis.summary['NEUTRAL']
            
            buys += b
            sells += s
            neutrals += n
            tf_details[label] = analysis.summary['RECOMMENDATION']
        
        # IMPROVED FORMULA: Uses all signals so it's not stuck at 5.0
        total_signals = buys + sells + neutrals
        if total_signals > 0:
            # Score logic: (Buys + half of Neutrals) / Total * 10
            # This ensures the rating moves even if the market is indecisive
            score = round(((buys + (0.5 * neutrals)) / total_signals) * 10, 1)
        else:
            score = 5.0

        # Action logic adjusted for the new formula sensitivity
        if score > 6.0: action, color = "🔥 LOOK FOR BUY", "#00FF88"
        elif score < 4.0: action, color = "🧊 LOOK FOR SELL", "#FF4B4B"
        else: action, color = "⚖️ WAIT / NEUTRAL", "#FFA500"
        
        return score, action, color, tf_details
    except: return 5.0, "SYNCING...", "#888", {}

# Data Fetch
score, action, m_color, tf_map = get_market_analysis()
news_text, news_color = get_news_countdown()

# 6. TOP HUD - UNCHANGED
st.markdown(f"""
    <div style="text-align:center; padding:12px; border-radius:10px; background:rgba(255,255,255,0.05); border: 2px solid {news_color}; margin-bottom: 20px;">
        <h3 style="margin:0; color:{news_color};">{news_text}</h3>
    </div>
""", unsafe_allow_html=True)

# 7. SIDEBAR - UNCHANGED
st.sidebar.markdown(f"""
<div style="text-align:center; padding:15px; border: 3px solid {m_color}; border-radius:15px; background: rgba(0,0,0,0.3);">
    <p style="margin:0; color:#888;">AI GLOBAL RATING</p>
    <h1 style="color:{m_color}; margin:0; font-size: 50px;">{score}</h1>
    <h3 style="color:{m_color}; margin:0;">{action}</h3>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.write("📈 **MOMENTUM STRENGTH**")
st.sidebar.progress(score / 10.0)

st.sidebar.subheader("⏳ TIMEFRAME STATUS")
for tf, rec in tf_map.items():
    c = "#00FF88" if "BUY" in rec else "#FF4B4B" if "SELL" in rec else "#888"
    st.sidebar.markdown(f"**{tf}**: <span style='color:{c}'>{rec}</span>", unsafe_allow_html=True)

# 8. THE GAUGES - UNCHANGED
st.markdown("### 📊 MARKET SUMMARY GAUGES")
col_g, col_d = st.columns(2)

with col_g:
    st.markdown("<h4 style='text-align:center; color:#00FF88;'>GOLD (XAUUSD) SUMMARY</h4>", unsafe_allow_html=True)
    components.html("""
    <div class="tradingview-widget-container">
      <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js" async>
      { "interval": "15m", "width": "100%", "height": "400", "isTransparent": true, "symbol": "OANDA:XAUUSD", "showIntervalTabs": true, "displayMode": "single", "colorTheme": "dark" }
      </script>
    </div>""", height=410)

with col_d:
    st.markdown("<h4 style='text-align:center; color:#FF4B4B;'>DOLLAR (DXY) SUMMARY</h4>", unsafe_allow_html=True)
    components.html("""
    <div class="tradingview-widget-container">
      <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js" async>
      { "interval": "15m", "width": "100%", "height": "400", "isTransparent": true, "symbol": "TVC:DXY", "showIntervalTabs": true, "displayMode": "single", "colorTheme": "dark" }
      </script>
    </div>""", height=410)

# 9. THE SMC MASTER CHART - UNCHANGED
st.markdown("---")
st.subheader("📊 PATRO SMC TERMINAL")
components.html(f"""
<div style="height:750px;">
  <div id="tv_main_chart"></div>
  <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
  <script type="text/javascript">
  new TradingView.widget({{
    "autosize": true, "symbol": "OANDA:XAUUSD", "interval": "15", "theme": "dark", "style": "1",
    "container_id": "tv_main_chart", 
    "show_popup_button": true,
    "withdateranges": true,
    "allow_symbol_change": true,
    "studies": ["STD;Fair_Value_Gap", "STD;Order_Block", "STD;Pivot_Points_High_Low", "STD;VWAP"]
  }});
  </script>
</div>""", height=760)

# 10. RISK CALCULATOR - UNCHANGED
st.sidebar.markdown("---")
st.sidebar.subheader("🛡️ POSITION SIZER")
bal = st.sidebar.number_input("Balance", value=1000)
risk = st.sidebar.slider("Risk %", 0.5, 5.0, 1.0)
sl = st.sidebar.number_input("SL Pips", value=30)
st.sidebar.info(f"🔥 USE LOT: {round((bal*(risk/100))/(sl*10), 2)}")
