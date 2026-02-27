# --- NEW: Price Alert Section ---
st.sidebar.divider()
st.sidebar.subheader("Set Price Alert")
alert_price = st.sidebar.number_input("Alert Price ($)", value=float(price))
alert_type = st.sidebar.selectbox("Alert When Price Goes:", ["Above", "Below"])

# --- AI Signal & Alert Logic ---
avg_price = df['Close'].mean().item()

if price > avg_price:
    st.success("AI SIGNAL: BUY")
else:
    st.error("AI SIGNAL: SELL")

# Check the Price Alert
if alert_type == "Above" and price >= alert_price:
    st.toast(f"🚨 ALERT: US30 is ABOVE {alert_price}!", icon="📈")
    st.warning(f"PRICE ALERT: Current price ${price:,.2f} is above your target!")
elif alert_type == "Below" and price <= alert_price:
    st.toast(f"🚨 ALERT: US30 is BELOW {alert_price}!", icon="📉")
    st.warning(f"PRICE ALERT: Current price ${price:,.2f} is below your target!")
