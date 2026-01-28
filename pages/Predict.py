import streamlit as st
import pandas as pd

from models.spending_predictor import train_models_by_category, predict_next_month


@st.cache_resource
def train_cached_models(monthly_df):
    monthly_df = monthly_df.sort_values(["category", "month"]).reset_index(drop=True)
    return train_models_by_category(monthly_df)


def show():
    st.subheader("🔮 Spending Prediction")

    # ==================== REQUIRE UPLOADED DATA ====================
    if "df" not in st.session_state:
        st.info("Upload a transaction file to use spending prediction.")
        st.stop()

    df = st.session_state["df"].copy()

    if df.empty:
        st.info("Uploaded dataset is empty.")
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

    monthly = (
        df[df["amount"] > 0]
        .groupby(["month", "category"], as_index=False)
        .agg(total_spend=("amount", "sum"))
    )

    if len(monthly) < 3:
        st.warning("Not enough data to train prediction model.")
        st.stop()

    # ==================== TRAIN MODELS ====================
    with st.spinner("Training prediction model..."):
        models, metrics = train_cached_models(monthly)

    if not models:
        st.warning("No categories have enough history to train a model.")
        st.stop()

    # ==================== CATEGORY SELECTION (DEFINE FIRST) ====================
    categories = sorted(models.keys())

    selected_category = st.selectbox(
        "Select Category",
        categories
    )

    # ==================== CATEGORY VALIDATION ====================
    if selected_category not in models:
        st.warning("Not enough history for this category.")
        st.stop()

    # ==================== MODEL ACCURACY ====================
    mae, rmse = metrics[selected_category]

    st.subheader("📈 Model Accuracy")
    col1, col2 = st.columns(2)
    col1.markdown(f"<p>MAE</p><h2 style='color:#1b5e20;'>₹{mae:,.2f}</h2>", unsafe_allow_html=True)
    col2.markdown(f"<p>RMSE</p><h2 style='color:#2e7d32;'>₹{rmse:,.2f}</h2>", unsafe_allow_html=True)

    # ==================== NEXT MONTH PREDICTION ====================
    st.subheader("📅 Predict Next Month")

    prediction = predict_next_month(
        models=models,
        history_df=monthly,
        category=selected_category
    )

    st.success(
        f"Predicted {selected_category.capitalize()} Spend Next Month: ₹{prediction:,.2f}"
    )

    # ==================== TRANSPARENCY ====================
    with st.expander("🔍 Last 3 Months Used for Prediction"):
        st.dataframe(
            monthly[monthly["category"] == selected_category]
            .sort_values("month", ascending=False)
            .head(3),
            use_container_width=True
        )
