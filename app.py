import streamlit as st
import streamlit.components.v1 as components

# 1. CORE INTERFACE
st.set_page_config(page_title="PATRO AI PRO V12.1.30", layout="wide")
st.markdown("<style>.stApp { background: #000; color: #fff; }</style>", unsafe_allow_html=True)

# 2. THE SIGNAL CENTER (VWAP + SMC Logic)
st.markdown("<h2 style='text-align:center; color:#00FF88;'>🏦 INSTITUTIONAL SIGNAL CENTER</h2>", unsafe_allow_html=True)

col1, col2 = st.columns([1, 1])

with col1:
    # Technical Gauge (The "No-Fake" Filter)
    gauge_html = """
    <div class="tradingview-widget-container">
      <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js" async>
      { "interval": "5m", "width": "100%", "isTransparent": true, "height": "220", "symbol": "OANDA:XAUUSD", "showIntervalTabs": false, "displayMode": "single", "locale": "en", "colorTheme": "dark" }
      </script>
    </div>
    """
    components.html(gauge_html, height=230)

with col2:
    st.markdown("""
        <div style='background:#111; padding:20px; border-radius:15px; border:1px solid #00FF88; height:220px;'>
            <h3 style='color:#00FF88; margin-top:0;'>⚓ VWAP PROTOCOL</h3>
            <p>🔵 <b>Price > VWAP:</b> Market is Bullish. Look for Buys at the VWAP line.</p>
            <p>🔴 <b>Price < VWAP:</b> Market is Bearish. Look for Sells at the VWAP line.</p>
            <p>🛡️ <b>Confirmation:</b> Only enter if the Gauge and VWAP direction match!</p>
        </div>
    """, unsafe_allow_html=True)

# 3. THE LIVE CHART (VWAP & SMC Access Enabled)
st.subheader("📊 LIVE XAUUSD (GOLD) STRUCTURE")
chart_html = """
<div class="tradingview-widget-container" style="height:600px;">
  <div id="tradingview_chart"></div>
  <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
  <script type="text/javascript">
  new TradingView.widget({
    "autosize": true, "symbol": "OANDA:XAUUSD", "interval": "5",
    "timezone": "Etc/UTC", "theme": "dark", "style": "1",
    "locale": "en", "toolbar_bg": "#111", "enable_publishing": false,
    "hide_side_toolbar": false, "allow_symbol_change": true,
    "show_popup_button": true, "container_id": "tradingview_chart",
    "studies": [
        "VWAP@tv-basicstudies", 
        "RSI@tv-basicstudies", 
        "Volume@tv-basicstudies"
    ]
  });
  </script>
</div>
"""
components.html(chart_html, height=600)
