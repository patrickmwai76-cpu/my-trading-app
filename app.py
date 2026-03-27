import streamlit as st
import requests
from datetime import datetime
import pytz
from tradingview_ta import TA_Handler, Interval
from streamlit_autorefresh import st_autorefresh
import streamlit.components.v1 as components

# 1. THEME & HEADER (Institutional Black)
st.set_page_config(page_title="PATRO AI PRO V12.8.0", layout="wide")
st.markdown("<style>.stApp { background: #000; color: #fff; }</style>", unsafe_allow_html=True)

# 2. AUTO-REFRESH (High-Frequency Updates)
st_autorefresh(interval=60000, key="patro_full_sync")

# 3. FEATURE: LIVE NEWS TICKER (Restored)
def get_live_news():
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
                return f"🔥 {n['title']} in {h}h {mn}m", "#FF4B4B"
        return "✅ NO HIGH IMPACT NEWS", "#00FF88"
    except: return "📡 NEWS FEED CONNECTING...", "#888"

news_text, news_color = get_live_news()
st.markdown(f"<div style='text-align:center; padding:10px; border:2px solid {news_color}; border-radius:10px;'><h3>{news_text}</h3></div>", unsafe_allow_html=True)

# 4. FEATURE: MULTI-TF AI SCORE & SMC SIGNAL (Restored)
def get_ai_analysis():
    tfs = {"1m": Interval.INTERVAL_1_MINUTE, "15m": Interval.INTERVAL_15_MINUTES, "1h": Interval.INTERVAL_1_HOUR, "4h": Interval.INTERVAL_4_HOURS}
    points = 0
    tf_data = {}
    try:
        for lab, tf in tfs.items():
            handler = TA_Handler(symbol="XAUUSD", screener="forex", exchange="OANDA", interval=tf)
            analysis = handler.get_analysis().summary['RECOMMENDATION']
            tf_data[lab] = analysis
            if "STRONG_BUY" in analysis: points += 2.5
            elif "BUY" in analysis: points += 1.5
            elif "STRONG_SELL" in analysis: points -= 2.5
            elif "SELL" in analysis: points -= 1.5
        
        score = round(5 + points, 1)
        score = max(0, min(10, score))
        
        # SMC Alignment
        if "BUY" in tf_data["15m"] and "BUY" in tf_data["1h"]: action, color = "🚀 BUY NOW", "#00FF88"
        elif "SELL" in tf_data["15m"] and "SELL" in tf_data["1h"]: action, color = "📉 SELL NOW", "#FF4B4B"
        else: action, color = "⚖️ NEUTRAL", "#FFA500"
        
        return score, action, color
    except: return 5.0, "SYNCING", "#888"

ai_score, ai_action, ai_color = get_ai_analysis()

# 5. SIDEBAR COMMANDS (Signal + Risk + Branding)
with st.sidebar:
    st.markdown(f"""<div style='text-align:center; padding:20px; border:3px solid {ai_color}; border-radius:15px; background:rgba(0,0,0,0.5);'>
        <h2 style='color:{ai_color}; margin:0;'>{ai_action}</h2>
        <h1 style='font-size:55px; margin:0;'>{ai_score}</h1>
        <p style='color:#888;'>AI MOMENTUM SCORE</p>
    </div>""", unsafe_allow_html=True)
    
    st.markdown("---")
    st.subheader("🛡️ RISK MGMT")
    balance = st.number_input("Balance", value=1000)
    risk_pct = st.slider("Risk %", 0.5, 3.0, 1.0)
    sl_pips = st.number_input("SL Pips", value=30)
    st.success(f"🔥 REC LOT: {round((balance * (risk_pct/100)) / (sl_pips * 10), 2)}")

# 6. FEATURE: THE MASTER CHART (Restored with Pop-Up + On-Chart Signals)
st.subheader("📊 PATRO SMC MASTER TERMINAL")
components.html(f"""
<div id="tv_chart_v12" style="height:750px;"></div>
<script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
<script type="text/javascript">
new TradingView.widget({{
  "autosize": true, "symbol": "OANDA:XAUUSD", "interval": "15", "theme": "dark", "style": "1",
  "container_id": "tv_chart_v12",
  "show_popup_button": true, # POP VIEW ENABLED
  "withdateranges": true, "allow_symbol_change": true, "details": true, "hotlist": true, "calendar": true,
  "studies": [
    "STD;Pivot_Points_High_Low", # FORCES "H" & "L" BUY/SELL LABELS
    "STD;Fair_Value_Gap",        # SMC GAPS
    "STD;Order_Block",           # SMC BLOCKS
    "STD;Bollinger_Bands%B"     # MOMENTUM SIGNALS
  ]
}});
</script>""", height=760)

# 7. FEATURE: MARKET GAUGES (Restored)
col_gold, col_dxy = st.columns(2)
with col_gold:
    st.write("🪙 **GOLD 15M SUMMARY**")
    components.html("""<iframe src="https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js?{"interval":"15m","width":"100%","height":"350","isTransparent":true,"symbol":"OANDA:XAUUSD","showIntervalTabs":true,"displayMode":"single","colorTheme":"dark"}" height="360" width="100%" style="border:none;"></iframe>""", height=360)
with col_dxy:
    st.write("💵 **DXY 15M SUMMARY**")
    components.html("""<iframe src="https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js?{"interval":"15m","width":"100%","height":"350","isTransparent":true,"symbol":"TVC:DXY","showIntervalTabs":true,"displayMode":"single","colorTheme":"dark"}" height="360" width="100%" style="border:none;"></iframe>""", height=360)
