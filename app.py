import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai
from datetime import date, timedelta

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="BrokeFi", 
    page_icon="💸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- NEON THEME CSS (THE "BROKEFI" LOOK) ---
st.markdown("""
<style>
    /* MAIN BACKGROUND */
    .stApp {
        background-color: #050505;
        color: #00FFC8;
    }
    
    /* INPUT FIELDS */
    .stTextInput input, .stNumberInput input, .stDateInput input {
        color: #00FFC8 !important;
        background-color: #111 !important;
        border: 1px solid #00FFC8 !important;
    }
    
    /* METRIC CARDS */
    div[data-testid="stMetric"] {
        background-color: #0a0a0a;
        border: 1px solid #333;
        box-shadow: 0 0 10px rgba(0, 255, 200, 0.1);
        border-radius: 5px;
        padding: 10px;
        border-left: 3px solid #00FFC8;
    }
    
    /* LABELS */
    div[data-testid="stMetricLabel"] {
        color: #888 !important;
        font-family: 'Courier New', monospace;
    }
    
    div[data-testid="stMetricValue"] {
        color: #00FFC8 !important;
        text-shadow: 0 0 5px #00FFC8;
    }
    
    /* BUTTONS */
    .stButton button {
        border: 1px solid #00FFC8;
        background-color: transparent;
        color: #00FFC8;
        text-shadow: 0 0 5px #00FFC8;
    }
    .stButton button:hover {
        background-color: #00FFC8;
        color: #000;
        box-shadow: 0 0 15px #00FFC8;
    }
    
    /* TITLES */
    h1, h2, h3 {
        font-family: 'Courier New', monospace;
        color: #fff;
    }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR CONFIG ---
with st.sidebar:
    st.title("💸 BrokeFi")
    st.caption("DECENTRALIZED POVERTY MANAGEMENT")
    
    st.divider()
    
    # API KEY INPUT (Secure way)
    api_key = st.text_input("Enter Gemini API Key", type="password", help="Get one at aistudio.google.com")
    
    st.subheader("Wallet Settings")
    currency = st.selectbox("Token", ["₹", "$", "€", "£"])
    current_balance = st.number_input("Liquid Assets", min_value=0.0, value=2000.0, step=100.0)
    fixed_costs = st.number_input("Burn Rate (Bills)", min_value=0.0, value=500.0, step=100.0)
    
    today = date.today()
    semester_end = st.date_input("Runway End Date", today + timedelta(days=90))
    buffer_percent = st.slider("HODL Buffer %", 0, 30, 10)

# --- LOGIC ENGINE ---
days_remaining = (semester_end - today).days
emergency_fund = current_balance * (buffer_percent / 100)
available_cash = current_balance - fixed_costs - emergency_fund

if days_remaining <= 0:
    st.warning("RUNWAY EXPIRED.")
    st.stop()

daily_budget = available_cash / days_remaining if available_cash > 0 else 0

# --- DASHBOARD ---
st.title("BrokeFi_Terminal v1.0")

col1, col2, col3, col4 = st.columns(4)
col1.metric("TIME REMAINING", f"{days_remaining} Days")
col2.metric("LIQUIDITY", f"{currency}{current_balance:,.0f}")
col3.metric("SAFE SPEND / DAY", f"{currency}{daily_budget:.2f}")
col4.metric("LAY'S INDEX", f"{int(daily_budget/5)} Packs")

st.divider()

# --- AI ADVISOR SECTION ---
col_ai, col_chart = st.columns([1, 1.5])

with col_ai:
    st.subheader("🤖 The Oracle")
    st.caption("Ask the AI if you can afford something.")
    
    user_item = st.text_input("I want to buy...", placeholder="e.g. A new gaming mouse for 1500")
    user_price = st.number_input(f"Price ({currency})", min_value=0.0)
    
    if st.button("RUN ANALYSIS"):
        if not api_key:
            st.error("⚠️ KEY MISSING: Please enter your Gemini API Key in the sidebar.")
        else:
            try:
                # CONFIGURE AI
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-pro')
                
                # THE PROMPT (The Personality)
                prompt = f"""
                You are a sarcastic, Gen-Z financial advisor named 'BrokeFi Bot'.
                The user is a broke college student.
                
                Data:
                - Daily Budget: {currency}{daily_budget:.2f}
                - Total Savings Left: {currency}{available_cash:.2f}
                - Days Left in Semester: {days_remaining}
                
                The user wants to buy: {user_item}
                Price: {currency}{user_price}
                
                Task:
                1. Calculate how many days of budget this wipes out.
                2. If it's over the daily budget, roast them.
                3. If it's cheap, tell them to go for it but stay humble.
                4. Keep it short (max 3 sentences). Use emojis.
                """
                
                with st.spinner("Calculating Risk..."):
                    response = model.generate_content(prompt)
                    st.success(response.text)
                    
            except Exception as e:
                st.error(f"System Failure: {e}")

with col_chart:
    st.subheader("📉 Burn Rate")
    # Chart Logic
    dates = [today + timedelta(days=i) for i in range(days_remaining)]
    balances = [available_cash - (daily_budget * i) for i in range(days_remaining)]
    df_chart = pd.DataFrame({"Date": dates, "Balance": balances})
    
    fig = px.area(df_chart, x="Date", y="Balance", template="plotly_dark")
    
    # Neon Green Line
    fig.update_traces(line_color='#00FFC8', fillcolor='rgba(0, 255, 200, 0.1)')
    fig.update_layout(paper_bgcolor="#050505", plot_bgcolor="#050505")
    
    st.plotly_chart(fig, use_container_width=True)