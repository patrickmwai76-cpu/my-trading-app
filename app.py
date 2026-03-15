import streamlit as st
import streamlit.components.v1 as components

# 1. CORE INTERFACE
st.set_page_config(page_title="PATRO AI PRO V12.1.35", layout="wide")
st.markdown("<style>.stApp { background: #000; color: #fff; }</style>", unsafe_allow_html=True)

# 2. THE MARKET TICKER (With DXY & Gold)
ticker_html = """
<div class="tradingview-widget-container">
  <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-ticker-tape.js" async>
  {
  "symbols": [
    { "proName": "INDEX:DXY", "title": "USD INDEX (DXY)" },
    { "proName": "OANDA:XAUUSD", "title": "GOLD SPOT" },
    { "proName": "FX_IDC:EURUSD", "title": "EUR/USD" }
  ],
  "showSymbolLogo": true, "colorTheme": "dark", "isTransparent": true, "displayMode": "adaptive", "locale": "en"
  }
  </script>
</div>
"""
components.html(ticker_html, height=50)

# 3. INSTITUTIONAL SIGNAL CENTER
st.markdown("<h2 style='text-align:center; color:#00FF88;'>🏦 INSTITUTIONAL SIGNAL CENTER</h2>", unsafe_allow_html=True)
col_gauge, col_dxy = st.columns([1, 1])

with col_gauge:
    # Gold Technical Gauge
    gauge_html = """
    <div class="tradingview-widget-container">
      <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js" async>
      { "interval": "15m", "width": "100%", "isTransparent": true, "height": "220", "symbol": "OANDA:XAUUSD", "showIntervalTabs": false, "displayMode": "single", "locale": "en", "colorTheme": "dark" }
      </script>
    </div>
    """
    components.html(gauge_html, height=230)

with col_dxy:
    # DXY Mini-Chart for Correlation
    st.markdown("<p style='text-align:center; color:#888;'>DXY (DOLLAR) - THE GOLD KILLER</p>", unsafe_allow_html=True)
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
<div class="tradingview-widget-container" style="height:550px;">
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
components.html(chart_html, height=550)

# 5. THE "MARKET KILLER" CHEAT SHEET (Final Checklist)
st.divider()
st.subheader("🎯 THE MARKET KILLER CHEAT SHEET")
col_check1, col_check2 = st.columns(2)

with col_check1:
    st.markdown("""
    #### 🛡️ STEP 1: TREND BIAS (1H/4H)
    - [ ] Is the overall trend Bullish or Bearish?
    - [ ] Did we recently have a **BOS** (Break of Structure)?
    - [ ] Is the price above or below the **VWAP** (Blue Line)?

    #### 🧩 STEP 2: LIQUIDITY CHECK
    - [ ] Did price sweep a Previous Day High/Low?
    - [ ] Is there a **Fair Value Gap (FVG)** that needs to be filled?
    """)

with col_check2:
    #### 🚀 STEP 3: THE "SURE" ENTRY
    st.markdown("""
    - [ ] Does the **DXY** (Dollar) move opposite to your Gold trade?
    - [ ] Does the **Technical Gauge** say "Strong Buy/Sell"?
    - [ ] **NO NEWS:** Check the Economic Calendar for any red icons.
    """)
    
    # 6. RISK CALCULATOR (Sidebar)
    st.sidebar.header("🛡️ RISK MANAGEMENT")
    balance = st.sidebar.number_input("Balance ($)", value=1000)
    risk_pct = st.sidebar.slider("Risk %", 0.5, 3.0, 1.0)
    sl_pips = st.sidebar.number_input("Stop Loss (Pips)", value=30)
    
    risk_cash = balance * (risk_pct / 100)
    pro_lot = risk_cash / (sl_pips * 10)
    
    st.sidebar.success(f"PRO LOT SIZE: {pro_lot:.2f}")
    st.sidebar.info(f"Risking: ${risk_cash:.2f}")

# 7. ECONOMIC CALENDAR (Safety Shield)
st.divider()
st.subheader("📅 GLOBAL NEWS RADAR")
cal_html = """
<div class="tradingview-widget-container">
  <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-events.js" async>
  { "colorTheme": "dark", "isTransparent": true, "width": "100%", "height": "300", "locale": "en", "importanceFilter": "-1,0,1" }
  </script>
</div>
"""
components.html(cal_html, height=310)
