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

    # ✅ Ensure transaction file is loaded
    transaction_file = st.session_state.get("transaction_file")
    if not transaction_file or not os.path.exists(transaction_file):
        st.markdown(f""" <div class="custom-alert-warning">"⚠️ Please upload a transaction file first.</div>""", unsafe_allow_html=True)
        return

    try:
        df = pd.read_csv(transaction_file, parse_dates=["date"])
        df["month"] = df["date"].dt.to_period("M").astype(str)
    except Exception as e:
        st.error(f"❌ Failed to load transaction file: {e}")
        return

    # Dummy fallback values if not in session_state (you can update this logic as needed)
    mae = st.session_state.get("mae", 0.0)
    rmse = st.session_state.get("rmse", 0.0)
    r2 = st.session_state.get("r2", 0.0)
    fig = st.session_state.get("ml_fig", None)

    # Default selections
    available_months = sorted(df["month"].unique())
    selected_months = available_months[-3:] if len(available_months) >= 3 else available_months
    selected_categories = sorted(df["category"].unique())

    df_filtered = df[df["month"].isin(selected_months) & df["category"].isin(selected_categories)]
    selected_chart_type = "bar"  # Default fallback, you can make this configurable if needed

    # 👇 Call the reusable report UI logic
    report_ui(df, selected_months, selected_categories, df_filtered, selected_chart_type, mae, rmse, r2, fig)


def report_ui(df, selected_months, selected_categories, df_filtered, selected_chart_type, mae, rmse, r2, fig):
    if st.button("📄 Download PDF Report"):
        with tempfile.TemporaryDirectory() as tmpdir:
            chart_paths = []

            # Main Charts
            for ct in ["Bar (Monthly Breakdown)", "Pie (Selected Months)", "Line (Daily Trend)"]:
                try:
                    ch = generate_chart(df_filtered, ct, selected_months, selected_categories)
                    if ch:
                        img_bytes = vegalite_to_png(ch.to_dict(), scale=3)
                        path = os.path.join(tmpdir, f"{ct.replace(' ', '_').replace('(', '').replace(')', '')}.png")
                        with open(path, "wb") as f:
                            f.write(img_bytes)
                        chart_paths.append(path)
                except Exception as e:
                    st.markdown(f""" <div class="custom-alert-warning">f"⚠️ Could not render {ct}: {e} </div>""", unsafe_allow_html=True)

            # Budget vs Actual Chart
            try:
                budget_vs_actual_chart, _ = generate_budget_vs_actual_chart(df, selected_months[-1], selected_chart_type)
                if budget_vs_actual_chart:
                    path = os.path.join(tmpdir, "budget_vs_actual.png")
                    with open(path, "wb") as f:
                        f.write(vegalite_to_png(budget_vs_actual_chart.to_dict(), scale=3))
                    chart_paths.append(path)
            except Exception as e:
                st.markdown(f""" <div class="custom-alert-warning">f"⚠️ Budget vs Actual chart error: {e} </div>""", unsafe_allow_html=True)

            # ML Model Chart (Optional)
            if fig:
                try:
                    ml_path = os.path.join(tmpdir, "ml_actual_vs_predicted.png")
                    fig.savefig(ml_path, dpi=300)
                    chart_paths.append(ml_path)
                except Exception as e:
                    st.markdown(f""" <div class="custom-alert-warning">f"⚠️ Model plot save error: {e}  </div>""", unsafe_allow_html=True)

            # Generate PDF
            report_path = generate_pdf_report(df, selected_months[-1], chart_paths, get_all_budgets(), mae, rmse, r2)

            # Download Button
            with open(report_path, "rb") as f:
                st.download_button(
                    "⬇️ Download Full Visual Report",
                    data=f,
                    file_name="finance_report.pdf",
                    mime="application/pdf"
                )

def show2():
    st.markdown("---")
    st.link_button(
        "📝 Give Feedback",
        "https://forms.gle/UNMYmAzc3kULbHQq8"
    )
    st.caption("Takes less than a minute")


