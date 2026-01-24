import pandas as pd
import streamlit as st
from pandas.tseries.offsets import MonthBegin
from models.spending_predictor import train_model, predict_spending

@st.cache_resource
def train_cached_model(monthly_df):
    return train_model(monthly_df)

def show():
    if "df" not in st.session_state:
        st.warning("Please upload a transaction file first.")
        st.stop()

    st.subheader("🔮 Spending Prediction")

    df = st.session_state["df"]

    # ---------- Monthly aggregation ----------
    monthly = (
        df[df["spend"] > 0]
        .groupby(["month", "category"])
        .agg(total_spend=("spend", "sum"))
        .reset_index()
    )

    if monthly.empty:
        st.warning("Not enough data to train the prediction model.")
        return

    available_months = sorted(
        monthly["month"].unique(),
        key=lambda x: pd.Period(x, freq="M")
    )
    categories = sorted(monthly["category"].unique())

    # ---------- Train model ----------
    with st.spinner("Training model..."):
        model, (mae, rmse) = train_cached_model(monthly)

    # Store metrics for PDF
    st.session_state["mae"] = mae
    st.session_state["rmse"] = rmse

    # ---------- Metrics ----------
    st.subheader("📈 Model Evaluation")
    st.metric("MAE", f"₹{mae:,.2f}")
    st.metric("RMSE", f"₹{rmse:,.2f}")

    # ---------- Add next month ----------
    next_month = (
        pd.Period(available_months[-1], freq="M")
        .to_timestamp() + MonthBegin(1)
    ).strftime("%Y-%m")

    if next_month not in available_months:
        available_months.append(next_month)

    # ---------- Prediction UI ----------
    st.subheader("📅 Predict")
    selected_month = st.selectbox("Select Month", available_months)
    selected_category = st.selectbox("Select Category", categories)

    if st.button("Predict Future Spend"):
        prediction = predict_spending(
            model=model,
            month=selected_month,
            category=selected_category
        )
        st.success(f"Predicted Spend: ₹{prediction:,.2f}")