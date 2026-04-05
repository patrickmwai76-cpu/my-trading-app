import streamlit as st
import streamlit.components.v1 as components

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="PATRO AI PRO | ULTRA", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .stApp { background-color: #050505; color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #0a0a0a; border-right: 1px solid #1f1f1f; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. THE EXACT GAUGE COMPONENT (From your Photo) ---
def professional_gauge(symbol, title):
    # This uses the "large" display mode to show all 3 sticks (Oscillators, Summary, MAs)
    gauge_html = f"""
    <div class="tradingview-widget-container">
      <div class="tradingview-widget-container__widget"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js" async>
      {{
        "interval": "15m",
        "width": "100%",
        "isTransparent": true,
        "height": 450,
        "symbol": "{symbol}",
        "showIntervalTabs": true,
        "displayMode": "multiple",
        "locale": "en",
        "colorTheme": "dark"
      }}
      </script>
    </div>
    """
    st.markdown(f"<h3 style='text-align:center; color:#00FF88;'>{title}</h3>", unsafe_allow_html=True)
    components.html(gauge_html, height=450)

# --- 3. TOP SECTION: THE PHOTO-MATCHED GAUGES ---
# We use two large columns to fit the "Triple-Stick" view for both assets
gauge_col1, gauge_col2 = st.columns(2)

with gauge_col1:
    professional_gauge("TVC:DXY", "📊 DXY DOLLAR ANALYSIS")

with gauge_col2:
    professional_gauge("OANDA:XAUUSD", "🔥 GOLD SMART ANALYSIS")

st.divider()

# --- 4. MAIN INTERFACE ---
col_chart, col_side = st.columns([3, 1])

with col_chart:
    st.markdown("#### 📈 PATRO AI LIVE TERMINAL")
    components.html("""
    <div id="tv_main" style="height:500px;"></div>
    <script src="https://s3.tradingview.com/tv.js"></script>
    <script>
    new TradingView.widget({
      "autosize": true, "symbol": "OANDA:XAUUSD", "interval": "15", "theme": "dark",
      "style": "1", "container_id": "tv_main",
      "studies": ["VWAP@tv-basicstudies", "PivotPointsHighLow@tv-basicstudies"]
    });
    </script>""", height=510)

with col_side:
    st.markdown("### 🧠 EXECUTION")
    st.metric("SCORE", "9/10", delta="GOD MODE")
    if st.button("🚀 EXECUTE BUY"):
        st.balloons()
    
    st.divider()
    st.link_button("🌐 POP-OUT FULL CHART", "https://www.tradingview.com/chart/XAUUSD/")

with st.sidebar:
    st.markdown("<h1 style='color:#00FF88;'>PATRO AI</h1>", unsafe_allow_html=True)
    st.write("Broker: Exness | Platform: MT5")
    st.number_input("Balance", value=2000)
    st.select_slider("Risk %", options=[1, 2, 3], value=1)
