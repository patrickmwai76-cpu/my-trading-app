import streamlit as st
import streamlit.components.v1 as components

# 1. CORE INTERFACE
st.set_page_config(page_title="PATRO AI PRO V12.1.37", layout="wide")
st.markdown("<style>.stApp { background: #000; color: #fff; }</style>", unsafe_allow_html=True)

# 2. THE MARKET TICKER
ticker_html = """
<div class="tradingview-widget-container">
  <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-ticker-tape.js" async>
  {
  "symbols": [
    { "proName": "INDEX:DXY", "title": "USD INDEX" },
    { "proName": "OANDA:XAUUSD", "title": "GOLD" },
    { "proName": "FX_IDC:EURUSD", "title": "EUR/USD" }
  ],
  "showSymbolLogo": true, "colorTheme": "dark", "isTransparent": true, "displayMode": "adaptive", "locale": "en"
  }
  </script>
</div>
"""
components.html(ticker_html, height=50)

# 3. THE MULTI-TIMEFRAME HUB
st.markdown("<h2 style='text-align:center; color:#00FF88;'>🏛️ MULTI-TIMEFRAME CONSENSUS</h2>", unsafe_allow_html=True)

# We enable "showIntervalTabs": true so you can toggle between 1m, 5m, 15m, 1h, etc.
gauge_mtf_html = """
<div class="tradingview-widget-container">
  <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js" async>
  {
    "interval": "15m",
    "width": "100%",
    "isTransparent": true,
    "height": "430",
    "symbol": "OANDA:XAUUSD",
    "showIntervalTabs": true,
    "displayMode": "multiple",
    "locale": "en",
    "colorTheme": "dark"
  }
  </script>
</div>
"""
components.html(gauge_mtf_html, height=450)

# 4. INSTITUTIONAL CORRELATION (DXY & Heatmap)
col_dxy, col_heatmap = st.columns([1, 1])

with col_dxy:
    st.markdown("<p style='text-align:center; color:#888;'>DXY (DOLLAR) CONFIRMATION</p>", unsafe_allow_html=True)
    dxy_mini_html = """
    <div class="tradingview-widget-container">
      <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-mini-symbol-overview.js" async>
      { "symbol": "INDEX:DXY", "width": "100%", "height": "220", "locale": "en", "dateRange": "1D", "colorTheme": "dark", "isTransparent": true }
      </script>
    </div>
    """
    components.html(dxy_mini_html, height=230)

with col_heatmap:
    st.markdown("<p style='text-align:center; color:#888;'>CURRENCY STRENGTH MAP</p>", unsafe_allow_html=True)
    heatmap_html = """
    <div class="tradingview-widget-container">
      <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-forex-heat-map.js" async>
      { "width": "100%", "height": "220", "currencies": ["EUR", "USD", "JPY", "GBP", "CHF", "AUD", "CAD"], "isTransparent": true, "colorTheme": "dark", "locale": "en" }
      </script>
    </div>
    """
    components.html(heatmap_html, height=230)

# 5. THE LIVE CHART
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

# 6. SIDEBAR RISK & CHECKLIST
st.sidebar.header("🛡️ RISK & RULES")
balance = st.sidebar.number_input("Balance ($)", value=1000)
risk_pct = st.sidebar.slider("Risk %", 0.5, 3.0, 1.0)
sl_pips = st.sidebar.number_input("Stop Loss (Pips)", value=30)
risk_cash = balance * (risk_pct / 100)
pro_lot = risk_cash / (sl_pips * 10)

st.sidebar.success(f"PRO LOT SIZE: {pro_lot:.2f}")
st.sidebar.markdown("---")
st.sidebar.markdown("### 🎯 MULTI-TF CHECK")
st.sidebar.checkbox("1m & 5m Align?")
st.sidebar.checkbox("15m & 1h Align?")
st.sidebar.checkbox("DXY Moving Opposite?")
