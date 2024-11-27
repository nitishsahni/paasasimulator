import streamlit as st
import numpy as np
import pandas as pd
from PIL import Image
from streamlit_theme import st_theme


# Set the page configuration with sidebar default open
st.set_page_config(
    page_title="Financial Simulation Tool",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"  # Ensure the sidebar is open by default
)

# Load and Display the Logo on the Main Page
light_logo = Image.open("paasa_logo_black.png")  # Light mode logo
dark_logo = Image.open("paasa_logo.png")   # Dark mode logo

# Get the current theme
try:
    theme = st_theme().get('base')
except:
    theme = "light"


# Display the appropriate logo based on the theme
if theme == "light":
    st.image(light_logo, width=100)  # Adjust the size as needed
else:
    st.image(dark_logo, width=100)   # Adjust the size as needed

# Title
st.write("Track your progress toward financial goals by adjusting your assumptions in the sidebar.")

# Add preset scenarios
st.sidebar.subheader("Simulator")
preset = st.sidebar.selectbox(
    "Select a Goal Template",
    ["Custom", "Education", "EB-5 Visa", "Property", "Retiring Abroad"]
)

# Set preset values based on selection
if preset == "Education":
    default_goal = 250000  # Average 4-year private college cost
    default_horizon = 18   # Planning from birth to college
    default_savings = 10000
    default_monthly = 500
elif preset == "EB-5 Visa":
    default_goal = 800000  # EB-5 investment requirement
    default_horizon = 5    # Typical planning horizon for EB-5
    default_savings = 100000
    default_monthly = 10000
elif preset == "Property":
    default_goal = 400000  # Average home down payment + closing costs
    default_horizon = 7    # Typical saving period for house down payment
    default_savings = 20000
    default_monthly = 1000
elif preset == "Retiring Abroad":
    default_goal = 500000  # Conservative retirement fund for abroad
    default_horizon = 15   # Mid-term retirement planning
    default_savings = 50000
    default_monthly = 2000
else:  # Custom
    default_goal = 100000
    default_horizon = 10
    default_savings = 10000
    default_monthly = 500

st.sidebar.divider()

# Current Financials (updated with presets)
current_savings = st.sidebar.number_input("Current Savings ($)", value=default_savings)
monthly_contribution = st.sidebar.number_input("Monthly Contribution ($)", value=default_monthly)

# Financial Goals (updated with presets)
goal_amount = st.sidebar.number_input("Target Goal Amount ($)", value=default_goal)
time_horizon = st.sidebar.number_input("Time Horizon (years)", value=default_horizon)

# Assumptions
annual_return = st.sidebar.slider("Expected Annual Return (%)", min_value=0, max_value=20, value=7) / 100
inflation_rate = st.sidebar.slider("Inflation Rate (%)", min_value=0, max_value=10, value=2) / 100

# Calculations
def calculate_future_value(p, c, r, t):
    fv_savings = p * (1 + r)**t
    fv_contributions = c * (((1 + r)**t - 1) / r) * (1 + r)
    return fv_savings + fv_contributions

# Use real return rate (nominal return - inflation)
real_return = annual_return - inflation_rate
future_value = calculate_future_value(current_savings, monthly_contribution * 12, real_return, time_horizon)

# Inflation-adjusted Goal
inflation_adjusted_goal = goal_amount * (1 + inflation_rate)**time_horizon
shortfall_or_surplus = future_value - inflation_adjusted_goal

# Add tabs for better organization
tab1, tab2, tab3 = st.tabs(["Overview", "Detailed Analysis", "Recommendations"])

with tab1:
    # Create two columns for results
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(
            label="Projected Future Value",
            value=f"${future_value:,.0f}",
            delta=f"${shortfall_or_surplus:,.0f}" if shortfall_or_surplus >= 0 else f"-${-shortfall_or_surplus:,.0f}"
        )
    
    with col2:
        st.metric(
            label="Inflation-Adjusted Goal",
            value=f"${inflation_adjusted_goal:,.0f}",
            delta=f"{(future_value/inflation_adjusted_goal - 1)*100:.1f}% vs goal"
        )

with tab2:
    # Enhanced visualization options
    chart_type = st.selectbox(
        "Select Chart Type",
        ["Line Chart", "Area Chart", "Bar Chart"]
    )
    
    # Calculate monthly data for more granular view
    months = np.arange(1, time_horizon * 12 + 1)
    monthly_values = [
        calculate_future_value(
            current_savings,
            monthly_contribution,  # Remove the *12 since we're calculating monthly
            real_return/12,  # Monthly rate
            t  # Use full months, not t/12
        ) 
        for t in months
    ]
    
    data_monthly = pd.DataFrame({
        "Month": months,
        "Projected Savings": monthly_values,
        "Monthly Goal": np.linspace(current_savings, inflation_adjusted_goal, len(months)),
    })
    data_monthly.set_index("Month", inplace=True)
    
    if chart_type == "Line Chart":
        st.line_chart(data_monthly)
    elif chart_type == "Area Chart":
        st.area_chart(data_monthly)
    else:
        st.bar_chart(data_monthly)

with tab3:
    # Add recommendations based on results
    st.header("Recommendations")
    
    if shortfall_or_surplus < 0:
        additional_monthly = abs(shortfall_or_surplus) / (((1 + annual_return)**time_horizon - 1) / annual_return) / 12
        st.warning(f"To reach your goal, consider increasing your monthly contribution by ${additional_monthly:,.2f}")
        
        # Add alternative scenarios
        st.subheader("Alternative Scenarios")
        col1, col2 = st.columns(2)
        with col1:
            st.write("If you increase return by 1%:")
            new_fv = calculate_future_value(current_savings, monthly_contribution * 12, annual_return + 0.01, time_horizon)
            st.metric("New Future Value", f"${new_fv:,.0f}", f"${new_fv - future_value:,.0f}")
        
        with col2:
            st.write("If you extend time horizon by 1 year:")
            extended_fv = calculate_future_value(current_savings, monthly_contribution * 12, annual_return, time_horizon + 1)
            st.metric("New Future Value", f"${extended_fv:,.0f}", f"${extended_fv - future_value:,.0f}")
    else:
        st.success("You're on track to meet your financial goals! Consider:")
        st.write("- Increasing your emergency fund")
        st.write("- Diversifying your investments")
        st.write("- Setting more ambitious financial goals")

# # Add sidebar improvements
# with st.sidebar:
#     st.markdown("---")
#     show_advanced = st.checkbox("Show Advanced Options")
    
#     if show_advanced:
#         st.subheader("Advanced Settings")
#         compound_freq = st.select_slider(
#             "Compound Frequency",
#             options=["Annually", "Semi-annually", "Quarterly", "Monthly"],
#             value="Monthly"
#         )
#         risk_tolerance = st.select_slider(
#             "Risk Tolerance",
#             options=["Conservative", "Moderate", "Aggressive"],
#             value="Moderate"
#         )
