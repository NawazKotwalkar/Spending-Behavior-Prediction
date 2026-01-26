import streamlit as st
import pandas as pd
import altair as alt

from utils.chart_utils import generate_budget_vs_actual_chart
CHART_HEIGHT = 420
def show():
    st.title("📊 Visualize Spending")
    # ==================== REQUIRE UPLOADED DATA ====================
    if "df" not in st.session_state:
        st.info("Upload a transaction file to view visualizations.")
        st.stop()
    df = st.session_state["df"].copy()
    if df.empty:
        st.info("No transactions found in uploaded file.")
        st.stop()
    # ==================== PREP DATA ====================
    df["date"] = pd.to_datetime(df["date"])
    df["month"] = df["date"].dt.to_period("M").astype(str)
    # Normalize categories (CRITICAL)
    df["category"] = (
        df["category"]
        .astype(str)
        .str.lower()
        .str.strip()
    )
    # ==================== FILTERS ====================
    st.markdown("### 🔎 Filters")
    # Categories ONLY from dataset
    categories = sorted(df["category"].unique())
    selected_categories = st.multiselect(
        "Select Category(s)",
        categories,
        default=categories
    )
    # Months ONLY from selected categories
    months = sorted(
        df[df["category"].isin(selected_categories)]["month"].unique()
    )
    if not months:
        st.warning("No months available for selected categories.")
        st.stop()
    selected_months = st.multiselect(
        "Select Month(s)",
        months,
        default=months[-1:]
    )
    # Final filtered dataset
    df_filtered = df[
        df["category"].isin(selected_categories)
        & df["month"].isin(selected_months)
    ]
    if df_filtered.empty:
        st.warning("No data for selected filters.")
        st.stop()
    # ==================== BAR CHART ====================
    st.markdown("### 📊 Spending by Category")
    bar_data = df_filtered.groupby("category", as_index=False)["amount"].sum()
    bar_chart = alt.Chart(bar_data).mark_bar().encode(
        x=alt.X("category:N", sort="-y"),
        y=alt.Y("amount:Q", title="Amount"),
        tooltip=["category", "amount"]
    ).properties(height=CHART_HEIGHT)
    st.altair_chart(bar_chart, use_container_width=True)
    # ==================== PIE CHART ====================
    st.markdown("### 🥧 Spending Distribution")
    if len(selected_categories) == 1 and len(selected_months) > 1:
        pie_data = df_filtered.groupby("month", as_index=False)["amount"].sum()
        color_field = "month:N"
        title = "Distribution by Month"
    else:
        pie_data = df_filtered.groupby("category", as_index=False)["amount"].sum()
        color_field = "category:N"
        title = "Distribution by Category"
    pie_chart = alt.Chart(pie_data).mark_arc().encode(
        theta="amount:Q",
        color=color_field,
        tooltip=[color_field.split(":")[0], "amount"]
    ).properties(height=CHART_HEIGHT, title=title)
    st.altair_chart(pie_chart, use_container_width=True)
    # ==================== LINE CHART ====================
    st.markdown("### 📈 Monthly Spending Trend")

    line_data = (
        df_filtered
        .groupby("month", as_index=False)["amount"]
        .sum()
        .sort_values("month")
    )
    line_chart = alt.Chart(line_data).mark_line(point=True).encode(
        x=alt.X("month:N", title="Month"),
        y=alt.Y("amount:Q", title="Total Spending"),
        tooltip=["month", "amount"]
    ).properties(height=CHART_HEIGHT)
    st.altair_chart(line_chart, use_container_width=True)
    # ==================== STACKED BAR ====================
    st.markdown("### 🧱 Category Contribution per Month")
    stacked_data = (
        df_filtered
        .groupby(["month", "category"], as_index=False)["amount"]
        .sum()
    )
    stacked_chart = alt.Chart(stacked_data).mark_bar().encode(
        x=alt.X("month:N", title="Month"),
        y=alt.Y("amount:Q", stack="zero", title="Amount"),
        color=alt.Color("category:N", legend=alt.Legend(title="Category")),
        tooltip=["month", "category", "amount"]
    ).properties(height=CHART_HEIGHT)
    st.altair_chart(stacked_chart, use_container_width=True)
    # ==================== BUDGET VS ACTUAL ====================
    st.markdown("### 💰 Budget vs Actual")
    budget_month = st.selectbox(
        "Select Month for Budget Comparison",
        selected_months,
        index=len(selected_months) - 1,
    )
    chart, merged = generate_budget_vs_actual_chart(
        df=df_filtered,
        selected_month=budget_month,
        chart_type="bar",
    )

    if chart is not None:
        st.altair_chart(chart, use_container_width=True)
        with st.expander("📋 Show Budget vs Actual Data"):
            st.dataframe(
                merged.sort_values("difference", ascending=False),
                use_container_width=True,
            )
    # ==================== TRANSACTION TABLE ====================
    st.markdown("### 📋 Transactions Table")
    st.dataframe(
        df_filtered.sort_values("date", ascending=False),
        use_container_width=True,
    )