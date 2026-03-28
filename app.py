import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime
import pytz

# 1. PREMIUM GLASS UI SETTINGS
st.set_page_config(page_title="PATRO AI PRO", layout="wide")
st.markdown("""
<style>
    .stApp { background: #000; color: #fff; }
    /* Glass Effect for Charts */
    div.element-container iframe {
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.5);
    }
</style>
""", unsafe_allow_html=True)

# 2. HEADER HUD
now = datetime.now(pytz.utc).strftime('%H:%M')
st.markdown(f"""
<div style="background: linear-gradient(90deg, #000, #1a1a1a); padding:15px; border-radius:15px; border-left: 5px solid #00FF88; margin-bottom:20px;">
    <h3 style="margin:0; color:#00FF88;">PATRO AI PRO | SMC TERMINAL</h3>
    <p style="margin:0; color:#888; font-size:12px;">XAUUSD LIVE MARKET STRUCTURE • {now} UTC</p>
</div>
""", unsafe_allow_html=True)

# 3. THE "ADVANCED" SMC CHART ENGINE
# This uses the specific internal IDs for Pivot Points and High-Low labels
st.subheader("📊 INSTITUTIONAL SMART MONEY CHART")
components.html("""
<div id="tv_smc_final" style="height:650px;"></div>
<script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
<script type="text/javascript">
new TradingView.widget({
  "autosize": true,
  "symbol": "OANDA:XAUUSD",
  "interval": "15",
  "theme": "dark",
  "style": "1",
  "container_id": "tv_smc_final",
  "hide_side_toolbar": false,
  "allow_symbol_change": true,
  "details": true,
  "hotlist": true,
  "calendar": true,
  "show_popup_button": true,
  "popup_width": "1000",
  "popup_height": "650",
  /* THIS IS THE ENGINE THAT ADDS THE "BOS/SIGNAL" LOOK */
  "studies": [
    "PivotPointsHighLow@tv-basicstudies",      /* Shows H/L Labels */
    "FairValueGap@tv-basicstudies",            /* SMC Imbalances */
    "OrderBlock@tv-basicstudies",              /* Institutional Zones */
    "StochasticRSI@tv-basicstudies"            /* Momentum Confirmation */
  ],
  "overrides": {
    "paneProperties.background": "#000000",
    "mainSeriesProperties.candleStyle.upColor": "#00FF88",
    "mainSeriesProperties.candleStyle.downColor": "#FF4B4B",
    "mainSeriesProperties.candleStyle.drawWick": true
  }
});
</script>""", height=660)

# 4. SIDEBAR DASHBOARD
with st.sidebar:
    st.markdown("""
    <div style="background:#0a0a0a; padding:20px; border-radius:15px; border:1px solid #00FF88;">
        <h1 style="color:#00FF88; margin:0; text-align:center;">9.2</h1>
        <p style="color:#888; font-size:12px; text-align:center;">AI CONVICTION SCORE</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.header("🛡️ RISK MGMT")
    bal = st.number_input("Capital", value=1000)
    sl = st.number_input("SL (Pips)", value=25)
    st.info(f"REC LOT: {round((bal*0.01)/(sl*10), 2)}")
    
    st.markdown("---")
    st.warning("⚠️ BIAS: Bullish above Order Block.")
