import streamlit as st
import streamlit.components.v1 as components

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="PATRO AI PRO | ULTRA", layout="wide", initial_sidebar_state="expanded")

# --- 2. THE TRADINGVIEW GAUGE COMPONENT ---
def tradingview_gauge(symbol, title):
    # This embeds the official TradingView Technical Analysis Gauge
    # It includes the "Stick" (Needle) in the middle as requested.
    calc_html = f"""
    <div class="tradingview-widget-container" style="width: 100%; height: 350px;">
      <div class="tradingview-widget-container__widget"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js" async>
      {{
        "interval": "15m",
        "width": "100%",
        "isTransparent": true,
        "height": 330,
        "symbol": "{symbol}",
        "showIntervalTabs": true,
        "displayMode": "single",
        "locale": "en",
        "colorTheme": "dark"
      }}
      </script>
    </div>
    """
    st.markdown(f"<h4 style='text-align:center; color:#00FF88;'>{title}</h4>", unsafe_allow_html=True)
    components.html(calc_html, height=350)

# --- 3. TOP SECTION: THE CLOCK GAUGES ---
st.markdown("### 🛰️ GLOBAL MARKET SENTIMENT")
gauge_col1, gauge_col2 = st.columns(2)

with gauge_col1:
    # DXY Gauge - Analyzing the US Dollar Index
    tradingview_gauge("TVC:DXY", "💵 DXY STRENGTH (USD)")

with gauge_col2:
    # XAUUSD Gauge - The Gold Signal (Includes 1m, 5m, 15m, 1h tabs)
    tradingview_gauge("OANDA:XAUUSD", "🏆 GOLD (XAUUSD) SIGNAL")

st.divider()

# --- 4. MAIN BODY: CHART & DATA ---
col_left, col_right = st.columns([3, 1])

with col_left:
    st.markdown("#### 📈 LIVE CHART INTERFACE")
    components.html("""
    <div id="tv_main" style="height:550px;"></div>
    <script src="https://s3.tradingview.com/tv.js"></script>
    <script>
    new TradingView.widget({
      "autosize": true, "symbol": "OANDA:XAUUSD", "interval": "15", "theme": "dark",
      "style": "1", "container_id": "tv_main",
      "studies": ["VWAP@tv-basicstudies", "PivotPointsHighLow@tv-basicstudies"]
    });
    </script>""", height=560)

with col_right:
    st.markdown("### 🧠 AI DASHBOARD")
    st.metric("CURRENT STATUS", "SCANNING", delta="100.17 DXY", delta_color="inverse")
    
    # POP-OUT BUTTON
    if st.button("🔍 POP-OUT ANALYSIS"):
        st.toast("Opening specialized analysis window...")
    
    st.link_button("🌐 VIEW ON TRADINGVIEW", "https://www.tradingview.com/chart/XAUUSD/")
    
    st.divider()
    st.markdown("#### RISK MGT")
    bal = st.number_input("Balance", value=2000)
    risk = st.select_slider("Risk %", options=[0.5, 1.0, 2.0], value=1.0)
    st.info(f"Max Loss: ${bal * (risk/100):.2f}")

# --- 5. SIDEBAR ---
with st.sidebar:
    st.markdown("<h1 style='color:#00FF88;'>PATRO AI PRO</h1>", unsafe_allow_html=True)
    st.markdown("v14.0 - ULTRA")
    st.divider()
    st.write("Broker: Exness (MT5)")
    st.write("Region: Nairobi, Kenya")
    if st.button("🔄 REFRESH SYSTEM"):
        st.rerun()
