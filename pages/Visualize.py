import streamlit as st
import pandas as pd
from utils.chart_utils import generate_chart, display_budget_vs_actual

def show():
    st.subheader("📊 Visualize Spending")

    df = st.session_state.get("transactions_df")

    if df is None or df.empty:
        st.markdown(
            """<div class="custom-alert-warning">
            ⚠️ Upload a transaction file first to view analytics.
            </div>""",
            unsafe_allow_html=True
        )
        return

    # ---------- SAFETY ----------
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])

    df["month"] = df["date"].dt.to_period("M").astype(str)

    # ---------- FILTERS ----------
    with st.container():
        col1, col2 = st.columns(2)

        with col1:
            months = sorted(df["month"].unique())
            selected_months = st.multiselect(
                "Month(s)",
                months,
                default=months[-1:]
            )

        with col2:
            categories = sorted(df["category"].unique())
            selected_categories = st.multiselect(
                "Categories",
                categories,
                default=categories
            )

    df_filtered = df[df["month"].isin(selected_months)]
    if selected_categories:
        df_filtered = df_filtered[df_filtered["category"].isin(selected_categories)]

    # ---------- CHART ----------
    chart_type = st.selectbox(
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
        chart_type,
        selected_months,
        selected_categories
    )

    if chart:
        st.altair_chart(chart, use_container_width=True)

    # ---------- BUDGET ----------
    st.markdown("---")
    st.subheader("📊 Budget vs Actual")

    budget_month = st.selectbox(
        "Select Month",
        sorted(df["month"].unique()),
        index=len(df["month"].unique()) - 1
    )

    display_budget_vs_actual(
        df=df,
        selected_month=budget_month,
        chart_type="bar"
    )
