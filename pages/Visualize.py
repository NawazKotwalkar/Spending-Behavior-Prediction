import streamlit as st
import pandas as pd
from utils.chart_utils import generate_chart, display_budget_vs_actual


def show():
    st.subheader("📊 Visualize Spending")

    # ✅ SINGLE SOURCE OF TRUTH
    df = st.session_state.get("df")

    if df is None or df.empty:
        st.warning("⚠️ No transaction data available. Please upload a file first.")
        return

    # ✅ SAFETY: ensure datetime (cloud-safe)
    if not pd.api.types.is_datetime64_any_dtype(df["date"]):
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df = df.dropna(subset=["date"])

    # ✅ Month column (guaranteed safe)
    df["month"] = df["date"].dt.to_period("M").astype(str)

    # ---------- FILTER OPTIONS ----------
    available_months = sorted(
        df["month"].unique(),
        key=lambda x: pd.Period(x, freq="M")
    )

    available_categories = sorted(
        df["category"]
        .dropna()
        .astype(str)
        .str.strip()
        .str.lower()
        .unique()
    )

    if not available_months:
        st.warning("⚠️ No valid month data found.")
        return

    selected_months = st.multiselect(
        "Select Month(s)",
        available_months,
        default=[available_months[-1]],
    )

    selected_categories = st.multiselect(
        "Select Categories",
        available_categories,
        default=available_categories,
    )

    # ---------- FILTER DATA ----------
    df_filtered = df[df["month"].isin(selected_months)]

    if selected_categories:
        df_filtered = df_filtered[df_filtered["category"].isin(selected_categories)]

    if df_filtered.empty:
        st.info("ℹ️ No data for selected filters.")
        return

    # ---------- CHART ----------
    chart_option = st.selectbox(
        "Chart Type",
        [
            "Bar (Monthly Breakdown)",
            "Line (Daily Trend)",
            "Pie (Selected Months)",
            "Bar (Total by Category)",
            "Multi-Month Category Comparison",
        ],
    )

    chart = generate_chart(
        df_filtered,
        chart_option,
        selected_months,
        selected_categories,
    )

    if chart:
        st.altair_chart(chart, use_container_width=True)

    # ---------- BUDGET VS ACTUAL ----------
    st.markdown("---")
    st.subheader("📊 Budget vs Actual Spending")
    st.caption("Budget = positive | Actual spend = negative (outflow)")

    budget_month = st.selectbox(
        "Select Month for Budget Comparison",
        available_months,
        index=len(available_months) - 1,
    )

    display_budget_vs_actual(
        df=df,
        selected_month=budget_month,
        chart_type="bar",
    )