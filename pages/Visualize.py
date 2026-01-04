import streamlit as st
import pandas as pd
import os
from utils.chart_utils import generate_chart, display_budget_vs_actual

def show():
    st.subheader("📊 Visualize Spending")
    df = st.session_state.get("transactions_df")

    if df is None or df.empty:
        st.warning("⚠️ No transaction data available.")
        return

    # 🔒 HARD FIX (the important part)
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])

    if df.empty:
        st.warning("⚠️ No valid dates found after parsing.")
        return

    # ✅ SAFE to use .dt now
    df["month"] = df["date"].dt.to_period("M").astype(str)

    available_months = sorted(df["month"].unique())
    available_categories = sorted(df["category"].unique())

    selected_months = st.multiselect(
        "Select Month(s)",
        available_months,
        default=available_months[-1:]
    )
    selected_categories = st.multiselect(
        "Select Categories",
        available_categories,
        default=available_categories
    )

    df_filtered = df[df["month"].isin(selected_months)]
    if selected_categories:
        df_filtered = df_filtered[df_filtered["category"].isin(selected_categories)]

    chart_option = st.selectbox(
        "Chart Type",
        [
            "Bar (Monthly Breakdown)",
            "Line (Daily Trend)",
            "Pie (Selected Months)",
            "Bar (Total by Category)",
            "Multi-Month Category Comparison"
        ]
    )

    chart = generate_chart(
        df_filtered,
        chart_option,
        selected_months,
        selected_categories
    )

    if chart:
        st.altair_chart(chart, use_container_width=True)

    st.markdown("---")
    st.subheader("📊 Budget vs Actual Spending")

    if df_filtered.empty:
        st.info("No data available for the selected filters.")
        return

    budget_month = st.selectbox(
        "Select Month for Budget Comparison",
        available_months,
        index=len(available_months) - 1
    )

    display_budget_vs_actual(
        df=df,
        selected_month=budget_month,
        chart_type="bar"
    )