import streamlit as st
from styles import apply_custom_styles

def show_about():
    st.title("ℹ️ About CodeLens")
    
    st.markdown("""
    ### Overview
    CodeLens is an advanced data preprocessing and visualization platform that empowers users to explore, 
    analyze, and generate complex system representations through intuitive interface and intelligent tools.

    ### Core Features
    - Streamlit interactive frontend
    - Pandas-powered data processing
    - Multi-diagram generation
    - OpenAI-powered insights
    - Advanced data cleaning and matching algorithms
    - Cross-platform path handling
    - Flexible export and visualization options

    ### Created by
    Zensar Project Diamond Team
    """)

if __name__ == "__main__":
    apply_custom_styles()
    show_about()
