import streamlit as st
import streamlit.components.v1 as components

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="PATRO AI PRO | ULTRA", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #050505; color: #ffffff; }
    .action-header {
        background: #111; padding: 20px; border-radius: 15px; 
        border: 2px solid #00FF88; text-align: center; margin-bottom: 25px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. THE SMART GAUGE COMPONENT ---
def draw_gauges(symbol, title):
    gauge_html = f"""
    <div class="tradingview-widget-container">
      <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js" async>
      {{
        "interval": "15m", "width": "100%", "isTransparent": true, "height": 400,
        "symbol": "{symbol}", "showIntervalTabs": true, "displayMode": "multiple",
        "locale": "en", "colorTheme": "dark"
      }}
      </script>
    </div>
    """
    st.markdown(f"<h3 style='text-align:center; color:#00FF88;'>{title}</h3>", unsafe_allow_html=True)
    components.html(gauge_html, height=400)

# --- 3. THE FIX: FULL SCREEN CHART ---
def draw_main_chart(height=600):
    chart_script = f"""
    <div id="tradingview_patro" style="height:{height}px;"></div>
    <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
    <script type="text/javascript">
    new TradingView.widget({{
      "autosize": true, "symbol": "OANDA:XAUUSD", "interval": "15",
      "theme": "dark", "style": "1", "container_id": "tradingview_patro",
      "studies": [
        {{ "id": "MASimple@tv-basicstudies", "inputs": {{ "length": 9 }}, "title": "9 EMA (Yellow)", "plots": {{ "0": {{ "color": "#FFEB3B" }} }} }},
        {{ "id": "MASimple@tv-basicstudies", "inputs": {{ "length": 21 }}, "title": "21 EMA (Red)", "plots": {{ "0": {{ "color": "#FF5252" }} }} }}
      ]
    }});
    </script>
    """
    components.html(chart_script, height=height+10)

# --- 4. TOP ACTION HEADER ---
st.markdown("""
<div class="action-header">
    <h1 style="color:#00FF88; margin:0;">🚀 LOOK FOR BUY (GOD MODE)</h1>
    <p style="color:#888;">Rating: 9.2/10 | Target: $4,680</p>
</div>
""", unsafe_allow_html=True)

# --- 5. GAUGE ROW ---
col1, col2 = st.columns(2)
with col1:
    draw_gauges("TVC:DXY", "DXY DOLLAR INDEX")
with col2:
    draw_gauges("OANDA:XAUUSD", "GOLD (XAUUSD) ANALYSIS")

st.divider()

# --- 6. THE NEW STABLE "POP-OUT" CHART ---
st.markdown("### 🖥️ CHART TERMINAL")
# Using an expander instead of a dialog to ensure it opens every time
with st.expander("🔍 CLICK TO OPEN FULL SCREEN ANALYSIS", expanded=False):
    st.info("Yellow Line over Red = BUY | Yellow Line under Red = SELL")
    draw_main_chart(height=750) # Extra large height for analysis

# Small chart for quick view
with st.container():
    draw_main_chart(height=400)

# --- 7. SIDEBAR ---
with st.sidebar:
    st.title("PATRO AI PRO")
    st.write("📍 Nairobi, Kenya")
    st.divider()
    if st.button("🔥 SEND MT5 SIGNAL"):
        st.success("Signal Sent: BUY XAUUSD")
