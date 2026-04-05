import streamlit as st
import streamlit.components.v1 as components
import plotly.graph_objects as go
from datetime import datetime
import pytz
import yfinance as yf

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="PATRO AI PRO | ULTRA", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .stApp { background-color: #050505; color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #0a0a0a; border-right: 1px solid #1f1f1f; }
    .stMetric { background-color: #111; padding: 10px; border-radius: 10px; border: 1px solid #222; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. GAUGE CREATOR (Clock Style) ---
def create_gauge(value, title, max_val, color):
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = value,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': title, 'font': {'size': 18, 'color': 'white'}},
        gauge = {
            'axis': {'range': [None, max_val], 'tickwidth': 1, 'tickcolor': "white"},
            'bar': {'color': color},
            'bgcolor': "rgba(0,0,0,0)",
            'borderwidth': 2,
            'bordercolor': "#333",
            'steps': [
                {'range': [0, max_val*0.4], 'color': '#330000'},
                {'range': [max_val*0.4, max_val*0.7], 'color': '#333300'},
                {'range': [max_val*0.7, max_val], 'color': '#003300'}
            ],
            'threshold': {
                'line': {'color': "white", 'width': 4},
                'thickness': 0.75,
                'value': value
            }
        }
    ))
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                      font={'color': "white"}, height=250, margin=dict(l=20, r=20, t=50, b=20))
    return fig

# --- 3. ANALYTICS ENGINE ---
def get_data():
    try:
        gold = yf.Ticker("GC=F")
        df = gold.history(period="2d", interval="15m")
        current_p = round(df['Close'].iloc[-1], 2) if not df.empty else 4690.52
        df['TP'] = (df['High'] + df['Low'] + df['Close']) / 3
        df['PV'] = df['TP'] * df['Volume']
        vwap = round(df['PV'].cumsum().iloc[-1] / df['Volume'].cumsum().iloc[-1], 2) if not df.empty else 4685.00
        p_low = round(df['Low'].tail(10).min(), 2) if not df.empty else 4677.20
        return current_p, vwap, p_low
    except:
        return 4690.52, 4685.00, 4677.20

price, vwap, pl = get_data()

# --- 4. CALC RATINGS ---
score = 0
if price > vwap: score += 2
if price > pl: score += 2
score += 5 # Timeframe Alignment Bias
dxy_val = 100.17 # April 2026 Close

# --- 5. TOP ROW: GAUGES ---
st.markdown("### 🛰️ SYSTEM OVERVIEW")
g_col1, g_col2, g_col3 = st.columns(3)

with g_col1:
    st.plotly_chart(create_gauge(score, "SIGNAL CONFIDENCE", 10, "#00FF88"), use_container_width=True)

with g_col2:
    # Inverse gauge for DXY (Lower is better for Gold)
    dxy_score = 105 - dxy_val # Normalized for 0-10 display
    st.plotly_chart(create_gauge(round(dxy_val, 2), "DXY STRENGTH", 110, "#FFAA00"), use_container_width=True)

with g_col3:
    st.plotly_chart(create_gauge(8, "TF ALIGNMENT", 10, "#0088FF"), use_container_width=True)

st.divider()

# --- 6. MAIN BODY ---
col_left, col_right = st.columns([3, 1])

with col_left:
    st.markdown(f"#### 📈 LIVE CHART | ${price}")
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
    st.markdown("### 🧠 PATRO AI LOGIC")
    st.metric("VWAP DISTANCE", f"{round(price-vwap, 2)}")
    st.metric("PIVOT DISTANCE", f"{round(price-pl, 2)}")
    
    st.divider()
    if st.button("🔍 POP-OUT CHART"):
        st.toast("Opening high-res window...")
        # (Dialog function logic would go here)
    
    st.link_button("🌐 TRADINGVIEW FULL", "https://www.tradingview.com/chart/XAUUSD/")

with st.sidebar:
    st.markdown("<h1 style='color:#00FF88;'>PATRO AI</h1>", unsafe_allow_html=True)
    bal = st.number_input("Account ($)", value=2000)
    risk = st.select_slider("Risk %", options=[0.5, 1.0, 2.0], value=1.0)
    st.metric("MAX RISK", f"${bal * (risk/100):.2f}")
    if st.button("🔄 REFRESH"):
        st.rerun()
