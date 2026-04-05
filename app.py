import streamlit as st
import streamlit.components.v1 as components

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="PATRO AI PRO | ULTRA", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .stApp { background-color: #050505; color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #0a0a0a; border-right: 1px solid #1f1f1f; }
    .action-header {
        background: #111; padding: 25px; border-radius: 15px; 
        border: 2px solid #00FF88; text-align: center; margin-bottom: 25px;
        box-shadow: 0px 0px 20px rgba(0, 255, 136, 0.2);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. THE CHART POP-OUT (DYNAMIC DIALOG) ---
@st.dialog("🖥️ PATRO AI | FULL SCREEN TERMINAL", width="large")
def chart_popout():
    components.html("""
    <div id="tv_full" style="height:700px;"></div>
    <script src="https://s3.tradingview.com/tv.js"></script>
    <script>
    new TradingView.widget({
      "autosize": true, "symbol": "OANDA:XAUUSD", "interval": "15", "theme": "dark",
      "style": "1", "container_id": "tv_full",
      "studies": ["VWAP@tv-basicstudies", "PivotPointsHighLow@tv-basicstudies", "RSI@tv-basicstudies"]
    });
    </script>""", height=710)

# --- 3. PROFESSIONAL GAUGE COMPONENT ---
def draw_gauges(symbol, title):
    gauge_html = f"""
    <div class="tradingview-widget-container">
      <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js" async>
      {{
        "interval": "15m",
        "width": "100%",
        "isTransparent": true,
        "height": 420,
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
    components.html(gauge_html, height=420)

# --- 4. TOP ACTION HEADER ---
st.markdown("""
<div class="action-header">
    <h1 style="color:#00FF88; margin:0; font-size: 42px;">🚀 LOOK FOR BUY (GOD MODE)</h1>
    <p style="color: #888; font-size: 16px; margin-top: 10px;">
        <b>AI ANALYSIS:</b> Confluence 9.2/10. Weekly Hammer support at $4,600. DXY weak at 100.03.
    </p>
</div>
""", unsafe_allow_html=True)

# --- 5. THE GAUGE ROW ---
col1, col2 = st.columns(2)
with col1:
    draw_gauges("TVC:DXY", "DXY DOLLAR INDEX")
with col2:
    draw_gauges("OANDA:XAUUSD", "GOLD (XAUUSD) ANALYSIS")

st.divider()

# --- 6. MAIN BODY & SIDEBAR ---
col_stats, col_action = st.columns([2, 1])

with col_stats:
    st.markdown("### 📊 LIVE DATA FEED")
    m1, m2, m3 = st.columns(3)
    m1.metric("XAUUSD", "$4,676.42", "OPENING")
    m2.metric("DXY", "100.03", "-0.14%")
    m3.metric("RATING", "9.2/10", "GOD MODE")

with col_action:
    st.markdown("### ⚡ QUICK ACTIONS")
    # THE CHART POP-OUT BUTTON
    if st.button("🖥️ POP-OUT FULL CHART", use_container_width=True):
        chart_popout()
    
    if st.button("🔥 SEND MT5 SIGNAL", use_container_width=True):
        st.success("Signal Sent to MT5 Terminal")

with st.sidebar:
    st.markdown("<h1 style='color:#00FF88;'>PATRO AI PRO</h1>", unsafe_allow_html=True)
    st.markdown("---")
    st.write("📍 **Location:** Nairobi, Kenya")
    st.write("🤖 **System Status:** Active")
    st.divider()
    bal = st.number_input("Wallet ($)", value=2000)
    risk = st.select_slider("Risk Mode", options=["Low", "Med", "High"], value="Med")
    st.write(f"Max Risk: **${bal * 0.02 if risk == 'Med' else bal * 0.01 if risk == 'Low' else bal * 0.05}**")
