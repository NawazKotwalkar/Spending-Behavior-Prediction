import streamlit as st
from streamlit_option_menu import option_menu
from utils.auth_db import is_logged_in, get_user_role
from ui.auth import auth_ui

# ------------------- PAGE CONFIG & THEME -------------------
st.set_page_config(
    page_title="Expenso",
    page_icon="assets/expenso_logo.png",
    layout="wide",
)

# Load custom CSS theme
def load_theme():
    try:
        with open("styles/theme.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.markdown(f""" <div class="custom-alert-warning">"Theme CSS not found. Continuing with default style.</div>""", unsafe_allow_html=True)

load_theme()

if not is_logged_in():
    st.title("🔐 Login / Sign Up")
    auth_ui()
    st.stop()
if "role" not in st.session_state:
    st.session_state["role"] = get_user_role()

def logout():
    st.session_state.clear()

st.button("🔒 Logout", on_click=logout)

selected = option_menu(
    menu_title=None,
    options=["Home", "Upload", "Visualize", "Predict", "Report"],
    icons=["house", "upload", "bar-chart", "robot", "file-earmark-pdf"],
    orientation="horizontal",
)

if selected == "Home":
    import pages.home as home
    home.show()

elif selected == "Upload":
    import pages.Upload as upload
    upload.show()

elif selected == "Visualize":
    import pages.Visualize as visualize
    visualize.show()

elif selected == "Predict":
    import pages.Predict as predict
    predict.show()

elif selected == "Report":
    import pages.Report as report
    report.show()
    report.show2()