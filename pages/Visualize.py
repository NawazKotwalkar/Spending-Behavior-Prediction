import streamlit as st
import pandas as pd
from utils.chart_utils import generate_chart, display_budget_vs_actual


def show():
    st.subheader("📊 Visualize Spending")

    # Always read canonical dataframe from session_state
    df = st.session_state.get("df")

    if df is None or df.empty:
        st.warning("⚠️ No transaction data available. Please upload a file first.")
        return

    # Defensive copy
    df = df.copy()

    # ---------------- NORMALIZE CORE COLUMNS ----------------
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])

    if df.empty:
        st.error("❌ No valid dates found in the data.")
        return

    # ✅ SINGLE SOURCE OF TRUTH FOR MONTH
    df["month"] = df["date"].dt.strftime("%Y-%m")

    # ✅ NORMALIZE CATEGORY EARLY (CRITICAL)
    df["category"] = (
        df["category"]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    # ---------------- FILTER OPTIONS ----------------
    available_months = sorted(
        df["month"].unique(),
        key=lambda x: pd.Period(x, freq="M")
    )

    available_categories = sorted(df["category"].unique())

    if not available_months:
        st.warning("⚠️ No valid months available.")
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

    # ---------------- FILTER DATA ----------------
    df_filtered = df[df["month"].isin(selected_months)]

    if selected_categories:
        df_filtered = df_filtered[df_filtered["category"].isin(selected_categories)]

    if df_filtered.empty:
        st.info("ℹ️ No data for selected filters.")
        return

    # ---------------- CHART SELECTION ----------------
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

    if chart is not None:
        st.altair_chart(chart, use_container_width=True)
    else:
        st.warning("⚠️ Unable to generate chart with current selection.")

    # ---------------- BUDGET VS ACTUAL ----------------
    st.markdown("---")
    st.subheader("📊 Budget vs Actual Spending")
    st.caption("All values shown as positive amounts")

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