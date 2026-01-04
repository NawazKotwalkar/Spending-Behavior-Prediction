import os
import pandas as pd
import streamlit as st

BUDGET_FILE = "data/budgets.csv"


def save_budget(category, amount):
    """Save fixed budget for a category (ignores month)."""
    os.makedirs("data", exist_ok=True)
    df = load_budgets()

    # Remove existing entry for category
    df = df[df["category"] != category]

    # Add new one
    new_row = pd.DataFrame([{"category": category, "budget": amount}])
    df = pd.concat([df, new_row], ignore_index=True)

    df.to_csv(BUDGET_FILE, index=False)


def load_budgets():
    """Load fixed category budgets from local file."""
    if os.path.exists(BUDGET_FILE):
        return pd.read_csv(BUDGET_FILE)
    return pd.DataFrame(columns=["category", "budget"])


def get_budget(category):
    """Get fixed budget amount for a given category."""
    df = load_budgets()
    row = df[df["category"] == category]
    if not row.empty:
        return row.iloc[0]["budget"]
    return None



def get_all_budgets():
    """
    Return budgets from session_state.
    This is REQUIRED for Streamlit Cloud.
    """
    return st.session_state.get("budget_df")
