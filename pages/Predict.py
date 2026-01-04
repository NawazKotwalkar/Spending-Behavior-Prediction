def show():
    import pandas as pd
    import os
    from pandas.tseries.offsets import MonthBegin
    import streamlit as st
    from models.spending_predictor import train_model, predict_spending
    from pathlib import Path

    # Load CSS once per session to avoid repeated injection
    def load_css_once(path="styles/styles.css"):
        if st.session_state.get("_css_loaded"):
            return
        p = Path(path)
        if p.exists():
            try:
                st.markdown(f"<style>{p.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)
                st.session_state["_css_loaded"] = True
            except Exception as e:
                st.markdown(f""" <div class="custom-alert-warning">f"Failed to load CSS: {e}</div>""", unsafe_allow_html=True)
        else:
            # silent fallback; user already warned in app shell if theme missing
            pass

    load_css_once()  # ensure your styles are injected

    st.subheader("🔮 Spending Prediction")

    transaction_file = st.session_state.get("transaction_file")
    if not transaction_file or not os.path.exists(transaction_file):
        st.markdown(f""" <div class="custom-alert-warning">"⚠️ Please upload a transaction file first.</div>""", unsafe_allow_html=True)
        return

    try:
        df = pd.read_csv(transaction_file, parse_dates=["date"])
    except Exception as e:
        st.error(f"❌ Failed to read transaction file: {e}")
        return

    # Train model
    with st.spinner("Training model..."):
        mae, rmse, r2 = train_model(df)

    # Show metrics (custom HTML so your CSS can style them)
    st.markdown("### 📈 Model Evaluation")

    metric_html = f"""
        <div class="metrics-row">
        <div class="custom-metric-card">
            <div class="custom-alert-warning">
            <div class="metric-title">MAE</div>
            <div class="metric-value">₹{mae:,.2f}</div>
            </div>
        </div>

        <div class="custom-metric-card">
            <div class="custom-alert-warning">
            <div class="metric-title">RMSE</div>
            <div class="metric-value">₹{rmse:,.2f}</div>
            </div>
        </div>

        <div class="custom-metric-card">
            <div class="custom-alert-warning">
            <div class="metric-title">R² Score</div>
            <div class="metric-value">{r2:.3f}</div>
            </div>
        </div>
        </div>
        """
    st.markdown(metric_html, unsafe_allow_html=True)


    df["month"] = df["date"].dt.to_period("M").astype(str)
    available_months = sorted(df["month"].unique())
    categories = sorted(df["category"].unique())

    # Add next month
    next_month = df["date"].max().to_period("M").to_timestamp() + MonthBegin(1)
    next_month_str = next_month.to_period("M").strftime("%Y-%m")
    if next_month_str not in available_months:
        available_months.append(next_month_str)

    st.markdown("### 📅 Predict")
    selected_month = st.selectbox("Select Month", available_months, index=len(available_months)-1)
    selected_category = st.selectbox("Select Category", categories)

    if st.button("Predict Future Spend"):
        prediction = predict_spending(selected_month, selected_category)
        if isinstance(prediction, str):
            st.error(prediction)
        else:
            pred_html = f"""
            <div class="prediction-card">
              <div class="pred-title">📊 Predicted Spend for <strong>{selected_category}</strong> in <strong>{selected_month}</strong></div>
              <div class="pred-amount">₹{max(0, prediction):,.2f}</div>
            </div>
            """
            st.markdown(pred_html, unsafe_allow_html=True)
