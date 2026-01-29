import streamlit as st
from utils.auth_db import get_logged_in_user

def show():
    st.title("🏠 Home")
    st.markdown(f"Welcome, **{get_logged_in_user()}**! 👋")

    st.markdown("### 💼 About the Personal Finance Tracker")
    st.markdown("""
    This app helps you track, categorize, and visualize your expenses with smart analytics.  
    You can:
    - Upload your bank statements (CSV  ONLY)
    - Auto-categorize expenses
    - Visualize spending trends
    - Compare against your budget
    - Predict future expenses using machine learning
    - Export full visual reports as PDF  
    """)

    st.markdown("### 📁 Required File Formats")
    st.markdown("""
    #### 🏦 Transaction (Bank Statement) CSV
    Your transaction file must be parsable into the following fields:
    
    - `date` → Transaction date  
    - `amount` → Spent or received amount  
    - `description` → Transaction details  
    - `category` → Transaction category  
      *(If missing, it will be auto-filled as `uncategorized`)*  
    
    Column names **do not need to match exactly** — the app automatically detects common variants
    (e.g. `transaction_date`, `debit/credit`, `narration`, etc.).
    
    ---
    
    #### 📊 Budget CSV
    Your budget file must contain **exactly** these columns:
    
    - `category` → Expense category  
    - `budget` → Monthly budget amount for that category  
    
    
    ⚠️ **Important:**  
    Category names in the budget file must match transaction categories  
    (after trimming spaces and converting to lowercase).
    """)
