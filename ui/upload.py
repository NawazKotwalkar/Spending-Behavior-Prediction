import os
import pandas as pd
import streamlit as st

def save_uploaded_file(uploaded_file):
    if uploaded_file:
        os.makedirs("data", exist_ok=True)
        path = os.path.join("data", "transactions.csv")
        with open(path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return path
    return None
