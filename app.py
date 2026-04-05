import streamlit as st
import streamlit.components.v1 as components

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="PATRO AI PRO | ULTRA", layout="wide", initial_sidebar_state="expanded")

# --- 2. THE MULTI-GAUGE COMPONENT (PHOTO MATCHED) ---
def professional_gauge(symbol, title):
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

# --- 3. DYNAMIC RATING & ACTION LOGIC ---
# Simulated live logic for April 5, 2026
score = 9.2  # High score due to weekly Hammer formation and DXY below 100.5
price = 4676.42

if score >= 8.5:
    action_text = "🚀 LOOK FOR BUY (GOD MODE)"
    action_color = "#00FF88"
    description = "Confluence high. All timeframes align with Weekly Hammer. DXY is weak."
elif score >= 6.5:
    action_text = "⚖️ SCALP BUY"
    action_color = "#FFAA00"
    description = "Trend is up but volume is neutral. Watch VWAP for entry."
elif score <= 3.5:
    action_text = "🔻 LOOK FOR SELL"
    action_color = "#FF4B4B"
    description = "Price below VWAP and Pivot. DXY gaining strength."
else:
    action_text = "⏸️ STANDBY (NEUTRAL)"
    action_color = "#888888"
    description = "Market ranging. No clear edge. Protect your capital."

# --- 4. TOP SECTION: ACTION & GAUGES ---
st.markdown(f"""
<div style="background: #111; padding: 20px; border-radius: 15px; border: 2px solid {action_color}; text-align: center; margin-bottom: 25px;">
    <h1 style="color:{action_color}; margin:0; font-size: 40px;">{action_text}</h1>
    <p style="color: #888; font-size: 16px; margin-top: 10px;"><b>AI REASON:</b> {description}</p>
</div>
""", unsafe_allow_html=True)

g_col1, g_col2 = st.columns(2)
with g_col1:
    professional_gauge("TVC:DXY", "DXY DOLLAR INDEX")
with g_col2:
    professional_gauge("OANDA:XAUUSD", "XAUUSD GOLD ANALYSIS")

st.divider()

# --- 5. CHART & SIDEBAR ---
col_left, col_right = st.columns([3, 1])

with col_left:
    components.html(f"""
    <div id="tv_main" style="height:500px;"></div>
    <script src="https://s3.tradingview.com/tv.js"></script>
    <script>
    new TradingView.widget({{
      "autosize": true, "symbol": "OANDA:XAUUSD", "interval": "15", "theme": "dark",
      "style": "1", "container_id": "tv_main",
      "studies": ["VWAP@tv-basicstudies", "PivotPointsHighLow@tv-basicstudies"]
    }});
    </script>""", height=510)

with col_right:
    st.markdown(f"### 🎯 RATING: {score}/10")
    st.progress(score/10)
    st.metric("GOLD PRICE", f"${price}")
    st.metric("DXY STATUS", "100.03", delta="-0.14 (Weak)")
    
    if st.button("🔥 SEND SIGNAL TO MT5"):
        st.success(f"Signal sent: {action_text} at ${price}")

with st.sidebar:
    st.markdown("<h1 style='color:#00FF88;'>PATRO AI</h1>", unsafe_allow_html=True)
    st.write("Broker: **Exness**")
    st.write("Mode: **Live Trading**")
    st.divider()
    st.link_button("🌐 POP-OUT CHART", "https://www.tradingview.com/chart/XAUUSD/")
