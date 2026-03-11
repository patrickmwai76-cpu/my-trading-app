import streamlit as st
import pandas as pd
import pandas_ta as ta
import yfinance as yf
import plotly.graph_objects as go

# --- 1. SETTINGS ---
st.set_page_config(page_title="PATRO AI PRO V12.0.3", layout="wide")
st.markdown("<style>.stApp { background: #010101; color: #ffffff; }</style>", unsafe_allow_html=True)

def get_data(ticker):
    df = yf.download(ticker, period="2d", interval="5m", progress=False, auto_adjust=True)
    if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
    df['ATR'] = ta.atr(df.High, df.Low, df.Close, length=14)
    df['VWAP'] = ta.vwap(df.High, df.Low, df.Close, df.Volume)
    df['RSI'] = ta.rsi(df.Close, length=14)
    return df

# --- 2. THE DASHBOARD ---
st.title("🌌 PATRO AI PRO | V12.0.3")

with st.sidebar:
    st.header("⚙️ RISK MANAGER")
    balance = st.number_input("M-Pesa Balance (USD)", value=100.0)
    risk_pct = st.slider("Risk Per Trade %", 1, 5, 2)
    asset = st.selectbox("Market", ["GOLD", "GBPUSD", "US30"])
    t_map = {"GOLD":"GC=F", "GBPUSD":"GBPUSD=X", "US30":"^DJI"}

@st.fragment(run_every="10s")
def live_engine():
    df = get_data(t_map[asset])
    cp = df.Close.iloc[-1]
    atr = df.ATR.iloc[-1]
    
    # CALCULATE TP/SL (Institutional Style)
    # Buy Setup: SL is below the last wick. Sell Setup: SL is above.
    sl_dist = atr * 2
    tp_dist = sl_dist * 2.5 # 1:2.5 Risk/Reward
    
    bias = "BUY" if cp > df.VWAP.iloc[-1] else "SELL"
    
    # UI METRICS
    c1, c2, c3 = st.columns(3)
    with c1:
        color = "#00FF88" if bias == "BUY" else "#FF3366"
        st.markdown(f"<div style='border:2px solid {color}; padding:10px; border-radius:10px; text-align:center;'><h3>{bias} ZONE</h3></div>", unsafe_allow_html=True)
    with c2:
        st.metric("CURRENT PRICE", f"{cp:,.2f}")
    with c3:
        # LOT SIZE CALCULATION (For Gold)
        risk_cash = balance * (risk_pct/100)
        lot_size = risk_cash / (sl_dist * 100) # Gold pip math
        st.metric("SUGGESTED LOT", f"{lot_size:.2f}")

    # --- THE SMART CHART ---
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=df.index, open=df.Open, high=df.High, low=df.Low, close=df.Close, name="Price"))
    
    # Draw SL/TP Lines Automatically based on Bias
    if bias == "BUY":
        tp_price, sl_price = cp + tp_dist, cp - sl_dist
        fig.add_hline(y=tp_price, line_dash="dash", line_color="#00FF88", annotation_text="TAKE PROFIT")
        fig.add_hline(y=sl_price, line_dash="dash", line_color="#FF3366", annotation_text="STOP LOSS")
    else:
        tp_price, sl_price = cp - tp_dist, cp + sl_dist
        fig.add_hline(y=tp_price, line_dash="dash", line_color="#00FF88", annotation_text="TAKE PROFIT")
        fig.add_hline(y=sl_price, line_dash="dash", line_color="#FF3366", annotation_text="STOP LOSS")

    # DETECT LIQUIDITY SWEEPS (High/Low of Previous Session)
    session_high = df.High.tail(24).max()
    session_low = df.Low.tail(24).min()
    fig.add_hline(y=session_high, line_color="orange", opacity=0.3, annotation_text="BANK SELL ZONE")
    fig.add_hline(y=session_low, line_color="orange", opacity=0.3, annotation_text="BANK BUY ZONE")

    fig.update_layout(height=600, template="plotly_dark", xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

    # ACTIONABLE INSTRUCTION
    if bias == "BUY" and cp < session_high:
        st.success(f"✅ ACTION: Entry valid. Target {tp_price:.2f}. Watch for rejection at {session_high:.2f}")
    elif bias == "SELL" and cp > session_low:
        st.error(f"✅ ACTION: Entry valid. Target {tp_price:.2f}. Watch for bounce at {session_low:.2f}")

live_engine()
