import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import hmac

# --- 1. BOOT & SECURITY ---
st.set_page_config(page_title="PATRO AI PRO", layout="wide")

def check_password():
    def credentials_entered():
        if (st.session_state["username"] == st.secrets["username"] and 
            hmac.compare_digest(st.session_state["password"], st.secrets["password"])):
            st.session_state["password_correct"] = True
            del st.session_state["password"]
            del st.session_state["username"]
        else: st.session_state["password_correct"] = False
    if st.session_state.get("password_correct", False): return True
    st.markdown('<h1 style="color:#00ff00; text-align:center;">🛡️ PATRO AI PRO</h1>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.text_input("User Identity", key="username")
        st.text_input("Command Key", type="password", key="password")
        st.button("INITIALIZE SYSTEM", on_click=credentials_entered, use_container_width=True)
    return False

if not check_password(): st.stop()

# --- 2. THE STABLE ENGINE ---
@st.cache_data(ttl=60)
def get_stable_data():
    try:
        # Fetching US30 Data
        df = yf.download("^DJI", period="1d", interval="1m", progress=False)
        # Fix for multi-index headers
        df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
        
        # Indicator: EMA 20
        df['EMA20'] = df['Close'].ewm(span=20, adjust=False).mean()
        
        # Indicator: RSI 14
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        df['RSI'] = 100 - (100 / (1 + (gain / loss)))
        
        # Logic: Trend & Entry
        df['Trend'] = 0
        df.loc[df['Close'] > df['EMA20'], 'Trend'] = 1
        df.loc[df['Close'] < df['EMA20'], 'Trend'] = -1
        df['Entry'] = df['Trend'].diff()
        return df
    except Exception as e:
        st.error(f"System Error: {e}")
        return None

df = get_stable_data()

if df is not None:
    # --- 3. TOP DASHBOARD ---
    last_sig = "BUY" if df['Trend'].iloc[-1] == 1 else "SELL"
    sig_color = "#00ff00" if last_sig == "BUY" else "#ff4b4b"
    
    st.markdown(f"<h1 style='text-align:center; color:{sig_color};'>LIVE SIGNAL: {last_sig}</h1>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    c1.metric("US30 PRICE", f"${df['Close'].iloc[-1]:,.2f}")
    c2.metric("CURRENT RSI", f"{df['RSI'].iloc[-1]:.2f}")
    c3.metric("EMA 20", f"{df['EMA20'].iloc[-1]:.2f}")

    # --- 4. TRIPLE-AXIS CHART ---
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, 
                        vertical_spacing=0.02, 
                        row_heights=[0.6, 0.2, 0.2])

    # 4a. Candlesticks & Signal Tags
    fig.add_trace(go.Candlestick(
        x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
        name='Price', increasing_line_color='#00ff00', decreasing_line_color='#ff4b4b'
    ), row=1, col=1)

    # Adding the BUY/SELL Labels
    buys = df[df['Entry'] == 2]
    fig.add_trace(go.Scatter(x=buys.index, y=buys['Low']*0.9998, mode='markers+text', 
                             text="BUY", textposition="bottom center",
                             marker=dict(color='#00ff00', size=12, symbol='triangle-up')), row=1, col=1)

    sells = df[df['Entry'] == -2]
    fig.add_trace(go.Scatter(x=sells.index, y=sells['High']*1.0002, mode='markers+text', 
                             text="SELL", textposition="top center",
                             marker=dict(color='#ff4b4b', size=12, symbol='triangle-down')), row=1, col=1)

    # 4b. Volume Bars
    fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name='Volume', marker_color='grey', opacity=0.5), row=2, col=1)

    # 4c. RSI Oscillator
    fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], line=dict(color='purple', width=2), name='RSI'), row=3, col=1)
    fig.add_hline(y=70, line_dash="dot", line_color="red", row=3, col=1)
    fig.add_hline(y=30, line_dash="dot", line_color="green", row=3, col=1)

    fig.update_layout(template='plotly_dark', height=900, xaxis_rangeslider_visible=False, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

# --- 5. SIDEBAR ---
with st.sidebar:
    st.markdown("### 🛠️ SYSTEM CONTROL")
    if st.button("🔄 REFRESH AI"):
        st.cache_data.clear()
        st.rerun()
