import altair as alt
import numpy as np
import streamlit as st
import pandas as pd
from utils.budget_manager import get_all_budgets

def generate_chart(data, chart_type, selected_months, selected_categories):
    data = data.copy()

    if chart_type == "Bar (Monthly Breakdown)":
        summary = data.groupby(["month", "category"], as_index=False)["amount"].sum()
        return (
            alt.Chart(summary)
            .mark_bar()
            .encode(
                x="month:N",
                y="amount:Q",
                color="category:N",
                tooltip=["month", "category", alt.Tooltip("amount:Q", format=",.2f")],
            )
            .properties(height=420)
        )

    if chart_type == "Line (Daily Trend)":
        trend = data.groupby("date", as_index=False)["amount"].sum()
        return (
            alt.Chart(trend)
            .mark_line(point=True)
            .encode(
                x="date:T",
                y="amount:Q",
                tooltip=["date", alt.Tooltip("amount:Q", format=",.2f")],
            )
            .interactive()
            .properties(height=420)
        )

    if chart_type == "Pie (Selected Months)":
        pie = data.groupby("category", as_index=False)["amount"].sum()
        return (
            alt.Chart(pie)
            .mark_arc(innerRadius=50)
            .encode(
                theta="amount:Q",
                color="category:N",
                tooltip=["category", alt.Tooltip("amount:Q", format=",.2f")],
            )
            .properties(height=420)
        )

    if chart_type == "Bar (Total by Category)":
        summary = data.groupby("category", as_index=False)["amount"].sum()
        return (
            alt.Chart(summary)
            .mark_bar()
            .encode(
                x=alt.X("category:N", sort="-y"),
                y="amount:Q",
                tooltip=["category", alt.Tooltip("amount:Q", format=",.2f")],
            )
            .properties(height=420)
        )

    if chart_type == "Multi-Month Category Comparison":
        summary = data.groupby(["month", "category"], as_index=False)["amount"].sum()
        return (
            alt.Chart(summary)
            .mark_bar()
            .encode(
                x="category:N",
                y="amount:Q",
                color="month:N",
                column="month:N",
                tooltip=["month", "category", alt.Tooltip("amount:Q", format=",.2f")],
            )
            .properties(height=420)
        )

    return None

def generate_budget_vs_actual_chart(df, selected_month, chart_type):
    budget_df = get_all_budgets()

    if budget_df is None or budget_df.empty:
        return None, None

    budget_df = budget_df.copy()


    # 🔑 NORMALIZE BUDGET COLUMN NAME
    if "budget_amount" in budget_df.columns:
        budget_df = budget_df.rename(columns={"budget_amount": "budget"})


# Use a case-insensitive check to ensure the month matches
    actual_df = (
        df[df["month"] == selected_month]
        .groupby("category", as_index=False)["amount"]
        .sum()
        .rename(columns={"amount": "actual"})
    )

    # Inside generate_budget_vs_actual_chart
    budget_df["category"] = budget_df["category"].astype(str).str.lower().str.strip()
    actual_df["category"] = actual_df["category"].astype(str).str.lower().str.strip()
    merged = pd.merge(budget_df, actual_df, on="category", how="left")
    merged["actual"] = merged["actual"].fillna(0)
    if actual_df.empty:
        st.warning(f"No transactions recorded for {selected_month}.")
    elif merged["actual"].sum() == 0:
        st.warning(
            f"Transactions exist in {selected_month}, "
            "but none match the budgeted categories."
        )
    if merged.empty:
        return None, None

    merged["difference"] = merged["actual"] - merged["budget"]
    merged["overspent"] = np.where(merged["difference"] > 0, "Over Budget", "OK")

    melted = merged.melt(
        id_vars=["category", "difference", "overspent"],
        value_vars=["budget", "actual"],
        var_name="Type",
        value_name="Value"
    )

    chart = (
            alt.Chart(melted)
            .mark_bar(size=28)
            .encode(
                x=alt.X("category:N", axis=alt.Axis(labelAngle=-20)),
                xOffset="Type:N",
                y=alt.Y("Value:Q", title="Amount", scale=alt.Scale(zero=True)),
                color=alt.Color(
                    "Type:N",
                    scale=alt.Scale(
                        domain=["budget", "actual"],
                        range=["#64748b", "#22c55e"]
                    ),
                    legend=alt.Legend(title="Type")
                ),
                tooltip=[
                    "category",
                    "Type",
                    alt.Tooltip("Value:Q", format=",.2f"),
                    alt.Tooltip("difference:Q", format=",.2f"),
                    "overspent"
                ],
            )
            .properties(height=420)
        )
    return chart, merged


def display_budget_vs_actual(df, selected_month, chart_type="bar"):
    chart, merged = generate_budget_vs_actual_chart(df, selected_month, chart_type)

    if chart is None:
        st.warning("No budget vs actual data")
        return

    st.altair_chart(chart, use_container_width=True)

    with st.expander("Show data"):
        st.dataframe(merged)
