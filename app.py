import streamlit as st
import requests
from datetime import datetime
import pytz
from tradingview_ta import TA_Handler, Interval
from streamlit_autorefresh import st_autorefresh
import streamlit.components.v1 as components

# 1. THEME & HEADER
st.set_page_config(page_title="PATRO AI PRO V12.7.5", layout="wide")
st.markdown("<style>.stApp { background: #000; color: #fff; }</style>", unsafe_allow_html=True)

# 2. AUTO-REFRESH (Keep everything live)
st_autorefresh(interval=60000, key="global_sync_v12")

# 3. FUTURE FEATURE: HIGH-IMPACT NEWS COUNTDOWN
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
                return f"⚠️ {n['title']} in {h}h {mn}m", "#FF4B4B"
        return "✅ NO PENDING USD NEWS", "#00FF88"
    except: return "📡 NEWS FEED SYNCING", "#888"

news_txt, news_col = get_news()

# 4. FUTURE FEATURE: MULTI-TIMEFRAME MOMENTUM SCORE
def get_deep_analysis():
    tfs = {"1m": Interval.INTERVAL_1_MINUTE, "15m": Interval.INTERVAL_15_MINUTES, "1h": Interval.INTERVAL_1_HOUR, "4h": Interval.INTERVAL_4_HOURS}
    points = 0
    results = {}
    try:
        for lab, tf in tfs.items():
            handler = TA_Handler(symbol="XAUUSD", screener="forex", exchange="OANDA", interval=tf)
            res = handler.get_analysis().summary['RECOMMENDATION']
            results[lab] = res
            if "STRONG_BUY" in res: points += 2.5
            elif "BUY" in res: points += 1.5
            elif "STRONG_SELL" in res: points -= 2.5
            elif "SELL" in res: points -= 1.5
        
        final_score = round(5 + points, 1)
        final_score = max(0, min(10, final_score)) # Keep between 0-10
        
        # SMC Alignment Logic
        if "BUY" in results["15m"] and "BUY" in results["1h"]: action, color = "🚀 BUY NOW", "#00FF88"
        elif "SELL" in results["15m"] and "SELL" in results["1h"]: action, color = "📉 SELL NOW", "#FF4B4B"
        else: action, color = "⚖️ NEUTRAL", "#FFA500"
        
        return final_score, action, color
    except: return 5.0, "SYNCING", "#888"

score, action, m_color = get_deep_analysis()

# --- UI LAYOUT ---

# Top Banner (News)
st.markdown(f"""<div style="text-align:center; padding:10px; border-radius:10px; border:2px solid {news_col}; background:rgba(0,0,0,0.5);"><h3 style="margin:0; color:{news_col};">{news_txt}</h3></div>""", unsafe_allow_html=True)

# Sidebar (Signal + Score + Risk)
with st.sidebar:
    st.markdown(f"""<div style="text-align:center; padding:20px; border:3px solid {m_color}; border-radius:15px; background:rgba(0,0,0,0.4); box-shadow: 0px 0px 15px {m_color}44;">
        <h2 style="margin:0; color:{m_color};">{action}</h2>
        <h1 style="margin:0; font-size:50px; color:{m_color};">{score}</h1>
        <p style="color:#888;">AI CONFIDENCE SCORE</p>
    </div>""", unsafe_allow_html=True)
    
    st.markdown("---")
    st.subheader("🛡️ POSITION SIZER")
    bal = st.number_input("Balance ($)", value=1000)
    risk = st.slider("Risk %", 0.5, 3.0, 1.0)
    sl = st.number_input("Stop Loss (Pips)", value=25)
    st.success(f"🔥 REC LOT: {round((bal*(risk/100))/(sl*10), 2)}")

# 5. THE CHART (WITH BUY/SELL + POP-UP + SMC)
st.subheader("📊 PATRO SMC MASTER TERMINAL")
components.html(f"""
<div id="tradingview_full" style="height:750px;"></div>
<script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
<script type="text/javascript">
new TradingView.widget({{
  "autosize": true, "symbol": "OANDA:XAUUSD", "interval": "15", "theme": "dark", "style": "1",
  "container_id": "tradingview_full",
  "show_popup_button": true,  # POP VIEW IS BACK
  "withdateranges": true, "allow_symbol_change": true, "details": true, "hotlist": true, "calendar": true,
  "studies": [
    "STD;Pivot_Points_High_Low", # DRAWS BUY/SELL PIVOT LABELS
    "STD;Fair_Value_Gap",        # SMC GAPS
    "STD;Order_Block",           # SMC BLOCKS
    "STD;VWAP"                   # INSTITUTIONAL PRICE
  ]
}});
</script>""", height=760)

# 6. GAUGES (Bottom)
col1, col2 = st.columns(2)
with col1:
    components.html("""<iframe src="https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js?{"interval":"15m","width":"100%","height":"350","isTransparent":true,"symbol":"OANDA:XAUUSD","showIntervalTabs":true,"displayMode":"single","colorTheme":"dark"}" height="360" width="100%" style="border:none;"></iframe>""", height=360)
with col2:
    components.html("""<iframe src="https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js?{"interval":"15m","width":"100%","height":"350","isTransparent":true,"symbol":"TVC:DXY","showIntervalTabs":true,"displayMode":"single","colorTheme":"dark"}" height="360" width="100%" style="border:none;"></iframe>""", height=360)
