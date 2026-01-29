import streamlit as st
import pandas as pd
import altair as alt

from utils.chart_utils import display_budget_vs_actual

CHART_HEIGHT = 420


def show():
    st.title("📊 Visualize Spending")

    # ==================== REQUIRE UPLOADED DATA ====================
    if "df" not in st.session_state:
        st.markdown(
            "<div class='custom-alert-warning'>📤 Upload a transaction file to view visualizations.</div>",
            unsafe_allow_html=True
        )
        st.stop()

    df = st.session_state["df"].copy()

    if df.empty:
        st.markdown(
            "<div class='custom-alert-warning'>⚠️ No transactions found in uploaded file.</div>",
            unsafe_allow_html=True
        )
        st.stop()

    # ==================== PREP DATA ====================
    df["date"] = pd.to_datetime(df["date"])
    df["month"] = df["date"].dt.to_period("M").astype(str)

    df["category"] = (
        df["category"]
        .astype(str)
        .str.lower()
        .str.strip()
    )

    # ==================== FILTERS ====================
    st.markdown("### Filters")

    categories = sorted(df["category"].unique())
    selected_categories = st.multiselect(
        "Select Category(s)",
        categories,
        default=categories
    )

    months = sorted(
        df[df["category"].isin(selected_categories)]["month"].unique()
    )

    if not months:
        st.markdown(
            "<div class='custom-alert-warning'>⚠️ No months available for selected categories.</div>",
            unsafe_allow_html=True
        )
        st.stop()

    selected_months = st.multiselect(
        "Select Month(s)",
        months,
        default=months[-1:]
    )

    df_filtered = df[
        df["category"].isin(selected_categories)
        & df["month"].isin(selected_months)
    ]

    if df_filtered.empty:
        st.markdown(
            "<div class='custom-alert-warning'>⚠️ No data for selected filters.</div>",
            unsafe_allow_html=True
        )
        st.stop()

    # ==================== CHART SELECTION (ALL EXCEPT BUDGET) ====================
    st.markdown("### 📈 Spending Charts")

    chart_option = st.selectbox(
        "Select chart",
        [
            "Bar – Spending by Category",
            "Pie – Spending Distribution",
            "Line – Monthly Trend",
            "Stacked Bar – Category Contribution",
        ],
    )

    # ==================== SELECTED CHART ====================

    if chart_option == "Bar – Spending by Category":
        data = df_filtered.groupby("category", as_index=False)["amount"].sum()

        chart = (
            alt.Chart(data)
            .mark_bar()
            .encode(
                x=alt.X("category:N", sort="-y"),
                y=alt.Y("amount:Q", title="Amount"),
                tooltip=["category", alt.Tooltip("amount:Q", format=",.2f")],
            )
            .properties(height=CHART_HEIGHT)
        )

        st.altair_chart(chart, use_container_width=True)

    elif chart_option == "Pie – Spending Distribution":
        if len(selected_categories) == 1 and len(selected_months) > 1:
            data = df_filtered.groupby("month", as_index=False)["amount"].sum()
            color_field = "month:N"
            title = "Distribution by Month"
        else:
            data = df_filtered.groupby("category", as_index=False)["amount"].sum()
            color_field = "category:N"
            title = "Distribution by Category"

        chart = (
            alt.Chart(data)
            .mark_arc()
            .encode(
                theta="amount:Q",
                color=color_field,
                tooltip=[color_field.split(":")[0], alt.Tooltip("amount:Q", format=",.2f")],
            )
            .properties(height=CHART_HEIGHT, title=title)
        )

        st.altair_chart(chart, use_container_width=True)

    elif chart_option == "Line – Monthly Trend":
        data = (
            df_filtered.groupby("month", as_index=False)["amount"]
            .sum()
            .sort_values("month")
        )

        chart = (
            alt.Chart(data)
            .mark_line(point=True)
            .encode(
                x=alt.X("month:N", title="Month"),
                y=alt.Y("amount:Q", title="Total Spending"),
                tooltip=["month", alt.Tooltip("amount:Q", format=",.2f")],
            )
            .properties(height=CHART_HEIGHT)
        )

        st.altair_chart(chart, use_container_width=True)

    elif chart_option == "Stacked Bar – Category Contribution":
        data = (
            df_filtered.groupby(["month", "category"], as_index=False)["amount"].sum()
        )

        chart = (
            alt.Chart(data)
            .mark_bar()
            .encode(
                x="month:N",
                y=alt.Y("amount:Q", stack="zero"),
                color="category:N",
                tooltip=[
                    "month",
                    "category",
                    alt.Tooltip("amount:Q", format=",.2f"),
                ],
            )
            .properties(height=CHART_HEIGHT)
        )

        st.altair_chart(chart, use_container_width=True)

    # ==================== BUDGET VS ACTUAL (ALWAYS SHOWN) ====================
    st.markdown("---")
    st.markdown("### 💰 Budget vs Actual")

    budget_month = st.selectbox(
        "Select Month for Budget Comparison",
        selected_months,
        index=len(selected_months) - 1,
        key="budget_month_selector",
    )

    display_budget_vs_actual(
        df=df_filtered,
        selected_month=budget_month,
        chart_type="bar",
        show_overspend_alert=True,
    )
