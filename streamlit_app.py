# This is the streamlit version of the index.html file that is present in the main branch

import streamlit as st
import pandas as pd
import requests
from io import BytesIO

# --- Page Configuration ---
st.set_page_config(
    page_title="ChurnGuard AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for Styling ---
st.markdown("""
<style>
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes slideInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    @keyframes pulseGlow {
        0%, 100% { text-shadow: 0 0 5px #c084fc; }
        50% { text-shadow: 0 0 20px #818cf8, 0 0 30px #38bdf8; }
    }

    /* Main Background & Styling */
    .stApp {
        background-image:
            radial-gradient(ellipse 50% 80% at 10% 110%, rgba(37, 99, 235, 0.3), transparent),
            radial-gradient(ellipse 50% 80% at 90% -10%, rgba(139, 92, 246, 0.3), transparent);
        background-color: #030712;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background: rgba(17, 24, 39, 0.8);
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(55, 65, 81, 0.3);
    }

    /* Glass Card Effect for Main Content */
    .glass-card {
        background: rgba(17, 24, 39, 0.7);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(55, 65, 81, 0.3);
        border-radius: 1rem;
        padding: 1.5rem;
        animation: fadeIn 0.5s ease-out forwards;
    }
    
    /* Title and Subtitle */
    .main-title {
        text-align: center;
        animation: fadeIn 1s ease-out;
    }
    .subtitle {
        text-align: center;
        color: #cbd5e1; /* Brighter color */
        font-size: 1.2rem; /* Slightly larger */
        animation: pulseGlow 4s infinite ease-in-out, fadeIn 1.5s ease-out;
    }

    /* Brand Text Gradient */
    .brand-text {
        background: -webkit-linear-gradient(45deg, #38bdf8, #818cf8, #c084fc);
        background-clip: text;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Result Styling */
    .result-card-churn {
        box-shadow: 0 0 30px rgba(248, 113, 113, 0.4);
        border: 1px solid rgba(248, 113, 113, 0.5);
    }
    .result-card-safe {
        box-shadow: 0 0 30px rgba(74, 222, 128, 0.4);
        border: 1px solid rgba(74, 222, 128, 0.5);
    }
    
    /* AI Recommendations Styling */
    .recommendations-title {
        font-size: 1.75rem;
        font-weight: bold;
        margin-top: 2.5rem;
        margin-bottom: 1.5rem;
        text-align: left;
        animation: fadeIn 0.5s ease-out 0.2s forwards;
        opacity: 0; /* Start hidden for animation */
    }
    
    .recommendations-container {
        list-style-type: none;
        padding: 0;
    }
    
    .recommendation-item {
        background: rgba(30, 41, 59, 0.6);
        border-radius: 0.75rem;
        padding: 1rem 1.5rem;
        margin-bottom: 1rem;
        display: flex;
        align-items: flex-start;
        border: 1px solid #374151;
        opacity: 0; /* Start hidden for animation */
        animation: slideInUp 0.6s ease-out forwards;
    }
    
    /* Staggered animation for list items */
    .recommendation-item:nth-child(1) { animation-delay: 0.3s; }
    .recommendation-item:nth-child(2) { animation-delay: 0.4s; }
    .recommendation-item:nth-child(3) { animation-delay: 0.5s; }
    .recommendation-item:nth-child(4) { animation-delay: 0.6s; }
    .recommendation-item:nth-child(5) { animation-delay: 0.7s; }
    .recommendation-item:nth-child(6) { animation-delay: 0.8s; }
    .recommendation-item:nth-child(7) { animation-delay: 0.9s; }
    .recommendation-item:nth-child(8) { animation-delay: 1.0s; }


    .recommendation-item svg {
        flex-shrink: 0;
        margin-right: 1rem;
        margin-top: 0.25rem;
        color: #38bdf8; /* sky-400 */
    }
    
    .markdown-content strong {
        color: #fafa15; /* Yellow */
        font-weight: 600;
    }

</style>
""", unsafe_allow_html=True)

# --- API Configuration ---
API_BASE_URL = 'http://127.0.0.1:8000'

# --- Session State Initialization ---
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None
if 'processing' not in st.session_state:
    st.session_state.processing = False

# --- API Communication Functions ---
def call_predict_api(customer_data):
    """Sends single customer data to the backend API."""
    try:
        response = requests.post(f"{API_BASE_URL}/predict", json=customer_data, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to connect to the backend. Please ensure the API server is running. Error: {e}")
        return None

def call_predict_file_api(uploaded_file):
    """Sends a file for batch prediction to the backend API."""
    try:
        files = {'file': (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
        response = requests.post(f"{API_BASE_URL}/predict-file", files=files, timeout=60)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to process the file. Error: {e}")
        return None

# --- Sidebar UI ---
with st.sidebar:
    st.markdown("<h1 class='brand-text'>ChurnGuard AI Settings</h1>", unsafe_allow_html=True)
    st.markdown("<h3>Enter customer details to predict churn and receive AI-powered retention strategies.<h3>", unsafe_allow_html=True)
    api_key = st.text_input("🔑 Your Groq API Key", type="password", help="Required for AI recommendations.")
    tab1, tab2 = st.tabs(["👤 Single Customer", "📁 Batch File"])
    with tab1:
        st.subheader("Customer Details")
        col1, col2 = st.columns(2)
        with col1:
            tenure = st.number_input("Tenure (Months)", min_value=0, value=12)
            complain = st.selectbox("Has Complained?", options=[0, 1], format_func=lambda x: "Yes" if x == 1 else "No")
            satisfaction_score = st.slider("Satisfaction Score", 1, 5, 3)
            day_since_last_order = st.number_input("Days Since Last Order", min_value=0, value=10)
            order_count = st.number_input("Order Count", min_value=0, value=5)
        with col2:
            cashback_amount = st.number_input("Cashback Amount", min_value=0.0, value=150.0, format="%.2f")
            warehouse_to_home = st.number_input("Warehouse to Home (km)", min_value=0.0, value=15.0, format="%.1f")
            hour_spend_on_app = st.number_input("Hours on App", min_value=0.0, value=3.0, format="%.1f")
            coupon_used = st.number_input("Coupons Used", min_value=0, value=1)
        prefered_order_cat = st.selectbox("Preferred Category", options=[0, 1, 2, 3], format_func=lambda x: {0: "Laptop & Accessory", 1: "Fashion", 2: "Grocery", 3: "Others"}[x])
        with st.expander("Show All Fields"):
            col1, col2 = st.columns(2)
            with col1:
                preferred_login_device = st.selectbox("Login Device", options=[0, 1], format_func=lambda x: {0: "Mobile Phone", 1: "Computer"}[x])
                city_tier = st.slider("City Tier", 1, 3, 1)
                gender = st.selectbox("Gender", options=[0, 1], format_func=lambda x: {0: "Female", 1: "Male"}[x])
                number_of_device_registered = st.slider("Registered Devices", 1, 6, 3)
            with col2:
                preferred_payment_mode = st.selectbox("Payment Mode", options=[0, 1], format_func=lambda x: {0: "Cash on Delivery", 1: "Digital Payment"}[x])
                marital_status = st.selectbox("Marital Status", options=[0, 1, 2], format_func=lambda x: {0: "Divorced", 1: "Single", 2: "Married"}[x])
                number_of_address = st.slider("Number of Addresses", 1, 10, 3)
                order_amount_hike = st.number_input("Order Amount Hike (%)", value=15.0, format="%.1f")
        if st.button("Analyze Churn Risk", use_container_width=True, type="primary"):
            if not api_key: st.warning("Please enter your Groq API key.")
            else:
                st.session_state.processing = True
                customer_data = { "api_key": api_key, "Tenure": float(tenure), "PreferredLoginDevice": int(preferred_login_device), "CityTier": int(city_tier), "WarehouseToHome": float(warehouse_to_home), "PreferredPaymentMode": int(preferred_payment_mode), "Gender": int(gender), "HourSpendOnApp": float(hour_spend_on_app), "NumberOfDeviceRegistered": int(number_of_device_registered), "PreferedOrderCat": int(prefered_order_cat), "SatisfactionScore": int(satisfaction_score), "MaritalStatus": int(marital_status), "NumberOfAddress": int(number_of_address), "Complain": int(complain), "OrderAmountHikeFromlastYear": float(order_amount_hike), "CouponUsed": float(coupon_used), "OrderCount": float(order_count), "DaySinceLastOrder": float(day_since_last_order), "CashbackAmount": float(cashback_amount) }
                with st.spinner("Analyzing Customer Profile..."):
                    result = call_predict_api(customer_data)
                    st.session_state.analysis_result = result
                st.session_state.processing = False
    with tab2:
        st.subheader("Upload Customer Data File")
        uploaded_file = st.file_uploader("Upload a CSV or XLSX file", type=['csv', 'xlsx'])
        if st.button("Process Batch File", use_container_width=True, type="primary", disabled=(uploaded_file is None)):
            st.session_state.processing = True
            with st.spinner("Processing file and predicting churn..."):
                result = call_predict_file_api(uploaded_file)
                st.session_state.analysis_result = result
            st.session_state.processing = False

# --- Main Content Area ---
st.markdown("<h1 class='main-title brand-text'>ChurnGuard AI</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Predict and Prevent Customer Churn with AI-Powered Insights</p>", unsafe_allow_html=True)

if st.session_state.analysis_result:
    result = st.session_state.analysis_result
    
    if "prediction" in result:
        is_churn = "not" not in result["prediction"]
        card_class = "result-card-churn" if is_churn else "result-card-safe"
        icon = "🚨" if is_churn else "✅"
        
        st.markdown(f"""
            <div class="glass-card {card_class}" style="margin-top: 2rem;">
                <h2 style='text-align: center;'>Analysis Complete</h2>
                <p style='font-size: 2rem; text-align: center; margin: 1rem 0; font-weight: 600;'>{icon} {result['prediction']}</p>
            </div>
        """, unsafe_allow_html=True)

        recommendations = result.get("retention_recommendations", "No recommendations available.")
        if is_churn and isinstance(recommendations, list):
            st.markdown("<h3 class='recommendations-title brand-text'>💡 AI Retention Strategies</h3>", unsafe_allow_html=True)
            
            for i, rec in enumerate(recommendations):
                st.markdown(f"""
                <div class="recommendation-item" style="animation-delay: {0.3 + i*0.1}s">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M9.663 17H14.337M12 3V4M18.364 5.636L17.657 6.343M21 12H20M4 12H3M6.343 5.657L5.636 4.95M12 21C14.1211 20.9992 16.1553 20.1053 17.6549 18.5365C19.1545 16.9677 19.9972 14.8643 19.9972 12.6875C19.9972 10.5107 19.1545 8.40729 17.6549 6.83851C16.1553 5.26972 14.1211 4.37585 12 4.375C9.87885 4.37585 7.84474 5.26972 6.34513 6.83851C4.84553 8.40729 4.00281 10.5107 4.00281 12.6875C4.00281 14.8643 4.84553 16.9677 6.34513 18.5365C7.84474 20.1053 9.87885 20.9992 12 21Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                    <div class="markdown-content">{rec}</div>
                </div>
                """, unsafe_allow_html=True)
        
        elif not is_churn:
             st.success(f"✅ **Loyal Customer:** {recommendations}")

    elif "customers_likely_to_churn" in result:
        churner_count = result['no_of_customers_to_churn']
        card_class = "result-card-churn" if churner_count > 0 else "result-card-safe"
        st.markdown(f"""
            <div class="glass-card {card_class}" style="margin-top: 2rem;">
                <h2 style='text-align: center;'>Batch Analysis Complete</h2>
                <p style='font-size: 3rem; text-align: center; font-weight: bold;' class='brand-text'>{churner_count}</p>
                <p style='text-align: center; font-size: 1.2rem; margin-bottom: 1rem;'>Customers Predicted to Churn</p>
        """, unsafe_allow_html=True)
        if churner_count > 0:
            st.write("Customer IDs Flagged for Churn:")
            churn_df = pd.DataFrame(result['customers_likely_to_churn'], columns=["CustomerID"])
            st.dataframe(churn_df, use_container_width=True)
        else:
            st.success("No customers were identified as a high churn risk in this batch.")
        st.markdown("</div>", unsafe_allow_html=True)
else:
    st.markdown("""
        <div class="glass-card" style='text-align: center; padding: 4rem; margin-top: 2rem;'>
            <div style='font-size: 4rem;'>🛡️</div>
            <h2>Ready to Analyze</h2>
            <p style='color: #9ca3af;'>Your customer churn analysis will appear here. Fill in the details on the left to get started.</p>
        </div>
    """, unsafe_allow_html=True)


