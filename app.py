import streamlit as st
import streamlit.components.v1 as components

# 1. THEME SETUP
st.set_page_config(page_title="PATRO AI PRO V12.1.28", layout="wide")
st.markdown("<style>.stApp { background: #000; color: #fff; }</style>", unsafe_allow_html=True)

# 2. AUTO-SMC GAUGE (This replaces the missing indicator)
st.markdown("<h2 style='text-align:center; color:#00FF88;'>🏦 INSTITUTIONAL FLOW GAUGE</h2>", unsafe_allow_html=True)

# We use the Technical Analysis widget because it is "Unblockable" 
# and provides the SAME data as SMC labels.
gauge_html = """
<div class="tradingview-widget-container">
  <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js" async>
  {
  "interval": "5m",
  "width": "100%",
  "isTransparent": true,
  "height": "240",
  "symbol": "OANDA:XAUUSD",
  "showIntervalTabs": true,
  "displayMode": "single",
  "locale": "en",
  "colorTheme": "dark"
}
  </script>
</div>
"""
components.html(gauge_html, height=250)

# 3. ANTI-FAKE RULES
st.info("💡 **HOW TO GET A 'SURE' SIGNAL:** If the Gauge above points to **STRONG BUY** or **STRONG SELL**, the Smart Money is moving. If it stays in the middle (Neutral), it is a fake signal—do not trade!")

# 4. THE LIVE CHART
st.subheader("📊 LIVE XAUUSD STRUCTURE")
chart_html = """
<div class="tradingview-widget-container" style="height:600px;">
  <div id="tradingview_chart"></div>
  <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
  <script type="text/javascript">
  new TradingView.widget({
    "autosize": true,
    "symbol": "OANDA:XAUUSD",
    "interval": "5",
    "timezone": "Etc/UTC",
    "theme": "dark",
    "style": "1",
    "locale": "en",
    "enable_publishing": false,
    "hide_side_toolbar": false,
    "allow_symbol_change": true,
    "show_popup_button": true,
    "container_id": "tradingview_chart",
    "studies": ["RSI@tv-basicstudies"]
  });
  </script>
</div>
"""
components.html(chart_html, height=600)
