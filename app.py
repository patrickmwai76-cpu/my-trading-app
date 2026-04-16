import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import yfinance as yf

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="PATRO AI PRO | ULTRA", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #050505; color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #0a0a0a; border-right: 1px solid #1f1f1f; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA ENGINE (Crossover Logic) ---
def get_signals():
    try:
        gold = yf.Ticker("GC=F")
        df = gold.history(period="2d", interval="15m")
        df['EMA9'] = df['Close'].ewm(span=9, adjust=False).mean()
        df['EMA21'] = df['Close'].ewm(span=21, adjust=False).mean()
        
        # Signal Detection
        df['Signal'] = 0
        df.loc[(df['EMA9'] > df['EMA21']) & (df['EMA9'].shift(1) <= df['EMA21'].shift(1)), 'Signal'] = 1
        df.loc[(df['EMA9'] < df['EMA21']) & (df['EMA9'].shift(1) >= df['EMA21'].shift(1)), 'Signal'] = -1
        return df
    except:
        return None

df = get_signals()
latest_sig = df[df['Signal'] != 0].iloc[-1] if df is not None and not df[df['Signal'] != 0].empty else None

# --- 3. PHOTO-MATCHED GAUGE COMPONENT ---
def draw_triple_gauge(symbol, title):
    gauge_html = f"""
    <div style="height:420px;">
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
    components.html(gauge_html, height=410)

# --- 4. TOP ACTION HEADER ---
if latest_sig is not None:
    action = "🚀 BUY CONFIRMED" if latest_sig['Signal'] == 1 else "🔻 SELL CONFIRMED"
    color = "#00FF88" if latest_sig['Signal'] == 1 else "#FF4B4B"
    st.markdown(f"""
        <div style="background:#111; padding:15px; border-radius:12px; border:2px solid {color}; text-align:center; margin-bottom:20px;">
            <h1 style="color:{color}; margin:0; font-size:28px;">{action} | {latest_sig.name.strftime('%H:%M')}</h1>
            <p style="color:#888; margin:0;">PATRO AI: 9/21 EMA Crossover at ${latest_sig['Close']:.2f}</p>
        </div>
    """, unsafe_allow_html=True)

# --- 5. THE GAUGE ROW (Exactly like your photo) ---
col_g1, col_g2 = st.columns(2)
with col_g1:
    draw_triple_gauge("TVC:DXY", "💵 DOLLAR (DXY) GAUGE")
with col_g2:
    draw_triple_gauge("OANDA:XAUUSD", "🏆 GOLD (XAUUSD) GAUGE")

st.divider()

# --- 6. MAIN CHART TERMINAL ---
st.markdown("### 📈 CROSSOVER ANALYSIS (M15)")

# Stable Pop-Out Link
st.link_button("🖥️ OPEN FULL SCREEN CHART", "https://www.tradingview.com/chart/?symbol=OANDA%3AXAUUSD", use_container_width=True)

chart_html = """
<div id="tv_main" style="height:550px;"></div>
<script src="https://s3.tradingview.com/tv.js"></script>
<script>
new TradingView.widget({
  "autosize": true, "symbol": "OANDA:XAUUSD", "interval": "15", "theme": "dark",
  "style": "1", "container_id": "tv_main",
  "studies": [
    { "id": "MASimple@tv-basicstudies", "inputs": { "length": 9 }, "title": "9 EMA", "plots": { "0": { "color": "#FFEB3B" } } },
    { "id": "MASimple@tv-basicstudies", "inputs": { "length": 21 }, "title": "21 EMA", "plots": { "0": { "color": "#FF5252" } } }
  ]
});
</script>"""
components.html(chart_html, height=560)

# --- 7. SIDEBAR ---
with st.sidebar:
    st.title("PATRO AI PRO")
    st.write("📍 Nairobi, Kenya")
    st.divider()
    if df is not None:
        st.metric("GOLD PRICE", f"${df['Close'].iloc[-1]:.2f}")
    if st.button("🔄 REFRESH DATA"):
        st.rerun()
