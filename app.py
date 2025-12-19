import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date, timedelta

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Student Survival Guide", 
    page_icon="🎓",
    layout="wide" # This uses the full width of the screen instead of a narrow center column
)

# --- CUSTOM STYLING (CSS) ---
# This hides the default Streamlit menu to make it look like a standalone app
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# --- SIDEBAR: SETTINGS ---
with st.sidebar:
    st.title("⚙️ Settings")
    currency = st.selectbox("Currency", ["₹", "$", "€", "£"])
    
    st.markdown("### 💰 Financials")
    current_balance = st.number_input("Current Bank Balance", min_value=0.0, value=1500.0, step=50.0)
    fixed_costs = st.number_input("Bills Due (Rent, etc.)", min_value=0.0, value=500.0, step=50.0)
    
    st.markdown("### ⏳ Timeline")
    today = date.today()
    default_end = today + timedelta(days=90)
    semester_end = st.date_input("Semester End Date", default_end)
    
    st.divider()
    buffer_percent = st.slider("Safety Buffer (%)", 0, 30, 15)

# --- CALCULATIONS ---
days_remaining = (semester_end - today).days
emergency_fund = current_balance * (buffer_percent / 100)
available_cash = current_balance - fixed_costs - emergency_fund

if days_remaining <= 0:
    st.error("🎉 The semester is over! You made it!")
    st.stop()

daily_budget = available_cash / days_remaining if available_cash > 0 else 0

# --- HEADER SECTION ---
st.title("🎓 Student Survival Guide")
st.markdown(f"**Today is {today.strftime('%B %d, %Y')}**")

# --- UI TABS ---
# This splits the app into 3 clean sections
tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "🛒 Decision Helper", "📈 Analytics"])

# === TAB 1: THE DASHBOARD ===
with tab1:
    # Top Row: The Big Numbers
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(label="🗓 Days Left", value=days_remaining)
    with col2:
        st.metric(label="🏦 Total Balance", value=f"{currency}{current_balance:,.0f}")
    with col3:
        st.metric(label="🛡️ Safety Net", value=f"{currency}{emergency_fund:,.0f}")
    with col4:
        # We color this Red if negative, Green if positive
        st.metric(
            label="💸 DAILY BUDGET", 
            value=f"{currency}{daily_budget:.2f}", 
            delta="Safe to Spend" if daily_budget > 10 else "Tight Budget",
            delta_color="normal"
        )

    st.divider()
    
    # Semester Progress Bar
    total_semester_days = 120 # Estimate
    progress = 1 - (days_remaining / total_semester_days)
    # Clamp progress between 0 and 1
    progress = max(0.0, min(1.0, progress))
    
    st.caption("⏳ Semester Progress")
    st.progress(progress)
    
    if available_cash < 0:
        st.error(f"🚨 DANGER ZONE: You are short by {currency}{abs(available_cash):.2f}. You need a loan or a gig.")

# === TAB 2: DECISION HELPER ===
with tab2:
    st.subheader("Should I buy this?")
    
    c1, c2 = st.columns([1, 1])
    
    with c1:
        item_name = st.text_input("Item Name", placeholder="e.g. Concert Tickets")
        item_cost = st.number_input(f"Price ({currency})", min_value=0.0, step=1.0)
    
    with c2:
        st.write("### The Verdict:")
        if item_cost > 0:
            impact_days = item_cost / daily_budget if daily_budget > 0 else 999
            
            # Logic for the verdict
            if item_cost > daily_budget * 3:
                st.error(f"🛑 **NO WAY.** This costs {impact_days:.1f} days of living expenses.")
            elif item_cost > daily_budget:
                st.warning(f"⚠️ **Risky.** This is over your daily limit. You'll have to starve for {impact_days:.1f} days.")
            else:
                st.success(f"✅ **Approved.** This fits in your budget! ({impact_days:.1f} days worth of cash)")
            
            # --- THE LAY'S CHIPS UPDATE ---
            chip_price = 5.0 # Cost of one small pack
            chip_count = int(item_cost / chip_price)
            
            st.info(f"🥔 Just so you know, that is **{chip_count} packs** of Magic Masala Lay's.")

# === TAB 3: ANALYTICS ===
with tab3:
    st.subheader("📉 The Burn Down")
    
    # Create better data for plotting
    dates = [today + timedelta(days=i) for i in range(days_remaining)]
    balances = [available_cash - (daily_budget * i) for i in range(days_remaining)]
    
    df_chart = pd.DataFrame({"Date": dates, "Projected Balance": balances})
    
    # Use Plotly for an interactive chart
    fig = px.area(
        df_chart, 
        x="Date", 
        y="Projected Balance", 
        template="plotly_dark",
        color_discrete_sequence=['#00CC96'] # Green color
    )
    
    # Add a red line for 0
    fig.add_hline(y=0, line_dash="dot", annotation_text="Broke Line", annotation_position="bottom right", line_color="red")
    
    st.plotly_chart(fig, use_container_width=True)