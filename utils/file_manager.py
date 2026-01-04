import os
import streamlit as st

def save_uploaded_file(uploaded_file, file_type):
    """
    Save uploaded file to `data/transactions/` or `data/budgets/` folder.
    Returns full file path and stores it in `st.session_state`.
    """
    if file_type == "transaction":
        folder = "data/transactions"
        state_key = "transaction_file"
    elif file_type == "budget":
        folder = "data/budgets"
        state_key = "budget_file"
    else:
        raise ValueError("Invalid file_type. Use 'transaction' or 'budget'.")

    os.makedirs(folder, exist_ok=True)
    file_path = os.path.join(folder, uploaded_file.name)

    # Save file
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Update session state
    st.session_state[state_key] = file_path
    return file_path
