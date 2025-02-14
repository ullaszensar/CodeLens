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

        /* Tables */
        div[data-testid="stTable"] {
            border: none !important;
        }

        table {
            border-collapse: collapse;
            margin: 0 !important;
        }

        th, td {
            border: none !important;
            text-align: left;
            padding: 8px;
            background-color: transparent !important;
        }

        tr:nth-child(even) {
            background-color: #f8f9fa;
        }

        /* Remove default table styles */
        .dataframe {
            border: none !important;
        }

        .dataframe th, .dataframe td {
            border: none !important;
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
            display: inline-block;
            white-space: nowrap;
            text-align: center;
            min-width: 120px;
            margin: 0 auto;
        }

        .download-button:hover {
            background-color: #90EE90;
            color: #262730 !important;
            text-decoration: none;
        }

        /* Analysis tab tables */
        div[data-testid="stHorizontalBlock"] {
            background: white;
            padding: 0;
            border: none !important;
            border-radius: 0;
            margin: 0;
            min-height: 0;
            line-height: normal;
        }

        div[data-testid="stHorizontalBlock"] > div {
            border: none !important;
            padding: 5px 10px;
            margin: 0;
            min-height: 0;
        }

        div[data-testid="stHorizontalBlock"] > div:last-child {
            border: none !important;
        }

        /* Table headers in Analysis tab */
        div[data-testid="stMarkdownContainer"] strong {
            color: #0066cc;
        }

        /* Export Reports table column styling */
        div[data-testid="stHorizontalBlock"]:has(> div > a.download-button) {
            display: flex;
            align-items: center;
        }

        div[data-testid="stHorizontalBlock"]:has(> div > a.download-button) > div:last-child {
            display: flex;
            justify-content: center;
            padding: 0 5px;
            min-width: 120px;
        }

        /* Additional styles for table rows */
        div[data-testid="column"] {
            padding: 0;
            border: none !important;
        }

        div[data-testid="stVerticalBlock"] > div {
            margin-bottom: 0 !important;
        }

        .element-container {
            margin: 0 !important;
            border: none !important;
        }
        </style>
    """, unsafe_allow_html=True)