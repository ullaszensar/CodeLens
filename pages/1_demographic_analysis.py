import streamlit as st
from utils import display_code_with_highlights
from styles import apply_custom_styles

def show_demographic_analysis():
    """Display demographic data analysis interface"""
    st.title("🔍 Demographic Analysis")
    st.markdown("### C360 Demographic & Target Data Analysis")

    # Application name input in sidebar
    app_name = st.sidebar.text_input("Application Name", "MyApp")

    # Main content area with two columns
    col1, col2 = st.columns(2)

    # First Excel Upload - Customer Demographic
    with col1:
        st.subheader("1. Customer Demographic Data")
        # Rest of the demographic analysis code...

if __name__ == "__main__":
    apply_custom_styles()
    show_demographic_analysis()
