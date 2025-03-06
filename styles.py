import streamlit as st

def apply_custom_styles():
    """Apply custom CSS styles to the Streamlit app"""
    st.markdown("""
        <style>
        /* Summary Table Styles */
        .summary-table {
            border-collapse: collapse;
            margin: 10px 0;
            font-size: 0.9em;
            width: 100%;
            box-shadow: 0 0 20px rgba(0, 0, 0, 0.15);
        }

        .summary-table thead tr {
            background-color: #0066cc;
            color: white;
            text-align: left;
        }

        .summary-table th,
        .summary-table td {
            padding: 8px 12px;
            text-align: left;
        }

        .summary-table tbody tr {
            border-bottom: 1px solid #dddddd;
        }

        .summary-table tbody tr:nth-of-type(even) {
            background-color: #f3f3f3;
        }

        /* Reduce the height of detail sections */
        .detail-section {
            margin: 10px 0;
            padding: 10px;
            background-color: #f8f9fa;
            border-radius: 5px;
            max-height: 300px;
            overflow-y: auto;
        }

        /* Main container */
        .main {
            padding: 2rem;
        }

        /* File uploader styling */
        .stUploadedFile {
            border: 1px solid #e6e6e6;
            border-radius: 5px;
            padding: 1rem;
            margin-bottom: 1rem;
            background-color: #ffffff;
        }

        .uploadedFile {
            background-color: #f8f9fa;
            border-radius: 5px;
            padding: 1rem;
            margin-bottom: 1rem;
        }

        /* Metrics styling */
        [data-testid="stMetricValue"] {
            font-size: 1.5rem !important;
            color: #0066cc !important;
        }

        /* Container styling */
        [data-testid="stVerticalBlock"] > div {
            padding: 0.5rem 0;
        }

        /* Download button styling */
        .download-button {
            display: inline-block;
            padding: 0.5rem 1rem;
            background-color: #0066cc;
            color: white !important;
            text-decoration: none;
            border-radius: 5px;
            text-align: center;
            margin: 0.5rem 0;
            width: 100%;
            transition: background-color 0.3s;
        }

        .download-button:hover {
            background-color: #90EE90;
            color: #262730 !important;
            text-decoration: none;
        }

        /* Success message styling */
        .stSuccess {
            background-color: #d4edda;
            color: #155724;
            padding: 1rem;
            border-radius: 5px;
            margin: 1rem 0;
        }

        /* Separator styling */
        hr {
            margin: 1.5rem 0;
            border: 0;
            border-top: 1px solid #e6e6e6;
        }

        /* Table styling */
        .stDataFrame {
            border: 1px solid #e6e6e6;
            border-radius: 5px;
            padding: 0.5rem;
        }

        /* Section headers */
        .subheader {
            color: #0066cc;
            margin-bottom: 1rem;
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

        /* Analysis tab tables */
        div[data-testid="stHorizontalBlock"] {
            background: white;
            padding: 0;
            border: none;
            border-radius: 0;
            margin: 0;
            min-height: 0;
            line-height: normal;
        }

        div[data-testid="stHorizontalBlock"] > div {
            border-right: none;
            padding: 5px 10px;
            margin: 0;
            min-height: 0;
        }

        div[data-testid="stHorizontalBlock"] > div:last-child {
            border-right: none;
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
            border: none;
        }

        div[data-testid="stVerticalBlock"] > div {
            margin-bottom: 0 !important;
        }

        .element-container {
            margin: 0 !important;
            border: none;
        }
        </style>
    """, unsafe_allow_html=True)