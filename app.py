import streamlit as st
import pandas as pd
import pandas_ta as ta
import yfinance as yf
import plotly.graph_objects as go

# --- 1. CORE CONFIG ---
st.set_page_config(page_title="PATRO AI PRO V11.6.2", layout="wide")
st.markdown("<style>.stApp { background: #010101; color: #ffffff; }</style>", unsafe_allow_html=True)

# --- 2. PERMANENT UI ---
st.title("🌌 PATRO AI PRO V11.6.2 | MASTER COMMAND")

with st.sidebar:
    st.header("🏢 INSTITUTIONAL DESK")
    asset_choice = st.selectbox("Market Target", ["GOLD", "GBPUSD", "US30"])
    ticker_map = {"GOLD":"GC=F", "GBPUSD":"GBPUSD=X", "US30":"^DJI"}
    target_ticker = ticker_map[asset_choice]
    
    st.divider()
    # Risk Management (Hard-Lock SL)
    st.subheader("🛡️ RISK MGMT")
    lot_size = st.number_input("Lot Size", value=0.1, step=0.01)
    risk_percent = st.slider("Risk Tolerance %", 0.5, 3.0, 1.0)
    
    st.divider()
    mtf_spot = st.empty()  # Power Matrix
    v_rec_spot = st.empty() # V-Recovery Alert
    sl_spot = st.empty() # Stop Loss Display

# --- 3. ANALYTICS ENGINE ---
def get_mtf_data(ticker, interval):
    try:
        df = yf.download(ticker, period="2d", interval=interval, progress=False, auto_adjust=True)
        if df.empty: return pd.DataFrame()
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        
        # Hidden Calculation Engines (Powering the Score)
        df['RSI'] = ta.rsi(df.Close, length=14)
        macd = ta.macd(df.Close)
        df['MACD'] = macd['MACD_12_26_9']
        df['SIG'] = macd['MACDs_12_26_9']
        return df
    except: return pd.DataFrame()

@st.fragment(run_every="8s") # 8-second refresh cycle
def run_master_pulse(ticker, label):
    # Data Stream
    d1, d5, d15 = get_mtf_data(ticker, "1m"), get_mtf_data(ticker, "5m"), get_mtf_data(ticker, "15m")
    if d1.empty: 
        st.warning("Awaiting Market Pulse...")
        return

    # --- A. CONFLUENCE BIAS (Hidden Matrix) ---
    def get_bias(df):
        r, m, s = df['RSI'].iloc[-1], df['MACD'].iloc[-1], df['SIG'].iloc[-1]
        if r > 50 and m > s: return "🟢 BULL"
        if r < 50 and m < s: return "🔴 BEAR"
        return "⚪ NEUTRAL"

    b1, b5, b15 = get_bias(d1), get_bias(d5), get_bias(d15)

    # --- B. INSTITUTIONAL RECOVERY & SL ---
    session_low = d1['Low'].min()
    current_price = d1['Close'].iloc[-1]
    
    # 2-Pip Hard-Lock Stop Loss
    sl_buffer = (0.0002 if "USD" in label else 1.0)
    hard_lock_sl = session_low - sl_buffer
    
    is_v_rebound = (current_price > session_low) and (b1 == "🟢 BULL") and (d1['Close'].iloc[-1] > d1['Open'].iloc[-1])

    # --- C. SIDEBAR UPDATES ---
    with mtf_spot.container():
        st.caption(f"MTF MATRIX ({pd.Timestamp.now().strftime('%H:%M:%S')} EAT)")
        st.table(pd.DataFrame([{"TF": "1M", "Power": b1}, {"TF": "5M", "Power": b5}, {"TF": "15M", "Power": b15}]))

    with v_rec_spot.container():
        if is_v_rebound:
            st.success("🔥 V-RECOVERY: ACTIVE")
            st.write(f"Target: {d1.High.max():,.2f}")
        else: st.info("SCANNING: No Rebound")
    
    with sl_spot.container():
        st.markdown(f"""
            <div style="border: 1px solid #FF3366; padding:10px; border-radius:5px; background: #FF336611;">
                <p style="margin:0; font-size:10px;">HARD-LOCK SL</p>
                <h3 style="margin:0; color:#FF3366;">{hard_lock_sl:,.2f}</h3>
            </div>
        """, unsafe_allow_html=True)

    # --- D. DASHBOARD SCORING ---
    is_strong_buy = (b1 == b5 == b15 == "🟢 BULL")
    is_strong_sell = (b1 == b5 == b15 == "🔴 BEAR")
    score = 98 if is_strong_buy else 2 if is_strong_sell else 50
    color = "#00FF88" if score > 90 else "#FF3366" if score < 10 else "#FFA500"

    c1, c2, c3 = st.columns([1, 1, 2])
    with c1:
        st.markdown(f"<div style='border:2px solid {color}; padding:10px; border-radius:10px; text-align:center;'><h2>{score}%</h2><p>AI CONFIDENCE</p></div>", unsafe_allow_html=True)
    with c2:
        st.metric("LIVE PRICE", f"{current_price:,.2f}", delta=f"{current_price - d1.Open.iloc[-1]:.2f}")
    with c3:
        signal = "🚀 STRONG BUY" if is_strong_buy else "📉 STRONG SELL" if is_strong_sell else "⌛ ACCUMULATING"
        st.markdown(f"<h1 style='color:{color};'>{signal}</h1>", unsafe_allow_html=True)

    # --- E. INSTITUTIONAL CHART ---
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=d1.index, open=d1.Open, high=d1.High, low=d1.Low, close=d1.Close, name="Price",
                                 increasing_line_color='#00FF88', decreasing_line_color='#FF3366'))
    
    # Session Low / SL Line
    fig.add_hline(y=session_low, line_dash="dash", line_color="#FF3366", annotation_text="Safety Floor")
    
    fig.update_layout(height=550, template="plotly_dark", xaxis_rangeslider_visible=False, 
                      margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True, key=f"pulse_{label}")

# --- 4. EXECUTION ---
run_master_pulse(target_ticker, asset_choice)
