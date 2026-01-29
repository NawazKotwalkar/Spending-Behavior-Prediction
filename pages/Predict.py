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
        st.markdown(
            "<div class='custom-alert-warning'>📤 Upload a transaction file to use spending prediction.</div>",
            unsafe_allow_html=True
        )
        st.stop()

    df = st.session_state["df"].copy()

    if df.empty:
        st.markdown(
            "<div class='custom-alert-warning'>⚠️ Uploaded dataset is empty.</div>",
            unsafe_allow_html=True
        )
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
        st.markdown(
            "<div class='custom-alert-warning'>⚠️ Not enough data to train prediction model.</div>",
            unsafe_allow_html=True
        )
        st.stop()

    # ==================== TRAIN MODELS ====================
    with st.spinner("Training prediction model..."):
        models, metrics = train_cached_models(monthly)

    if not models:
        st.markdown(
            "<div class='custom-alert-warning'>⚠️ No categories have enough history to train a model.</div>",
            unsafe_allow_html=True
        )
        st.stop()

    # ==================== CATEGORY SELECTION ====================
    categories = sorted(models.keys())

    selected_category = st.selectbox(
        "Select Category",
        categories
    )

    # ==================== CATEGORY VALIDATION ====================
    if selected_category not in models:
        st.markdown(
            "<div class='custom-alert-warning'>⚠️ Not enough history for this category.</div>",
            unsafe_allow_html=True
        )
        st.stop()

    # ==================== MODEL ACCURACY ====================
    mae, rmse = metrics[selected_category]

    st.subheader("📈 Model Accuracy")
    col1, col2 = st.columns(2)

    col1.markdown(
        f"""
        <div class="metric-card info">
            <p class="metric-title">MAE</p>
            <p class="metric-value">₹{mae:,.2f}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    col2.markdown(
        f"""
        <div class="metric-card success">
            <p class="metric-title">RMSE</p>
            <p class="metric-value">₹{rmse:,.2f}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # ==================== NEXT MONTH PREDICTION ====================
    st.subheader("📅 Predict Next Month")

    prediction = predict_next_month(
        models=models,
        history_df=monthly,
        category=selected_category
    )

    st.markdown(
        f"<div class='custom-alert-success'>✅ Predicted "
        f"<b>{selected_category.capitalize()}</b> spend next month: "
        f"<b>₹{prediction:,.2f}</b></div>",
        unsafe_allow_html=True
    )

    # ==================== TRANSPARENCY ====================
    with st.expander("🔍 Last 3 Months Used for Prediction"):
        st.dataframe(
            monthly[monthly["category"] == selected_category]
            .sort_values("month", ascending=False)
            .head(3),
            use_container_width=True
        )
