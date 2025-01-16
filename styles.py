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

        /* Download button styling */
        .download-button {
            background-color: #0066cc;
            color: white !important;
            padding: 0.3rem 0.8rem;
            border-radius: 4px;
            text-decoration: none;
            font-size: 0.9rem;
            transition: background-color 0.3s;
        }

        .download-button:hover {
            background-color: #0052a3;
            text-decoration: none;
        }

        /* Table styling */
        .stMarkdown table {
            width: 100%;
            margin-bottom: 1rem;
        }

        .stMarkdown td {
            padding: 0.5rem;
            border-bottom: 1px solid #e9ecef;
        }
        </style>
    """, unsafe_allow_html=True)