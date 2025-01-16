import streamlit as st

def apply_custom_styles():
    """Apply custom CSS styles to the Streamlit app"""
    st.markdown("""
        <style>
        /* Main container */
        .main {
            padding: 2rem;
        }

        /* Metrics styling */
        .css-1ht1j8u {
            background-color: #f8f9fa;
            padding: 1rem;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        /* Expander styling */
        .streamlit-expanderHeader {
            background-color: #f8f9fa;
            border-radius: 5px;
        }

        /* Code blocks */
        .stCode {
            background-color: #f8f9fa !important;
            border-radius: 5px;
        }

        /* Progress bar */
        .stProgress > div > div {
            background-color: #0066cc;
        }

        /* File uploader */
        .uploadedFile {
            background-color: #f8f9fa;
            border-radius: 5px;
            padding: 0.5rem;
        }

        /* Buttons */
        .stButton > button {
            background-color: #0066cc;
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 5px;
        }

        /* Sidebar */
        .css-1d391kg, [data-testid="stSidebar"] {
            background-color: #e6f3ff !important;
        }

        /* Headers */
        h1, h2, h3 {
            color: #0066cc;
        }

        /* File tree */
        pre {
            background-color: #f8f9fa;
            padding: 1rem;
            border-radius: 5px;
            margin: 0.5rem 0;
        }
        </style>
    """, unsafe_allow_html=True)