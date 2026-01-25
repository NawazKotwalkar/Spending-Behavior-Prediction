import altair as alt
import numpy as np
import streamlit as st
import pandas as pd
from utils.budget_manager import get_all_budgets


def generate_chart(data, chart_type, selected_months, selected_categories):
    data = data.copy()

    if chart_type == "Bar (Monthly Breakdown)":
        summary = data.groupby(["month", "category"], as_index=False)["amount"].sum()
        return alt.Chart(summary).mark_bar().encode(
            x="month:N",
            y="amount:Q",
            color="category:N",
            tooltip=["month", "category", alt.Tooltip("amount:Q", format=",.2f")]
        )

    if chart_type == "Line (Daily Trend)":
        trend = data.groupby("date", as_index=False)["amount"].sum()
        return alt.Chart(trend).mark_line(point=True).encode(
            x="date:T",
            y="amount:Q",
            tooltip=["date", alt.Tooltip("amount:Q", format=",.2f")]
        ).interactive()

    if chart_type == "Pie (Selected Months)":
        pie = data.groupby("category", as_index=False)["amount"].sum()
        return alt.Chart(pie).mark_arc(innerRadius=50).encode(
            theta="amount:Q",
            color="category:N",
            tooltip=["category", alt.Tooltip("amount:Q", format=",.2f")]
        )

    if chart_type == "Bar (Total by Category)":
        summary = data.groupby("category", as_index=False)["amount"].sum()
        return alt.Chart(summary).mark_bar().encode(
            x=alt.X("category:N", sort="-y"),
            y="amount:Q",
            tooltip=["category", alt.Tooltip("amount:Q", format=",.2f")]
        )

    if chart_type == "Multi-Month Category Comparison":
        summary = data.groupby(["month", "category"], as_index=False)["amount"].sum()
        return alt.Chart(summary).mark_bar().encode(
            x="category:N",
            y="amount:Q",
            color="month:N",
            column="month:N",
            tooltip=["month", "category", alt.Tooltip("amount:Q", format=",.2f")]
        )

    return None


def generate_budget_vs_actual_chart(df, selected_month, chart_type):
    budget_df = get_all_budgets()
    if budget_df is None or budget_df.empty:
        return None, None

    actual_df = (
        df[df["month"] == selected_month]
        .groupby("category", as_index=False)["amount"]
        .sum()
        .rename(columns={"amount": "actual"})
    )

    budget_df["category"] = budget_df["category"].str.lower().str.strip()
    actual_df["category"] = actual_df["category"].str.lower().str.strip()

    merged = pd.merge(budget_df, actual_df, on="category", how="inner")
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

    chart = alt.Chart(melted).mark_bar(size=28).encode(
        x=alt.X("category:N", axis=alt.Axis(labelAngle=-20)),
        xOffset="Type:N",
        y="Value:Q",
        color="Type:N",
        tooltip=[
            "category",
            "Type",
            alt.Tooltip("Value:Q", format=",.2f"),
            alt.Tooltip("difference:Q", format=",.2f"),
            "overspent"
        ]
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