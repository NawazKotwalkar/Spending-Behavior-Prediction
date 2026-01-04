from PIL import Image
from fpdf import FPDF
import os
import datetime
import pandas as pd


class PDF(FPDF):
    def __init__(self):
        super().__init__()
        self.add_font("DejaVu", "", "fonts/dejavu-fonts-ttf-2.37/ttf/DejaVuSans.ttf", uni=True)
        self.add_font("DejaVu", "B", "fonts/dejavu-fonts-ttf-2.37/ttf/DejaVuSans.ttf", uni=True)

    def header(self):
        self.set_font("DejaVu", "B", 14)
        self.cell(0, 10, "Personal Finance Report", ln=True, align="C")
        self.ln(6)

    def add_heading(self, text, size=13):
        self.set_font("DejaVu", "B", size)
        self.cell(0, 10, str(text), ln=True)
        self.ln(3)

    def add_text(self, text):
        self.set_font("DejaVu", "", 11)
        self.multi_cell(0, 8, str(text))
        self.ln(1)

    def add_chart_image(self, image_path, title=None):
        if not os.path.exists(image_path):
            self.add_text(f"Missing chart: {image_path}")
            return

        # 🔥 One chart per page
        self.add_page()

        if title:
            self.add_heading(title)

        try:
            with Image.open(image_path) as img:
                w_px, h_px = img.size
                aspect = h_px / w_px

                max_width_mm = 170
                max_height_mm = 220

                img_height = max_width_mm * aspect
                if img_height > max_height_mm:
                    img_height = max_height_mm

                self.image(image_path, w=max_width_mm, h=img_height)
        except Exception as e:
            self.add_text(f"Error displaying chart: {e}")


def generate_pdf_report(
    df: pd.DataFrame,
    selected_month: str,
    chart_paths=None,
    budget_df: pd.DataFrame = None,
    mae=None,
    rmse=None,
    r2=None
) -> str:

    chart_paths = chart_paths or []

    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # -------------------- HEADER INFO --------------------
    pdf.add_heading(f"Report for {selected_month}")
    pdf.add_text(
        f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )

    # -------------------- ML METRICS --------------------
    if mae is not None and rmse is not None and r2 is not None:
        pdf.add_heading("ML Model Evaluation")
        pdf.add_text(f"MAE (Mean Absolute Error): Rs.{mae:,.2f}")
        pdf.add_text(f"RMSE (Root Mean Squared Error): Rs.{rmse:,.2f}")
        pdf.add_text(f"R² Score: {r2:.4f}")

    # -------------------- MONTH DATA --------------------
    if "month" not in df.columns:
        pdf.add_text("Error: 'month' column missing.")
    else:
        month_df = df[df["month"] == selected_month].copy()

        if month_df.empty:
            pdf.add_text(f"No data available for {selected_month}.")
        else:
            month_df["amount"] = pd.to_numeric(
                month_df["amount"], errors="coerce"
            ).fillna(0)

            total_spent = month_df["amount"].sum()

            # -------------------- QUICK SUMMARY --------------------
            pdf.add_heading("Quick Summary")
            pdf.add_text(
                f"In {selected_month}, your total spending was Rs.{total_spent:,.2f}. "
                "This report highlights where your money went, compares it against "
                "your planned budget, and provides insights to improve spending habits."
            )

            # -------------------- CATEGORY BREAKDOWN --------------------
            pdf.add_heading("Category-wise Spending")
            if "category" in month_df.columns:
                cat_summary = (
                    month_df.groupby("category")["amount"]
                    .sum()
                    .reset_index()
                )

                for _, row in cat_summary.iterrows():
                    pdf.add_text(
                        f"- {row['category']}: Rs.{row['amount']:,.2f}"
                    )
            else:
                pdf.add_text("'category' column missing.")

            # -------------------- TOP 3 CATEGORIES --------------------
            pdf.add_heading("Top Spending Categories")
            top_cats = (
                cat_summary.sort_values("amount", ascending=False)
                .head(3)
            )

            for _, row in top_cats.iterrows():
                pdf.add_text(
                    f"- {row['category']}: Rs.{row['amount']:,.2f}"
                )

    # -------------------- CHARTS --------------------
    valid_charts = [p for p in chart_paths if os.path.exists(p)]
    if valid_charts:
        for path in valid_charts:
            title = (
                "Budget vs Actual Overview"
                if "budget_vs_actual" in path
                else os.path.splitext(os.path.basename(path))[0]
                .replace("_", " ")
                .title()
            )
            pdf.add_chart_image(path, title)
    else:
        pdf.add_text("No chart images available to include.")

    # -------------------- BUDGET VS ACTUAL --------------------
    if budget_df is not None and not month_df.empty:
        pdf.add_heading("Budget vs Actual Summary")

        actual_df = (
            month_df.groupby("category")["amount"]
            .sum()
            .reset_index()
        )

        merged = pd.merge(
            actual_df,
            budget_df,
            on="category",
            how="left"
        )

        merged = merged[merged["budget"].notna()]
        merged["difference"] = merged["amount"] - merged["budget"]

        if merged.empty:
            pdf.add_text("No matching budget categories for this month.")
        else:
            for _, row in merged.iterrows():
                status = (
                    "⚠️ Over Budget"
                    if row["difference"] > 0
                    else "✅ Within Budget"
                )
                pdf.add_text(
                    f"- {row['category']}: "
                    f"Spent Rs.{row['amount']:.2f} | "
                    f"Budget Rs.{row['budget']:.2f} → {status}"
                )

            # -------------------- RECOMMENDATIONS --------------------
            pdf.add_heading("Recommendations")
            overspent = merged[merged["difference"] > 0]

            if not overspent.empty:
                pdf.add_text(
                    "You exceeded your budget in some categories. "
                    "Consider reducing discretionary expenses or "
                    "revising your budget limits."
                )
            else:
                pdf.add_text(
                    "Great job! You stayed within your budget across all categories."
                )

    # -------------------- SAVE FILE --------------------
    os.makedirs("data", exist_ok=True)
    filename = f"report_{selected_month.replace('-', '')}.pdf"
    path = os.path.abspath(os.path.join("data", filename))
    pdf.output(path)

    return path
