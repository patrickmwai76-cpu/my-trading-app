import streamlit as st
import streamlit.components.v1 as components

# 1. CORE INTERFACE
st.set_page_config(page_title="PATRO AI PRO V12.1.34", layout="wide")
st.markdown("<style>.stApp { background: #000; color: #fff; }</style>", unsafe_allow_html=True)

# 2. FIXED TICKER TAPE (The "NameError" Fix)
# We define the variable clearly here first.
ticker_html = """
<div class="tradingview-widget-container">
  <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-ticker-tape.js" async>
  {
  "symbols": [
    { "proName": "INDEX:DXY", "title": "DXY (DOLLAR)" },
    { "proName": "OANDA:XAUUSD", "title": "GOLD" },
    { "proName": "BITSTAMP:BTCUSD", "title": "BITCOIN" }
  ],
  "showSymbolLogo": true, "colorTheme": "dark", "isTransparent": true, "displayMode": "adaptive", "locale": "en"
  }
  </script>
</div>
"""
# Now we call it using the exact same name
components.html(ticker_html, height=50)

# 3. INSTITUTIONAL SIGNAL CENTER
st.markdown("<h2 style='text-align:center; color:#00FF88;'>🏦 INSTITUTIONAL SIGNAL CENTER</h2>", unsafe_allow_html=True)

col1, col2 = st.columns([1, 1])

with col1:
    # Gold Technical Gauge
    gauge_html = """
    <div class="tradingview-widget-container">
      <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js" async>
      { "interval": "5m", "width": "100%", "isTransparent": true, "height": "220", "symbol": "OANDA:XAUUSD", "showIntervalTabs": false, "displayMode": "single", "locale": "en", "colorTheme": "dark" }
      </script>
    </div>
    """
    components.html(gauge_html, height=230)

with col2:
    # DXY (Dollar Index) Correlation - If DXY goes DOWN, Gold goes UP
    st.markdown("<p style='text-align:center; color:#888;'>DXY (DOLLAR INDEX) CONFIRMATION</p>", unsafe_allow_html=True)
    dxy_mini_html = """
    <div class="tradingview-widget-container">
      <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-mini-symbol-overview.js" async>
      { "symbol": "INDEX:DXY", "width": "100%", "height": "175", "locale": "en", "dateRange": "1D", "colorTheme": "dark", "isTransparent": true }
      </script>
    </div>
    """
    components.html(dxy_mini_html, height=190)

# 4. THE LIVE CHART
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
    "studies": ["VWAP@tv-basicstudies", "RSI@tv-basicstudies"]
  });
  </script>
</div>
"""
components.html(chart_html, height=600)

# 5. RISK CALCULATOR (Sidebar)
st.sidebar.header("🛡️ MARKET KILLER RISK")
balance = st.sidebar.number_input("Account Balance ($)", value=1000)
risk_pct = st.sidebar.slider("Risk (%)", 0.5, 5.0, 1.0)
sl_pips = st.sidebar.number_input("Stop Loss (Pips)", value=20)

risk_cash = balance * (risk_pct / 100)
recommended_lot = risk_cash / (sl_pips * 10)

st.sidebar.markdown(f"### 🔥 PRO LOT: **{recommended_lot:.2f}**")
st.sidebar.caption(f"Risking: ${risk_cash:.2f} per trade.")
