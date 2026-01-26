import os
import tempfile
import streamlit as st
import pandas as pd
from vl_convert import vegalite_to_png

from utils.chart_utils import generate_chart, generate_budget_vs_actual_chart
from reports.report_generator import generate_pdf_report
from utils.budget_manager import get_all_budgets


def show():
    st.subheader("📥 Export Report")

    # -------------------- LOAD DATA --------------------
    if "df" not in st.session_state:
        st.warning("Please upload a transaction file first.")
        return

    df = st.session_state["df"].copy()

    # -------------------- ENSURE MONTH COLUMN --------------------
    if "month" not in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df = df.dropna(subset=["date"])
        df["month"] = df["date"].dt.to_period("M").astype(str)

    # -------------------- METRICS FROM PREDICT --------------------
    mae = st.session_state.get("mae")
    rmse = st.session_state.get("rmse")

    # -------------------- DEFAULT SELECTIONS --------------------
    available_months = sorted(df["month"].unique())

    selected_months = (
        available_months[-3:]
        if len(available_months) >= 3
        else available_months
    )

    selected_categories = sorted(df["category"].unique())

    df_filtered = df[
        df["month"].isin(selected_months)
        & df["category"].isin(selected_categories)
    ]

    selected_chart_type = "bar"

    report_ui(
        df=df,
        selected_months=selected_months,
        selected_categories=selected_categories,
        df_filtered=df_filtered,
        selected_chart_type=selected_chart_type,
        mae=mae,
        rmse=rmse,
    )


def report_ui(
    df,
    selected_months,
    selected_categories,
    df_filtered,
    selected_chart_type,
    mae,
    rmse,
):
    if st.button("📄 Download PDF Report"):
        with tempfile.TemporaryDirectory() as tmpdir:
            chart_paths = []

            # -------------------- MAIN CHARTS --------------------
            for ct in [
                "Bar (Monthly Breakdown)",
                "Pie (Selected Months)",
                "Line (Daily Trend)",
            ]:
                try:
                    chart = generate_chart(
                        df_filtered, ct, selected_months, selected_categories
                    )
                    if chart:
                        img_bytes = vegalite_to_png(chart.to_dict(), scale=3)
                        path = os.path.join(
                            tmpdir,
                            f"{ct.replace(' ', '_').replace('(', '').replace(')', '')}.png",
                        )
                        with open(path, "wb") as f:
                            f.write(img_bytes)
                        chart_paths.append(path)
                except Exception as e:
                    st.warning(f"Could not render {ct}: {e}")

            # -------------------- BUDGET vs ACTUAL --------------------
            try:
                chart, _ = generate_budget_vs_actual_chart(
                    df, selected_months[-1], selected_chart_type
                )
                if chart:
                    path = os.path.join(tmpdir, "budget_vs_actual.png")
                    with open(path, "wb") as f:
                        f.write(vegalite_to_png(chart.to_dict(), scale=3))
                    chart_paths.append(path)
            except Exception as e:
                st.warning(f"Budget vs Actual chart error: {e}")

            # -------------------- GENERATE PDF --------------------
            report_path = generate_pdf_report(
                df=df,
                selected_month=selected_months[-1],
                chart_paths=chart_paths,
                budget_df=get_all_budgets(),
                mae=mae,
                rmse=rmse,
            )

            with open(report_path, "rb") as f:
                st.download_button(
                    "⬇️ Download Full Visual Report",
                    data=f,
                    file_name="finance_report.pdf",
                    mime="application/pdf",
                )


def show2():
    st.markdown("---")
    st.link_button(
        "📝 Give Feedback",
        "https://forms.gle/UNMYmAzc3kULbHQq8",
    )
    st.caption("Takes less than a minute")
