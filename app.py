import streamlit as st
import pandas as pd
from datetime import date, timedelta

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Student Survival Guide", page_icon="🎓")

# --- STYLE & HEADER ---
st.title("🎓 The Student Survival Guide")
st.markdown("Stop wondering if you're broke. Know for sure.")

# --- SIDEBAR: THE INPUTS ---
st.sidebar.header("📝 Set Your Baseline")

currency = st.sidebar.radio("Currency", ["$", "₹", "€", "£"], horizontal=True)
current_balance = st.sidebar.number_input(f"Current Bank Balance ({currency})", min_value=0.0, value=1500.0, step=10.0)
fixed_costs = st.sidebar.number_input(f"Remaining Bills/Rent this Semester ({currency})", min_value=0.0, value=500.0, step=10.0)

# Date Picker
today = date.today()
default_end = today + timedelta(days=90)
semester_end = st.sidebar.date_input("Semester End Date", default_end)

# --- LOGIC ENGINE ---
days_remaining = (semester_end - today).days

if days_remaining <= 0:
    st.error("The semester is over! Go enjoy your break!")
    st.stop()

# Safety Buffer logic (10% emergency fund)
buffer_percent = st.sidebar.slider("Emergency Buffer %", 0, 30, 10)
emergency_fund = current_balance * (buffer_percent / 100)

available_cash = current_balance - fixed_costs - emergency_fund

# --- MAIN DASHBOARD ---
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="Days Remaining", value=f"{days_remaining} days")

with col2:
    st.metric(label="Emergency Fund", value=f"{currency}{emergency_fund:,.2f}")

with col3:
    if available_cash < 0:
        st.error("You are in debt!")
        daily_budget = 0
    else:
        daily_budget = available_cash / days_remaining
        st.metric(label="✅ Daily Safe Spend", value=f"{currency}{daily_budget:,.2f}")

st.divider()

# --- THE "CAN I AFFORD THIS?" CALCULATOR ---
st.subheader(f"🤔 Can I afford this?")

col_calc1, col_calc2 = st.columns([2, 1])

with col_calc1:
    item_name = st.text_input("What do you want to buy?", placeholder="e.g. New Sneakers")
    item_cost = st.number_input(f"How much is it? ({currency})", min_value=0.0, step=1.0)

with col_calc2:
    # RAMEN MATH
    ramen_price = 0.50 # Assuming 50 cents/rupees per pack generic
    
    if item_cost > 0:
        st.write("### The Cost in Reality:")
        
        # 1. Budget Impact
        days_lost = item_cost / daily_budget if daily_budget > 0 else 0
        st.warning(f"This purchase wipes out **{days_lost:.1f} days** of your budget.")
        
        # 2. Ramen Translation
        ramen_count = int(item_cost / ramen_price)
        st.info(f"🍜 That is equivalent to **{ramen_count} packs** of instant noodles.")
        
        if item_cost > daily_budget:
            st.error("🚫 DON'T DO IT. That's over your daily limit!")
        else:
            st.success("✅ Go for it. It fits today's budget.")

# --- VISUALIZATION ---
st.divider()
st.subheader("📉 The Burn Down Chart")

# Create a fake projection data for the chart
data = {
    'Day': range(days_remaining),
    'Balance Projection': [available_cash - (daily_budget * i) for i in range(days_remaining)]
}
df = pd.DataFrame(data)
st.line_chart(df, x='Day', y='Balance Projection')