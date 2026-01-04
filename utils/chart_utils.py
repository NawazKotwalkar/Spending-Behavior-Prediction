import altair as alt
import numpy as np
import streamlit as st
import pandas as pd
from utils.budget_manager import get_all_budgets

def generate_chart(data, chart_type, selected_months, selected_categories):
    if chart_type == "Bar (Monthly Breakdown)":
        summary = data.groupby(['month', 'category'])['amount'].sum().reset_index()
        return alt.Chart(summary).mark_bar().encode(
            x='month:N', y='amount:Q', color='category:N',
            tooltip=['month', 'category', 'amount']
        ).properties(width=1000, height=500)

    elif chart_type == "Line (Daily Trend)":
        trend = data.groupby("date")["amount"].sum().reset_index()
        return alt.Chart(trend).mark_line().encode(
            x="date:T", y="amount:Q", tooltip=["date", "amount"]
        ).interactive()

    elif chart_type == "Pie (Selected Months)" and selected_months:
        month_df = data[data["month"].isin(selected_months)]
        selected_categories = month_df["category"].unique()

        if len(selected_categories) == 1:
            pie_data = month_df.groupby("month")["amount"].sum().reset_index()
            return alt.Chart(pie_data).mark_arc(innerRadius=50).encode(
                theta="amount:Q",
                color=alt.Color("month:N", legend=alt.Legend(title="Month")),
                tooltip=["month", "amount"]
            ).properties(width=1000, height=500)
        else:
            pie_data = month_df.groupby("category")["amount"].sum().reset_index()
            return alt.Chart(pie_data).mark_arc(innerRadius=50).encode(
                theta="amount:Q",
                color=alt.Color("category:N", legend=alt.Legend(title="Category")),
                tooltip=["category", "amount"]
            ).properties(width=1000, height=500)

    elif chart_type == "Bar (Total by Category)":
        summary = data.groupby("category")["amount"].sum().reset_index()
        return alt.Chart(summary).mark_bar().encode(
            x=alt.X("category:N", sort='-y'), y="amount:Q", tooltip=["category", "amount"]
        ).properties(width=1000, height=500)

    elif chart_type == "Multi-Month Category Comparison":
        summary = data.groupby(['month', 'category'])['amount'].sum().reset_index()
        return alt.Chart(summary).mark_bar().encode(
            x=alt.X("category:N", title="Category"),
            y=alt.Y("amount:Q", title="Amount Spent"),
            color="month:N",
            column=alt.Column("month:N", title=""),
            tooltip=["month", "category", "amount"]
        ).properties(width=1000, height=500)

    return None

def generate_budget_vs_actual_chart(df, selected_month, chart_type):
    budget_df = get_all_budgets()

    if budget_df is None or budget_df.empty:
        return None, None

    actual_df = (
        df[df["month"] == selected_month]
        .groupby("category")["amount"]
        .sum()
        .reset_index()
    )
    
    actual_df["category"] = actual_df["category"].astype(str).str.strip().str.lower()
    budget_df["category"] = budget_df["category"].astype(str).str.strip().str.lower()

    merged = pd.merge(actual_df, budget_df, on="category", how="inner")

    if merged.empty:
        return None, None

    merged["difference"] = merged["amount"] - merged["budget"]
    merged["overspent"] = np.where(
        merged["difference"] > 0, "Over Budget", "Within Budget"
    )

    melted = merged.melt(
        id_vars=["category", "difference", "overspent"],
        value_vars=["budget", "amount"],
        var_name="Type",
        value_name="Value"
    )

    if chart_type == "bar":
        chart = (
            alt.Chart(melted)
            .mark_bar(size=28)
            .encode(
                x=alt.X(
                    "category:N",
                    title="Category",
                    axis=alt.Axis(labelAngle=-20)
                ),
                xOffset=alt.XOffset("Type:N"),
                y=alt.Y(
                    "Value:Q",
                    title="Amount",
                    scale=alt.Scale(zero=True)
                ),
                color=alt.Color(
                    "Type:N",
                    scale=alt.Scale(
                        domain=["budget", "amount"],
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
                ]
            )
            .properties(
                height=420,
                title=f"Budget vs Actual – {selected_month}"
            )
        )
    else:
        return None, None

    return chart, merged

def display_budget_vs_actual(df, selected_month, chart_type="bar"):
    chart, merged = generate_budget_vs_actual_chart(df, selected_month, chart_type)

    if chart is None or merged is None:
        st.markdown(
            '<div class="custom-alert-warning">⚠️ No budget vs actual data available.</div>',
            unsafe_allow_html=True
        )
        return

    st.altair_chart(chart, use_container_width=True)

    overspent_categories = merged[merged["overspent"] == "Over Budget"]

    if not overspent_categories.empty:
        st.markdown("### ⚠️ Overspending Alert")
        for _, row in overspent_categories.iterrows():
            st.markdown(
                f"""
                <div class="custom-alert-warning">
                    ⚠️ You overspent in <b>{row['category']}</b> by ₹{abs(row['difference']):,.2f}<br>
                    Budget: ₹{row['budget']:,.2f} | Spent: ₹{row['amount']:,.2f}
                </div>
                """,
                unsafe_allow_html=True
            )

    with st.expander("📄 Show Budget vs Actual Data Table"):
        st.dataframe(
            merged[
                ["category", "budget", "amount", "difference", "overspent"]
            ].style.format({
                "budget": "₹{:.2f}",
                "amount": "₹{:.2f}",
                "difference": "₹{:.2f}"
            }),
            use_container_width=True
        )
