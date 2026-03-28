import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime
import pytz
import yfinance as yf

# --- 1. TRENDMASTER CORE LOGIC ---
def get_market_data():
    try:
        gold = yf.Ticker("GC=F")
        df = gold.history(period="5d", interval="15m")
        if df.empty: return 4493.79, 4490.00, 4492.50 # Fallbacks
        
        current_p = round(df['Close'].iloc[-1], 2)
        
        # VWAP Calculation (Simplified for Intraday)
        df['Typical_Price'] = (df['High'] + df['Low'] + df['Close']) / 3
        vwap = (df['Typical_Price'] * df['Volume']).cumsum() / df['Volume'].cumsum()
        current_vwap = round(vwap.iloc[-1], 2)
        
        # Pivot HL (Last 5 bars)
        recent_low = df['Low'].tail(5).min()
        
        return current_p, recent_low, current_vwap
    except:
        return 4493.79, 4485.00, 4491.00

price, pivot_low, vwap_val = get_market_data()

# --- 2. TRENDMASTER MODE STATUS ---
# Logic: Price must be > VWAP and > Pivot Low for TrendMaster Bullish
is_vwap_aligned = price > vwap_val
is_pivot_aligned = price > pivot_low
trendmaster_mode = "ACTIVE 🚀" if (is_vwap_aligned and is_pivot_aligned) else "SCANNING..."

# --- 3. DYNAMIC SIGNAL DIALOG ---
@st.dialog("🎯 TRENDMASTER EXECUTION", width="medium")
def show_trendmaster_signal(p, v, pl):
    st.markdown(f"""
    <div style="text-align: center; border-bottom: 1px solid #333; padding-bottom: 10px;">
        <h1 style="color: #00FF88; margin: 0;">GOD MODE BUY</h1>
        <p style="color: #888;">VWAP: {v} | PIVOT HL: {pl}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Entry is current market price
    entry = p
    sl = pl - 2.50  # SL protected below the Pivot Low
    tp = entry + ((entry - sl) * 2.5) # Dynamic 1:2.5 RR
    
    c1, c2 = st.columns(2)
    with c1:
        st.metric("ENTRY (LIVE)", f"{entry}")
        st.metric("STOP LOSS", f"{sl:.2f}", delta="Below Pivot", delta_color="inverse")
    with c2:
        st.metric("TAKE PROFIT", f"{tp:.2f}", delta="Target High")
        st.metric("MODE", "TRENDMASTER")

    if st.button("EXECUTE TRADE"):
        st.toast("Injecting Order to MT5 Terminal...", icon="🔥")

# --- 4. HUD & MAIN TERMINAL ---
st.markdown(f"""
<div style="background: #0a0a0a; padding:20px; border-radius:15px; border: 1px solid #222; border-left: 5px solid #00FF88;">
    <h2 style="margin:0; color:#00FF88;">PATRO AI | TRENDMASTER MODE</h2>
    <p style="margin:0; color:#888;">STATUS: {trendmaster_mode} | LIVE PRICE: ${price}</p>
</div>
""", unsafe_allow_html=True)

col_l, col_r = st.columns([1, 4])

with col_l:
    st.write("### ⚡ CONFLUENCE")
    st.info(f"VWAP: {vwap_val}")
    st.info(f"Pivot Low: {pivot_low}")
    
    if st.button("🚀 GENERATE SIGNAL"):
        if trendmaster_mode == "ACTIVE 🚀":
            show_trendmaster_signal(price, vwap_val, pivot_low)
        else:
            st.error("Market not aligned for God Mode.")

with col_r:
    # TradingView Chart with VWAP and Pivots
    components.html("""
    <div id="tv_chart" style="height:500px;"></div>
    <script src="https://s3.tradingview.com/tv.js"></script>
    <script>
    new TradingView.widget({
      "autosize": true, "symbol": "OANDA:XAUUSD", "interval": "15", "theme": "dark",
      "container_id": "tv_chart",
      "studies": ["VWAP@tv-basicstudies", "PivotPointsHighLow@tv-basicstudies"]
    });
    </script>""", height=510)
