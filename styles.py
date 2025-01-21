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
            transition: background-color 0.3s;
        }

        .stButton > button:hover {
            background-color: #90EE90 !important;
            color: #262730 !important;
        }

        /* Tabs styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 2px;
            background-color: #0066cc;
            padding: 10px 10px 0 10px;
            border-radius: 5px 5px 0 0;
        }

        .stTabs [data-baseweb="tab"] {
            color: white !important;
            background-color: #0066cc;
            padding: 10px 20px;
            border-radius: 5px 5px 0 0;
        }

        .stTabs [data-baseweb="tab"][aria-selected="true"] {
            background-color: #004c99;
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
            background-color: #90EE90;
            color: #262730 !important;
            text-decoration: none;
        }

        /* Table styling */
        .stMarkdown table {
            width: 100%;
            margin-bottom: 1rem;
            border-collapse: collapse;
        }

        .stMarkdown td, .stMarkdown th {
            padding: 0.75rem;
            border: 1px solid #dee2e6;
            text-align: left;
        }

        .stMarkdown th {
            background-color: #f8f9fa;
            font-weight: bold;
            border-bottom: 2px solid #dee2e6;
        }

        /* Analysis tab tables */
        div[data-testid="stHorizontalBlock"] {
            background: white;
            padding: 10px;
            border: 1px solid #dee2e6;
            border-radius: 5px;
            margin: 5px 0;
        }

        div[data-testid="stHorizontalBlock"] > div {
            border-right: 1px solid #dee2e6;
            padding: 0 10px;
        }

        div[data-testid="stHorizontalBlock"] > div:last-child {
            border-right: none;
        }

        /* Table headers in Analysis tab */
        div[data-testid="stMarkdownContainer"] strong {
            color: #0066cc;
        }
        </style>
    """, unsafe_allow_html=True)