import streamlit as st
import pandas as pd
from utils.chart_utils import generate_chart, display_budget_vs_actual


def show():
    st.subheader("📊 Visualize Spending")

    # -------------------- LOAD DATA --------------------
    df = st.session_state.get("transactions_df")

    if df is None or df.empty:
        st.warning("⚠️ No transaction data available. Please upload a file first.")
        return

    # -------------------- HARD SAFETY FIX --------------------
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])

    if df.empty:
        st.warning("⚠️ No valid dates found in transaction data.")
        return

    df["month"] = df["date"].dt.to_period("M").astype(str)

    # -------------------- FILTER OPTIONS --------------------
    available_months = sorted(df["month"].unique())
    available_categories = sorted(df["category"].unique())

    # -------------------- FILTER UI (CLEAN) --------------------
    with st.container():
        col1, col2, col3 = st.columns([1.2, 1.2, 1])

        with col1:
            selected_months = st.multiselect(
                "📅 Select Month(s)",
                available_months,
                default=available_months[-1:]
            )

        with col2:
            selected_categories = st.multiselect(
                "🏷 Select Categories",
                available_categories,
                default=available_categories
            )

        with col3:
            chart_option = st.selectbox(
                "📊 Chart Type",
                [
                    "Bar (Monthly Breakdown)",
                    "Line (Daily Trend)",
                    "Pie (Selected Months)",
                    "Bar (Total by Category)",
                    "Multi-Month Category Comparison"
                ]
            )

    # -------------------- FILTER DATA --------------------
    df_filtered = df[df["month"].isin(selected_months)]

    if selected_categories:
        df_filtered = df_filtered[df_filtered["category"].isin(selected_categories)]

    if df_filtered.empty:
        st.info("No data available for selected filters.")
        return

    # -------------------- MAIN CHART --------------------
    st.markdown("### 📈 Spending Overview")

    chart = generate_chart(
        df_filtered,
        chart_option,
        selected_months,
        selected_categories
    )

    if chart:
        st.altair_chart(chart, use_container_width=True)

    # -------------------- BUDGET VS ACTUAL (COLLAPSED) --------------------
    st.markdown("---")

    with st.expander("📊 Budget vs Actual Comparison", expanded=False):
        budget_month = st.selectbox(
            "Select Month",
            available_months,
            index=len(available_months) - 1
        )

        display_budget_vs_actual(
            df=df,
            selected_month=budget_month,
            chart_type="bar"
        )
