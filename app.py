import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import pytz
from tradingview_ta import TA_Handler, Interval
from streamlit_autorefresh import st_autorefresh
import streamlit.components.v1 as components

# 1. PAGE SETUP (Black Professional Theme)
st.set_page_config(page_title="PATRO AI PRO V12.6.8", layout="wide")
st.markdown("<style>.stApp { background: #000; color: #fff; }</style>", unsafe_allow_html=True)

# 2. AUTO-REFRESH (60 Seconds for High-Speed Signals)
st_autorefresh(interval=60000, key="global_refresh_lock")

# 3. LIVE TICKER TAPE (Header)
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

# 4. NEWS COUNTDOWN ENGINE (High Impact Only)
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

# 5. DEEP SCANNER (Moving Score + SMC Buy/Sell Logic)
def get_market_analysis():
    tfs = {
        "1m": Interval.INTERVAL_1_MINUTE, "5m": Interval.INTERVAL_5_MINUTES, 
        "15m": Interval.INTERVAL_15_MINUTES, "1h": Interval.INTERVAL_1_HOUR, 
        "4h": Interval.INTERVAL_4_HOURS, "1D": Interval.INTERVAL_1_DAY
    }
    total_points = 0
    tf_details = {}
    try:
        for label, tf in tfs.items():
            handler = TA_Handler(symbol="XAUUSD", screener="forex", exchange="OANDA", interval=tf)
            analysis = handler.get_analysis()
            rec = analysis.summary['RECOMMENDATION']
            tf_details[label] = rec
            if "STRONG_BUY" in rec: total_points += 2
            elif "BUY" in rec: total_points += 1
            elif "STRONG_SELL" in rec: total_points -= 2
            elif "SELL" in rec: total_points -= 1
        
        # Sensitive Math ensures 5.0 is almost never stuck
        score = round(5 + (total_points / 12 * 5), 1)
        
        # SMC NOW Logic (Alignment)
        smc_buy = "BUY" in tf_details["15m"] and "BUY" in tf_details["1h"]
        smc_sell = "SELL" in tf_details["15m"] and "SELL" in tf_details["1h"]

        if smc_buy and score > 5.2: action, color = "🚀 BUY NOW", "#00FF88"
        elif smc_sell and score < 4.8: action, color = "📉 SELL NOW", "#FF4B4B"
        else: action, color = "⚖️ NEUTRAL / WAIT", "#FFA500"
        return score, action, color, tf_details
    except: return 5.0, "SYNCING...", "#888", {}

score, action, m_color, tf_map = get_market_analysis()
news_text, news_color = get_news_countdown()

# 6. TOP HUD (News Countdown)
st.markdown(f"""
    <div style="text-align:center; padding:12px; border-radius:10px; background:rgba(255,255,255,0.05); border: 2px solid {news_color}; margin-bottom: 20px;">
        <h3 style="margin:0; color:{news_color};">{news_text}</h3>
    </div>
""", unsafe_allow_html=True)

# 7. SIDEBAR (AI Signal & Dashboard)
st.sidebar.markdown(f"""
<div style="text-align:center; padding:15px; border: 3px solid {m_color}; border-radius:15px; background: rgba(0,0,0,0.3); box-shadow: 0px 0px 10px {m_color}55;">
    <p style="margin:0; color:#888;">AI SMC SIGNAL</p>
    <h1 style="color:{m_color}; margin:0; font-size: 40px;">{action}</h1>
    <h2 style="color:{m_color}; margin:0;">{score}</h2>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.write("📈 **MOMENTUM STRENGTH**")
st.sidebar.progress(score / 10.0)

# 8. THE GAUGES (XAUUSD & DXY)
st.markdown("### 📊 MARKET SUMMARY GAUGES")
col_g, col_d = st.columns(2)
with col_g:
    st.markdown("<h4 style='text-align:center; color:#00FF88;'>GOLD SUMMARY</h4>", unsafe_allow_html=True)
    components.html("""<iframe src="https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js?{"interval":"15m","width":"100%","height":"350","isTransparent":true,"symbol":"OANDA:XAUUSD","showIntervalTabs":true,"displayMode":"single","colorTheme":"dark"} " height="360" width="100%" style="border:none;"></iframe>""", height=360)
with col_d:
    st.markdown("<h4 style='text-align:center; color:#FF4B4B;'>DXY SUMMARY</h4>", unsafe_allow_html=True)
    components.html("""<iframe src="https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js?{"interval":"15m","width":"100%","height":"350","isTransparent":true,"symbol":"TVC:DXY","showIntervalTabs":true,"displayMode":"single","colorTheme":"dark"} " height="360" width="100%" style="border:none;"></iframe>""", height=360)

# 9. THE SMC MASTER CHART (TradingView Inside + Pop View)
st.markdown("---")
st.subheader("📊 PATRO SMC TERMINAL (XAUUSD)")
components.html(f"""
<div id="tv_main_chart" style="height:750px;"></div>
<script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
<script type="text/javascript">
new TradingView.widget({{
  "autosize": true, "symbol": "OANDA:XAUUSD", "interval": "15", "theme": "dark", "style": "1",
  "container_id": "tv_main_chart", 
  "show_popup_button": true,      # POP VIEW IS HERE
  "popup_width": "1000",
  "popup_height": "650",
  "withdateranges": true,
  "allow_symbol_change": true,
  "studies": ["STD;Fair_Value_Gap", "STD;Order_Block", "STD;Pivot_Points_High_Low", "STD;VWAP"]
}});
</script>""", height=760)

# 10. POSITION SIZER (Sidebar Bottom)
st.sidebar.markdown("---")
st.sidebar.subheader("🛡️ POSITION SIZER")
bal = st.sidebar.number_input("Balance", value=1000)
risk = st.sidebar.slider("Risk %", 0.5, 5.0, 1.0)
sl = st.sidebar.number_input("SL Pips", value=30)
st.sidebar.info(f"🔥 USE LOT: {round((bal*(risk/100))/(sl*10), 2)}")
