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
            background-color: #2d3035;
            padding: 1rem;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        /* Expander styling */
        .streamlit-expanderHeader {
            background-color: #2d3035;
            border-radius: 5px;
        }
        
        /* Code blocks */
        .stCode {
            background-color: #272822 !important;
            border-radius: 5px;
        }
        
        /* Progress bar */
        .stProgress > div > div {
            background-color: #FF4B4B;
        }
        
        /* File uploader */
        .uploadedFile {
            background-color: #2d3035;
            border-radius: 5px;
            padding: 0.5rem;
        }
        
        /* Buttons */
        .stButton > button {
            background-color: #FF4B4B;
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 5px;
        }
        
        /* Sidebar */
        .css-1d391kg {
            background-color: #1E1E1E;
        }
        
        /* Headers */
        h1, h2, h3 {
            color: #FF4B4B;
        }
        
        /* File tree */
        pre {
            background-color: #2d3035;
            padding: 1rem;
            border-radius: 5px;
            margin: 0.5rem 0;
        }
        </style>
    """, unsafe_allow_html=True)
