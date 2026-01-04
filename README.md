Spending Behaviour Prediction Model
==================================

Overview
--------
This project focuses on analyzing user spending patterns and predicting future expenses using historical transaction data.
The system combines data preprocessing, feature engineering, and machine learning to provide meaningful insights into
personal finance behavior.

The model helps users:
- Understand spending habits
- Track category-wise expenses
- Compare actual spending vs budget
- Predict future monthly spending

--------------------------------------------------

Transaction Data Requirements
-----------------------------
The transaction file must be provided in CSV format and must contain the following columns:

- date        : Transaction date
- amount      : Transaction amount
- description : Description of the transaction
- category    : Spending category

Example:
date,amount,description,category

--------------------------------------------------

Budget Data Requirements
------------------------
The budget file must be provided in CSV format and must contain the following columns:

- category : Spending category
- budget   : Budget amount for that category

Example:
category,budget

--------------------------------------------------

Model Details
-------------
- The spending behaviour prediction model is trained using historical transaction data.
- Features are derived from past spending trends and category-wise aggregation.
- The model predicts future spending amounts on a monthly basis.

Data Integrity & Leakage
------------------------
- This project strictly avoids data leakage.
- Training data and prediction targets are properly separated.
- No future information is used during model training.

--------------------------------------------------

Database Note
-------------
The application uses a remote database server.
Initial connection and data loading may take some time depending on server response.

Kindly bear with the delay during startup or first load.

--------------------------------------------------

Tech Stack
----------
- Python
- Streamlit
- Machine Learning (Scikit-learn)
- MySQL
- Pandas, NumPy
- Data Visualization Libraries

--------------------------------------------------

Disclaimer
----------
Predictions are based on historical patterns and are meant for analytical purposes only.
Actual spending may vary due to external or unexpected factors.
