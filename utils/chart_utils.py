import altair as alt
import numpy as np
import streamlit as st
import pandas as pd
from utils.budget_manager import get_all_budgets


# ==========================================================
# GENERAL SPENDING CHARTS (USES `spend`)
# ==========================================================
def generate_chart(data, chart_type, selected_months, selected_categories):

    data = data.copy()

    if chart_type == "Bar (Monthly Breakdown)":
        summary = (
            data.groupby(["month", "category"], as_index=False)["spend"].sum()
        )

        return alt.Chart(summary).mark_bar().encode(
            x="month:N",
            y=alt.Y("spend:Q", title="Amount Spent"),
            color="category:N",
            tooltip=[
                "month",
                "category",
                alt.Tooltip("spend:Q", format=",.2f"),
            ],
        ).properties(height=420)

    elif chart_type == "Line (Daily Trend)":
        trend = (
            data.groupby("date", as_index=False)["spend"].sum()
        )

        return alt.Chart(trend).mark_line(point=True).encode(
            x="date:T",
            y=alt.Y("spend:Q", title="Daily Spend"),
            tooltip=[
                "date",
                alt.Tooltip("spend:Q", format=",.2f"),
            ],
        ).interactive()

    elif chart_type == "Pie (Selected Months)":
        pie_data = (
            data.groupby("category", as_index=False)["spend"].sum()
        )

        return alt.Chart(pie_data).mark_arc(innerRadius=50).encode(
            theta="spend:Q",
            color="category:N",
            tooltip=[
                "category",
                alt.Tooltip("spend:Q", format=",.2f"),
            ],
        ).properties(height=420)

    elif chart_type == "Bar (Total by Category)":
        summary = (
            data.groupby("category", as_index=False)["spend"].sum()
        )

        return alt.Chart(summary).mark_bar().encode(
            x=alt.X("category:N", sort="-y"),
            y=alt.Y("spend:Q", title="Total Spend"),
            tooltip=[
                "category",
                alt.Tooltip("spend:Q", format=",.2f"),
            ],
        ).properties(height=420)

    elif chart_type == "Multi-Month Category Comparison":
        summary = (
            data.groupby(["month", "category"], as_index=False)["spend"].sum()
        )

        return alt.Chart(summary).mark_bar().encode(
            x="category:N",
            y="spend:Q",
            color="month:N",
            column="month:N",
            tooltip=[
                "month",
                "category",
                alt.Tooltip("spend:Q", format=",.2f"),
            ],
        ).properties(height=420)

    return None


# ==========================================================
# BUDGET VS ACTUAL (USES `budget` vs `actual`)
# ==========================================================
def generate_budget_vs_actual_chart(df, selected_month, chart_type):

    budget_df = get_all_budgets()

    if budget_df is None or budget_df.empty:
        return None, None

    # ---------- ACTUAL SPEND ----------
    actual_df = (
        df[df["month"] == selected_month]
        .groupby("category", as_index=False)["spend"]
        .sum()
        .rename(columns={"spend": "actual"})
    )

    # Normalize
    actual_df["category"] = actual_df["category"].str.strip().str.lower()
    budget_df["category"] = budget_df["category"].str.strip().str.lower()

    merged = pd.merge(budget_df, actual_df, on="category", how="inner")

    if merged.empty:
        return None, None

    merged["difference"] = merged["actual"] - merged["budget"]
    merged["overspent"] = np.where(
        merged["difference"] > 0, "Over Budget", "Within Budget"
    )

    # ---------- LONG FORMAT FOR ALTAIR ----------
    melted = merged.melt(
        id_vars=["category", "difference", "overspent"],
        value_vars=["budget", "actual"],
        var_name="Type",
        value_name="Value",
    )

    if chart_type == "bar":
        chart = (
            alt.Chart(melted)
            .mark_bar(size=28)
            .encode(
                x=alt.X(
                    "category:N",
                    title="Category",
                    axis=alt.Axis(labelAngle=-20),
                ),
                xOffset="Type:N",
                y=alt.Y(
                    "Value:Q",
                    title="Amount",
                    scale=alt.Scale(zero=True),
                ),
                color=alt.Color(
                    "Type:N",
                    scale=alt.Scale(
                        domain=["budget", "actual"],
                        range=["#64748b", "#22c55e"],
                    ),
                    legend=alt.Legend(title="Type"),
                ),
                tooltip=[
                    "category",
                    "Type",
                    alt.Tooltip("Value:Q", format=",.2f"),
                    alt.Tooltip("difference:Q", format=",.2f"),
                    "overspent",
                ],
            )
            .properties(
                height=420,
                title=f"Budget vs Actual – {selected_month}",
            )
        )
    else:
        return None, None

    return chart, merged


# ==========================================================
# DISPLAY HELPER
# ==========================================================
def display_budget_vs_actual(df, selected_month, chart_type="bar"):

    chart, merged = generate_budget_vs_actual_chart(df, selected_month, chart_type)

    if chart is None or merged is None:
        st.markdown(
            '<div class="custom-alert-warning">⚠️ No budget vs actual data available.</div>',
            unsafe_allow_html=True,
        )
        return

    st.altair_chart(chart, use_container_width=True)

    overspent = merged[merged["overspent"] == "Over Budget"]

    if not overspent.empty:
        st.markdown("### ⚠️ Overspending Alert")
        for _, row in overspent.iterrows():
            st.markdown(
                f"""
                <div class="custom-alert-warning">
                    ⚠️ You overspent in <b>{row['category']}</b> by ₹{row['difference']:,.2f}<br>
                    Budget: ₹{row['budget']:,.2f} | Spent: ₹{row['actual']:,.2f}
                </div>
                """,
                unsafe_allow_html=True,
            )

    with st.expander("📄 Show Budget vs Actual Data Table"):
        st.dataframe(
            merged[
                ["category", "budget", "actual", "difference", "overspent"]
            ].style.format({
                "budget": "₹{:.2f}",
                "actual": "₹{:.2f}",
                "difference": "₹{:.2f}",
            }),
            use_container_width=True,
        )
