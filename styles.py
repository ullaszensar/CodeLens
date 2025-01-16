import streamlit as st

def apply_custom_styles():
    """Apply custom CSS styles to the Streamlit app"""
    st.markdown("""
        <style>
        /* Main container */
        .main {
            padding: 2rem;
            background-color: white;
        }

        /* Metrics styling */
        .css-1ht1j8u {
            background-color: #f8f9fa;
            padding: 1rem;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border: 1px solid #e9ecef;
        }

        /* Expander styling */
        .streamlit-expanderHeader {
            background-color: #f8f9fa;
            border-radius: 5px;
            border: 1px solid #e9ecef;
        }

        /* Code blocks */
        .stCode {
            background-color: #f8f9fa !important;
            border-radius: 5px;
            border: 1px solid #e9ecef;
        }

        /* Progress bar */
        .stProgress > div > div {
            background-color: #4B9CD3;
        }

        /* File uploader */
        .uploadedFile {
            background-color: #f8f9fa;
            border-radius: 5px;
            padding: 0.5rem;
            border: 1px solid #e9ecef;
        }

        /* Buttons */
        .stButton > button {
            background-color: #4B9CD3;
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 5px;
        }

        .stButton > button:hover {
            background-color: #357ABD;
        }

        /* Sidebar */
        .css-1d391kg {
            background-color: white;
        }

        /* Headers */
        h1, h2, h3 {
            color: #4B9CD3;
        }

        /* File tree */
        pre {
            background-color: #f8f9fa;
            padding: 1rem;
            border-radius: 5px;
            margin: 0.5rem 0;
            border: 1px solid #e9ecef;
        }
        </style>
    """, unsafe_allow_html=True)