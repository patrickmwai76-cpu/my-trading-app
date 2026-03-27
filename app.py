import streamlit as st
import requests
from datetime import datetime
import pytz
from tradingview_ta import TA_Handler, Interval
from streamlit_autorefresh import st_autorefresh
import streamlit.components.v1 as components

# 1. THEME & HEADER
st.set_page_config(page_title="PATRO AI PRO V12.7.0", layout="wide")
st.markdown("<style>.stApp { background: #000; color: #fff; }</style>", unsafe_allow_html=True)

# 2. AUTO-REFRESH (Keep signals live)
st_autorefresh(interval=60000, key="global_sync")

# 3. LIVE PRICE TICKER
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

# 4. SMC AI ENGINE (Sidebar Signal)
def get_smc_signal():
    try:
        handler = TA_Handler(symbol="XAUUSD", screener="forex", exchange="OANDA", interval=Interval.INTERVAL_15_MINUTES)
        rec = handler.get_analysis().summary['RECOMMENDATION']
        if "STRONG_BUY" in rec: return "🚀 BUY NOW", "#00FF88"
        if "STRONG_SELL" in rec: return "📉 SELL NOW", "#FF4B4B"
        return "⚖️ WAIT / SMC SETUP", "#FFA500"
    except: return "📡 SYNCING", "#888"

action, m_color = get_smc_signal()

# 5. SIDEBAR: THE COMMAND CENTER
st.sidebar.markdown(f"""
<div style="text-align:center; padding:20px; border: 3px solid {m_color}; border-radius:15px; background: rgba(0,0,0,0.4); box-shadow: 0px 0px 15px {m_color}33;">
    <h3 style="margin:0; color:#888;">PATRO AI SIGNAL</h3>
    <h1 style="color:{m_color}; margin:10px 0; font-size:38px;">{action}</h1>
    <hr style="border:0.5px solid #333;">
    <p style="font-size:12px;">SMC 15M ALIGNMENT ACTIVE</p>
</div>
""", unsafe_allow_html=True)

# 6. THE CHART (WITH BUY/SELL LABELS & POP-UP)
st.subheader("📊 XAUUSD SMC MASTER TERMINAL")
components.html(f"""
<div id="tradingview_smc" style="height:750px;"></div>
<script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
<script type="text/javascript">
new TradingView.widget({{
  "autosize": true,
  "symbol": "OANDA:XAUUSD",
  "interval": "15",
  "theme": "dark",
  "style": "1",
  "container_id": "tradingview_smc",
  "show_popup_button": true,
  "popup_width": "1000",
  "popup_height": "650",
  "withdateranges": true,
  "allow_symbol_change": true,
  "details": true,
  "hotlist": true,
  "calendar": true,
  # ADDED SMC INDICATORS THAT DRAW LABELS ON CHART:
  "studies": [
    "STD;Pivot_Points_High_Low", # Displays H/L labels for Buy/Sell zones
    "STD;Fair_Value_Gap",        # Shows SMC "Gaps"
    "STD;Order_Block",           # Shows Institutional Entry Blocks
    "STD;VWAP"                   # Volume Weighted Price
  ]
}});
</script>
""", height=760)

# 7. MARKET DEPTH GAUGES (Back in position)
st.markdown("---")
col1, col2 = st.columns(2)
with col1:
    st.markdown("#### 🪙 GOLD 1H ANALYSIS")
    components.html("""<iframe src="https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js?{"interval":"1h","width":"100%","height":"350","isTransparent":true,"symbol":"OANDA:XAUUSD","showIntervalTabs":true,"displayMode":"single","colorTheme":"dark"}" height="360" width="100%" style="border:none;"></iframe>""", height=360)
with col2:
    st.markdown("#### 💵 DXY 1H ANALYSIS")
    components.html("""<iframe src="https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js?{"interval":"1h","width":"100%","height":"350","isTransparent":true,"symbol":"TVC:DXY","showIntervalTabs":true,"displayMode":"single","colorTheme":"dark"}" height="360" width="100%" style="border:none;"></iframe>""", height=360)

# 8. RISK CALCULATOR (Sidebar Bottom)
st.sidebar.markdown("---")
with st.sidebar:
    st.subheader("🛡️ RISK MGMT")
    bal = st.number_input("Account ($)", value=2000)
    risk_pct = st.slider("Risk (%)", 0.5, 3.0, 1.0)
    sl_pips = st.number_input("SL (Pips)", value=30)
    lots = round((bal * (risk_pct/100)) / (sl_pips * 10), 2)
    st.success(f"🔥 RECOMMENDED LOT: {lots}")
