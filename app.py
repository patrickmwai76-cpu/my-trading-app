import streamlit as st
import streamlit.components.v1 as components

# 1. PAGE CONFIG
st.set_page_config(page_title="PATRO AI PRO V12.1.38", layout="wide")
st.markdown("<style>.stApp { background: #000; color: #fff; }</style>", unsafe_allow_html=True)

# 2. THE TOP SIGNAL HUB
st.markdown("<h2 style='text-align:center; color:#00FF88;'>🏛️ CONSENSUS COMMAND CENTER</h2>", unsafe_allow_html=True)

# We create 3 columns to see 3 different timeframes AT ONCE
col_ltf, col_itf, col_htf = st.columns(3)

with col_ltf:
    st.markdown("<p style='text-align:center; color:#888;'>LTF (5M) - THE TRIGGER</p>", unsafe_allow_html=True)
    gauge_5m = """<div class="tradingview-widget-container"><script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js" async>{ "interval": "5m", "width": "100%", "isTransparent": true, "height": "330", "symbol": "OANDA:XAUUSD", "showIntervalTabs": false, "displayMode": "single", "locale": "en", "colorTheme": "dark" }</script></div>"""
    components.html(gauge_5m, height=340)

with col_itf:
    st.markdown("<p style='text-align:center; color:#888;'>ITF (15M) - THE SETUP</p>", unsafe_allow_html=True)
    gauge_15m = """<div class="tradingview-widget-container"><script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js" async>{ "interval": "15m", "width": "100%", "isTransparent": true, "height": "330", "symbol": "OANDA:XAUUSD", "showIntervalTabs": false, "displayMode": "single", "locale": "en", "colorTheme": "dark" }</script></div>"""
    components.html(gauge_15m, height=340)

with col_htf:
    st.markdown("<p style='text-align:center; color:#888;'>HTF (1H) - THE BOSS</p>", unsafe_allow_html=True)
    gauge_1h = """<div class="tradingview-widget-container"><script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js" async>{ "interval": "1H", "width": "100%", "isTransparent": true, "height": "330", "symbol": "OANDA:XAUUSD", "showIntervalTabs": false, "displayMode": "single", "locale": "en", "colorTheme": "dark" }</script></div>"""
    components.html(gauge_1h, height=340)

# 3. GLOBAL CORRELATION (DXY)
st.markdown("---")
st.markdown("<p style='text-align:center; color:#888;'>DXY (DOLLAR) VS XAUUSD (GOLD) CORRELATION</p>", unsafe_allow_html=True)
dxy_compare = """<div class="tradingview-widget-container"><script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-mini-symbol-overview.js" async>{ "symbol": "INDEX:DXY", "width": "100%", "height": "200", "locale": "en", "dateRange": "1D", "colorTheme": "dark", "isTransparent": true }</script></div>"""
components.html(dxy_compare, height=210)

# 4. THE LIVE CHART (15M SMC Focus)
st.subheader("📊 LIVE XAUUSD MARKET STRUCTURE")
chart_html = """<div class="tradingview-widget-container" style="height:550px;"><div id="tradingview_chart"></div><script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script><script type="text/javascript">new TradingView.widget({ "autosize": true, "symbol": "OANDA:XAUUSD", "interval": "15", "theme": "dark", "style": "1", "container_id": "tradingview_chart", "studies": ["VWAP@tv-basicstudies"] });</script></div>"""
components.html(chart_html, height=550)

# 5. RISK SIDEBAR
st.sidebar.header("🛡️ THE KILLER RISK")
balance = st.sidebar.number_input("Balance", value=1000)
risk = st.sidebar.slider("Risk %", 0.5, 2.0, 1.0)
sl = st.sidebar.number_input("SL Pips", value=30)
lot = (balance * (risk/100)) / (sl * 10)
st.sidebar.success(f"USE LOT: {lot:.2f}")
