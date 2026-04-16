import streamlit as st
import streamlit.components.v1 as components

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="PATRO AI PRO | ULTRA", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #050505; color: #ffffff; }
    .signal-card {
        padding: 20px; border-radius: 15px; text-align: center;
        margin-bottom: 20px; border: 2px solid #333;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. THE SMART CHART WITH CORRECT COLORS ---
def draw_colored_chart():
    # We use 'studies' to force the specific colors: Yellow (#FFEB3B) and Red (#FF5252)
    chart_script = """
    <div id="tradingview_patro" style="height:600px;"></div>
    <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
    <script type="text/javascript">
    new TradingView.widget({
      "autosize": true,
      "symbol": "OANDA:XAUUSD",
      "interval": "15",
      "timezone": "Africa/Nairobi",
      "theme": "dark",
      "style": "1",
      "locale": "en",
      "toolbar_bg": "#f1f3f6",
      "enable_publishing": false,
      "hide_top_toolbar": false,
      "save_image": false,
      "container_id": "tradingview_patro",
      "studies": [
        {
            "id": "MASimple@tv-basicstudies",
            "inputs": { "length": 9 },
            "title": "9 EMA (Fast)",
            "plots": { "0": { "color": "#FFEB3B" } } 
        },
        {
            "id": "MASimple@tv-basicstudies",
            "inputs": { "length": 21 },
            "title": "21 EMA (Slow)",
            "plots": { "0": { "color": "#FF5252" } }
        }
      ]
    });
    </script>
    """
    components.html(chart_script, height=610)

# --- 3. MAIN DASHBOARD ---
st.markdown("### 🛰️ PATRO AI | MOMENTUM TERMINAL")

# Top row for visual confirmation
col_signal, col_dxy = st.columns([2, 1])

with col_signal:
    # This box helps you identify the cross without confusion
    st.markdown("""
    <div style="display: flex; gap: 10px; justify-content: center; margin-bottom: 10px;">
        <div style="background: #FFEB3B; color: black; padding: 5px 15px; border-radius: 5px; font-weight: bold;">YELLOW = BUY LINE</div>
        <div style="background: #FF5252; color: white; padding: 5px 15px; border-radius: 5px; font-weight: bold;">RED = SELL LINE</div>
    </div>
    """, unsafe_allow_html=True)
    draw_colored_chart()

with col_dxy:
    st.markdown("### 🧠 AI CONFLUENCE")
    st.metric("DXY INDEX", "100.03", "-0.14%")
    st.info("Market Rule: If Yellow crosses ABOVE Red -> **BUY**. If Yellow crosses BELOW Red -> **SELL**.")
    
    if st.button("🖥️ POP-OUT CHART", use_container_width=True):
        st.toast("Opening Full Analysis Window...")

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title("PATRO AI PRO")
    st.write("📍 Nairobi, Kenya")
    st.divider()
    if st.button("🔥 REFRESH SIGNALS"):
        st.rerun()
