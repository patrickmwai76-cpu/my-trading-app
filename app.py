import streamlit as st
import streamlit.components.v1 as components

# 1. CORE INTERFACE
st.set_page_config(page_title="PATRO AI PRO V12.1.36", layout="wide")
st.markdown("<style>.stApp { background: #000; color: #fff; }</style>", unsafe_allow_html=True)

# 2. THE MARKET TICKER
ticker_html = """
<div class="tradingview-widget-container">
  <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-ticker-tape.js" async>
  {
  "symbols": [
    { "proName": "INDEX:DXY", "title": "USD INDEX" },
    { "proName": "OANDA:XAUUSD", "title": "GOLD" },
    { "proName": "FX_IDC:EURUSD", "title": "EUR/USD" },
    { "proName": "BITSTAMP:BTCUSD", "title": "BTC" }
  ],
  "showSymbolLogo": true, "colorTheme": "dark", "isTransparent": true, "displayMode": "adaptive", "locale": "en"
  }
  </script>
</div>
"""
components.html(ticker_html, height=50)

# 3. INSTITUTIONAL X-RAY (Heatmap & Strength)
st.markdown("<h2 style='text-align:center; color:#00FF88;'>🔬 INSTITUTIONAL X-RAY</h2>", unsafe_allow_html=True)
col_heatmap, col_strength = st.columns([1.5, 1])

with col_heatmap:
    # Forex Heatmap - Shows which currencies are "Killing it" right now
    st.markdown("<p style='color:#888;'>GLOBAL CURRENCY HEATMAP</p>", unsafe_allow_html=True)
    heatmap_html = """
    <div class="tradingview-widget-container">
      <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-forex-heat-map.js" async>
      { "width": "100%", "height": "350", "currencies": ["EUR", "USD", "JPY", "GBP", "CHF", "AUD", "CAD"], "isTransparent": true, "colorTheme": "dark", "locale": "en" }
      </script>
    </div>
    """
    components.html(heatmap_html, height=360)

with col_strength:
    # Technical Gauge for XAUUSD
    st.markdown("<p style='color:#888;'>GOLD MOMENTUM GAUGE</p>", unsafe_allow_html=True)
    gauge_html = """
    <div class="tradingview-widget-container">
      <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js" async>
      { "interval": "15m", "width": "100%", "isTransparent": true, "height": "320", "symbol": "OANDA:XAUUSD", "showIntervalTabs": false, "displayMode": "single", "locale": "en", "colorTheme": "dark" }
      </script>
    </div>
    """
    components.html(gauge_html, height=330)

# 4. THE LIVE CHART (VWAP Anchor)
st.subheader("📊 LIVE XAUUSD (GOLD) STRUCTURE")
chart_html = """
<div class="tradingview-widget-container" style="height:600px;">
  <div id="tradingview_chart"></div>
  <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
  <script type="text/javascript">
  new TradingView.widget({
    "autosize": true, "symbol": "OANDA:XAUUSD", "interval": "15",
    "timezone": "Etc/UTC", "theme": "dark", "style": "1",
    "locale": "en", "toolbar_bg": "#111", "enable_publishing": false,
    "hide_side_toolbar": false, "allow_symbol_change": true,
    "show_popup_button": true, "container_id": "tradingview_chart",
    "studies": ["VWAP@tv-basicstudies"]
  });
  </script>
</div>
"""
components.html(chart_html, height=600)

# 5. MARKET KILLER CHECKLIST & RISK (Sidebar)
st.sidebar.header("🛡️ RISK & RULES")
balance = st.sidebar.number_input("Balance ($)", value=1000)
risk_pct = st.sidebar.slider("Risk %", 0.5, 3.0, 1.0)
sl_pips = st.sidebar.number_input("Stop Loss (Pips)", value=30)
risk_cash = balance * (risk_pct / 100)
pro_lot = risk_cash / (sl_pips * 10)

st.sidebar.success(f"PRO LOT SIZE: {pro_lot:.2f}")
st.sidebar.markdown("---")
st.sidebar.markdown("### 🎯 PRE-FLIGHT CHECK")
st.sidebar.checkbox("DXY Correlation Match?")
st.sidebar.checkbox("Gauge is 'Strong'?")
st.sidebar.checkbox("Price near VWAP?")
st.sidebar.checkbox("No High-Impact News?")
