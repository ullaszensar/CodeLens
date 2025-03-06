# Package Installation Instructions:
# 1. One-line installation (recommended):
#    pip install streamlit==1.41.1 plotly==5.18.0 pandas==2.1.4 pygments==2.18.0 fuzzywuzzy==0.18.0 
#    python-levenshtein==0.23.0 openpyxl==3.1.2 trafilatura==1.6.4 xlsxwriter==3.1.9
#
# Note: If you encounter any issues, try upgrading pip first:
#    python -m pip install --upgrade pip
#
# Package Version Check
import pkg_resources
import sys
import logging
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Start timing the initialization
logger.info("Starting application initialization...")
start_time = time.time()

def check_required_packages():
    """Check if all required packages are installed with correct versions"""
    required_packages = {
        'streamlit': '1.41.1',
        'plotly': '5.18.0',
        'pandas': '2.1.4',
        'pygments': '2.18.0',
        'fuzzywuzzy': '0.18.0',
        'python-levenshtein': '0.23.0',
        'openpyxl': '3.1.2',
        'trafilatura': '1.6.4',
        'xlsxwriter': '3.1.9'
    }

    missing_packages = []
    outdated_packages = []

    print("\nVerifying package installations...")

    for package, required_version in required_packages.items():
        try:
            installed_version = pkg_resources.get_distribution(package).version
            if installed_version != required_version:
                outdated_packages.append(f"{package} (installed: {installed_version}, required: {required_version})")
                print(f"✗ {package} {installed_version} (required: {required_version})")
            else:
                print(f"✓ {package} {installed_version}")
        except pkg_resources.DistributionNotFound:
            missing_packages.append(package)
            print(f"✗ {package} not found")

    if missing_packages or outdated_packages:
        print("\nPackage Verification Failed:")
        if missing_packages:
            print("\nMissing Packages:")
            for pkg in missing_packages:
                print(f"- {pkg}")
        if outdated_packages:
            print("\nOutdated Packages:")
            for pkg in outdated_packages:
                print(f"- {pkg}")
        print("\nPlease install required packages using:")
        print(" ".join([f"{pkg}=={ver}" for pkg, ver in required_packages.items()]))
        sys.exit(1)
    else:
        print("\n✓ All required packages are correctly installed!")

# Check packages before importing
check_required_packages()

# Rest of your imports
import streamlit as st
import tempfile
import os
from pathlib import Path
import time
from datetime import datetime
from codescan import CodeAnalyzer
from utils import display_code_with_highlights, create_file_tree
from styles import apply_custom_styles
import base64
import io
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
import pandas as pd
from fuzzywuzzy import process, fuzz
import re

# Add timing checks for key initialization steps
def init_app():
    """Initialize application components with timing checks"""
    init_start = time.time()

    # Page config
    st.set_page_config(
        page_title="CodeLens - Code Utility",
        page_icon="🔍",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    logger.info(f"Page config initialized in {time.time() - init_start:.2f}s")

    # Apply custom styles
    style_start = time.time()
    apply_custom_styles()
    logger.info(f"Custom styles applied in {time.time() - style_start:.2f}s")

    # Initialize session state if needed
    if 'df_customer' not in st.session_state:
        st.session_state.df_customer = None
    if 'df_meta' not in st.session_state:
        st.session_state.df_meta = None
    if 'meta_preprocessing_stats' not in st.session_state:
        st.session_state.meta_preprocessing_stats = None
    if 'customer_preprocessing_stats' not in st.session_state:
        st.session_state.customer_preprocessing_stats = None

    logger.info(f"Total initialization completed in {time.time() - init_start:.2f}s")

# Call initialization
init_app()

# Page config - REMOVED, replaced by init_app()
# st.set_page_config(
#     page_title="CodeLens - Code Utility",
#     page_icon="🔍",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )
#
# # Apply custom styles
# apply_custom_styles()

# Creator information
st.sidebar.markdown("""
### Created by:
Zensar Project Diamond Team
""")

def get_file_download_link(file_path):
    """Generate a download link for a file"""
    with open(file_path, 'r') as f:
        data = f.read()
    b64 = base64.b64encode(data.encode()).decode()
    return f'<a href="data:text/html;base64,{b64}" download="{os.path.basename(file_path)}" class="download-button">Download</a>'

def parse_timestamp_from_filename(filename):
    """Extract timestamp from filename format app_name_code_analysis_YYYYMMDD_HHMMSS"""
    try:
        # Extract date and time part
        date_time_str = filename.split('_')[-2] + '_' + filename.split('_')[-1].split('.')[0]
        return datetime.strptime(date_time_str, '%Y%m%d_%H%M%S')
    except:
        return datetime.min

def read_log_file():
    """Read and format the log file content"""
    try:
        if os.path.exists('code_analysis.log'):
            with open('code_analysis.log', 'r') as f:
                logs = f.readlines()
            return logs
        return []
    except Exception as e:
        return [f"Error reading log file: {str(e)}"]

def compare_attributes(df1, df2, algorithm_type, threshold, match_type="Attribute Name"):
    """Compare attributes between two dataframes using fuzzy matching"""
    # Select scoring function based on algorithm type
    if algorithm_type == "Levenshtein Ratio (Basic)":
        scorer = fuzz.ratio
    elif algorithm_type == "Partial Ratio (Substring)":
        scorer = fuzz.partial_ratio
    else:  # Token Sort Ratio
        scorer = fuzz.token_sort_ratio

    matches = []

    # Compare attr_name columns only
    if 'attr_name' not in df1.columns:
        return pd.DataFrame()

    # Get unique values from both dataframes based on match type
    if match_type == "Business Name":
        customer_values = df1['business_name'].dropna().unique()
        target_values = df2['business_name'].dropna().unique()
    elif match_type == "Attribute Description":
        customer_values = df1['attr_description'].dropna().unique()
        target_values = df2['attr_description'].dropna().unique()
    else:  # Default to Attribute Name
        customer_values = df1['attr_name'].dropna().unique()
        target_values = df2['attr_name'].dropna().unique()

    # Compare values based on match type
    for customer_value in customer_values:
        # Get relevant information based on match type
        if match_type == "Business Name":
            customer_value_field = 'business_name'
            display_field = 'Business Name'
        elif match_type == "Attribute Description":
            customer_value_field = 'attr_description'
            display_field = 'Attribute Description'
        else:
            customer_value_field = 'attr_name'
            display_field = 'Attribute Name'

        # Get full customer record
        customer_record = df1[df1[customer_value_field] == customer_value].iloc[0]

        # Get top matches from target data
        value_matches = process.extract(
            customer_value,
            target_values,
            scorer=scorer,
            limit=3
        )

        # Add matches that meet the threshold
        for target_value, score in value_matches:
            if score >= threshold:
                # Get full target record
                target_record = df2[df2[customer_value_field] == target_value].iloc[0]

                # Create base match entry with matching details
                match_entry = {
                    'Match Score (%)': score
                }

                # Add all columns from customer record with C360 prefix
                for col in customer_record.index:
                    match_entry[f'C360 {col}'] = customer_record[col]

                # Add all columns from target record with Target Data prefix
                for col in target_record.index:
                    match_entry[f'Target Data {col}'] = target_record[col]

                matches.append(match_entry)

    # Create DataFrame and sort by match score
    df_matches = pd.DataFrame(matches)
    if not df_matches.empty:
        # Sort by match score
        df_matches = df_matches.sort_values('Match Score (%)', ascending=False)

    return df_matches

def preprocess_meta_data(df):
    """Preprocess meta data by removing rows with single integers/special chars or empty descriptions"""
    initial_rows = len(df)
    removed_rows = {
        'integer_description': 0,
        'empty_description': 0,
        'single_value': 0
    }

    # Copy dataframe to avoid modifying original
    processed_df = df.copy()

    if 'attr_description' in processed_df.columns:
        # Check for empty or NA values in attr_description
        empty_mask = processed_df['attr_description'].isna() | (processed_df['attr_description'].astype(str).str.strip() == '')
        if empty_mask.any():
            print(f"Found {empty_mask.sum()} rows with empty attr_description")
            removed_rows['empty_description'] = empty_mask.sum()
            processed_df = processed_df[~empty_mask]

        # Check for integer-only content in attr_description
        integer_mask = processed_df['attr_description'].astype(str).str.match(r'^\d+$')
        if integer_mask.any():
            print(f"Found {integer_mask.sum()} rows with integer-only content in attr_description")
            removed_rows['integer_description'] = integer_mask.sum()
            processed_df = processed_df[~integer_mask]

    # Check each cell for single integer or special character
    def check_single_value(val):
        if pd.isna(val):
            return False
        val_str = str(val).strip()
        # Check for single integer
        if val_str.isdigit():
            return True
        # Check for single special character (non-alphanumeric)
        if len(val_str) == 1 and not val_str.isalnum():
            return True
        return False

    # Apply check to all cells
    single_value_mask = processed_df.apply(
        lambda row: any(check_single_value(val) for val in row),
        axis=1
    )

    if single_value_mask.any():
        print(f"Found {single_value_mask.sum()} rows with single integer or special character values")
        removed_rows['single_value'] = single_value_mask.sum()
        processed_df = processed_df[~single_value_mask]

    # Calculate total rows removed
    total_removed = initial_rows - len(processed_df)
    print(f"\nPreprocessing Summary for Target Data:")
    print(f"Initial rows: {initial_rows}")
    print(f"Rows removed due to empty description: {removed_rows['empty_description']}")
    print(f"Rows removed due to integer-only description: {removed_rows['integer_description']}")
    print(f"Rows removed due to single integer/special char: {removed_rows['single_value']}")
    print(f"Final rows: {len(processed_df)}")

    return processed_df, {
        'initial_rows': initial_rows,
        'final_rows': len(processed_df),
        'total_removed': total_removed,
        'details': removed_rows
    }

def preprocess_customer_data(df):
    """Preprocess customer data by removing rows with single integers/special chars or empty descriptions"""
    initial_rows = len(df)
    removed_rows = {
        'integer_description': 0,
        'empty_description': 0,
        'single_value': 0
    }

    # Copy dataframe to avoid modifying original
    processed_df = df.copy()

    if 'attr_description' in processed_df.columns:
        # Check for empty or NA values in attr_description
        empty_mask = processed_df['attr_description'].isna() | (processed_df['attr_description'].astype(str).str.strip() == '')
        if empty_mask.any():
            print(f"Found {empty_mask.sum()} rows with empty attr_description")
            removed_rows['empty_description'] = empty_mask.sum()
            processed_df = processed_df[~empty_mask]

        # Check for integer-only content in attr_description
        integer_mask = processed_df['attr_description'].astype(str).str.match(r'^\d+$')
        if integer_mask.any():
            print(f"Found {integer_mask.sum()} rows with integer-only content in attr_description")
            removed_rows['integer_description'] = integer_mask.sum()
            processed_df = processed_df[~integer_mask]

    # Check each cell for single integer or special character
    def check_single_value(val):
        if pd.isna(val):
            return False
        val_str = str(val).strip()
        # Check for single integer
        if val_str.isdigit():
            return True
        # Check for single special character (non-alphanumeric)
        if len(val_str) == 1 and not val_str.isalnum():
            return True
        return False

    # Apply check to all cells
    single_value_mask = processed_df.apply(
        lambda row: any(check_single_value(val) for val in row),
        axis=1
    )

    if single_value_mask.any():
        print(f"Found {single_value_mask.sum()} rows with single integer or special character values")
        removed_rows['single_value'] = single_value_mask.sum()
        processed_df = processed_df[~single_value_mask]

    # Calculate total rows removed
    total_removed = initial_rows - len(processed_df)
    print(f"\nPreprocessing Summary for Customer Data:")
    print(f"Initial rows: {initial_rows}")
    print(f"Rows removed due to empty description: {removed_rows['empty_description']}")
    print(f"Rows removed due to integer-only description: {removed_rows['integer_description']}")
    print(f"Rows removed due to single integer/special char: {removed_rows['single_value']}")
    print(f"Final rows: {len(processed_df)}")

    return processed_df, {
        'initial_rows': initial_rows,
        'final_rows': len(processed_df),
        'total_removed': total_removed,
        'details': removed_rows
    }

def create_removed_rows_df(preprocessing_stats, original_df, processed_df):
    """Create a detailed DataFrame of removed rows with reasons"""
    # Find indices of removed rows
    original_indices = set(original_df.index)
    kept_indices = set(processed_df.index)
    removed_indices = original_indices - kept_indices

    # Create list to store removed row information
    removed_rows_data = []

    def check_single_value(val):
        if pd.isna(val):
            return False
        val_str = str(val).strip()
        if val_str.isdigit():
            return True
        if len(val_str) == 1 and not val_str.isalnum():
            return True
        return False

    # Check each removed row
    for idx in removed_indices:
        row = original_df.loc[idx]
        reason = []

        if 'attr_description' in row.index:
            # Check for empty description
            if pd.isna(row['attr_description']) or str(row['attr_description']).strip() == '':
                reason.append("Empty attr_description")
            # Check for integer-only description
            elif str(row['attr_description']).isdigit():
                reason.append("Integer-only attr_description")

        # Check for single integer or special character in any cell
        for col in row.index:
            if check_single_value(row[col]):
                reason.append(f"Single integer or special character in column '{col}'")
                break

        # Add row to data with detailed reason
        if reason:
            removed_rows_data.append({
                'Original Row Number': idx + 1,
                'Removal Reason': ' & '.join(reason),
                **row.to_dict()
            })

    # Create DataFrame
    removed_df = pd.DataFrame(removed_rows_data)
    return removed_df



def show_demographic_analysis():
    """Display demographic data analysis interface"""
    st.title("🔍 CodeLens")
    st.markdown("### C360 Demographic & Target Data Analysis")

    # Application name input in sidebar
    st.sidebar.header("Analysis Settings")
    app_name = st.sidebar.text_input("Application Name", "MyApp")

    # Initialize session state for dataframes if not present

    # Main content area with two columns
    col1, col2 = st.columns(2)

    # First Excel Upload - Customer Demographic
    with col1:
        st.subheader("1. Customer Demographic Data")
        

        # Add container for file upload
        with st.container():
            customer_demo_file = st.file_uploader(
                "Upload Customer Demographic Excel",
                type=['xlsx', 'xls'],
                key='customer_demo'
            )

        if customer_demo_file is not None:
            try:
                raw_df_customer = pd.read_excel(customer_demo_file)
                st.session_state.df_customer, st.session_state.customer_preprocessing_stats = preprocess_customer_data(raw_df_customer)
                st.success("✅ Customer Demographic file Processed successfully")

                # File Summary
                st.markdown("""
                    <h4 style='color: #0066cc; margin-bottom: 10px;'>File Summary</h4>
                    <table class='summary-table'>
                        <thead>
                            <tr>
                                <th>Metric</th>
                                <th>Value</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>Total Rows</td>
                                <td>{}</td>
                            </tr>
                            <tr>
                                <td>Total Columns</td>
                                <td>{}</td>
                            </tr>
                        </tbody>
                    </table>
                """.format(
                    len(st.session_state.df_customer),
                    len(st.session_state.df_customer.columns)
                ), unsafe_allow_html=True)

                # Preprocessing Summary
                st.markdown("""
                    <h4 style='color: #0066cc; margin-bottom: 10px;'>Preprocessing Summary</h4>
                    <table class='summary-table'>
                        <thead>
                            <tr>
                                <th>Metric</th>
                                <th>Value</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>Initial Rows</td>
                                <td>{}</td>
                            </tr>
                            <tr>
                                <td>Rows Removed</td>
                                <td>{}</td>
                            </tr>
                            <tr>
                                <td>Final Rows</td>
                                <td>{}</td>
                            </tr>
                        </tbody>
                    </table>
                """.format(
                    st.session_state.customer_preprocessing_stats['initial_rows'],
                    st.session_state.customer_preprocessing_stats['total_removed'],
                    st.session_state.customer_preprocessing_stats['final_rows']
                ), unsafe_allow_html=True)

                # Download buttons in a container
                with st.container():
                    download_cols = st.columns(2)
                    with download_cols[0]:
                        st.markdown(
                            download_dataframe(
                                st.session_state.df_customer,
                                "customer_demographic",
                                "excel",
                                button_text="Processed Data"
                            ),
                            unsafe_allow_html=True
                        )
                    with download_cols[1]:
                        # Create detailed removed rows DataFrame
                        removed_df = create_removed_rows_df(
                            st.session_state.customer_preprocessing_stats,
                            raw_df_customer,
                            st.session_state.df_customer
                        )
                        st.markdown(
                            download_dataframe(
                                removed_df,
                                "customer_removed_rows",
                                "excel",
                                button_text="Removed Rows"
                            ),
                            unsafe_allow_html=True
                        )

                # Data Preview with reduced height
                st.markdown("<h4 style='color: #0066cc; margin-bottom: 10px;'>Data Preview</h4>", unsafe_allow_html=True)
                with st.container():
                    st.markdown("<div class='detail-section'>", unsafe_allow_html=True)
                    st.dataframe(st.session_state.df_customer.head(5), use_container_width=True)
                    st.markdown("</div>", unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Error loading customer demographic file: {str(e)}")

    # Second Excel Upload - Meta Data
    with col2:
        st.subheader("2. Target Data")
        

        # Add container for file upload
        with st.container():
            meta_data_file = st.file_uploader(
                "Upload Target Data Excel",
                type=['xlsx', 'xls'],
                key='meta_data'
            )

        if meta_data_file is not None:
            try:
                raw_df_meta = pd.read_excel(meta_data_file)
                st.session_state.df_meta, st.session_state.meta_preprocessing_stats = preprocess_meta_data(raw_df_meta)
                st.success("✅ Target Data Processed Successfully")

                # File Summary
                st.markdown("""
                    <h4 style='color: #0066cc; margin-bottom: 10px;'>File Summary</h4>
                    <table class='summary-table'>
                        <thead>
                            <tr>
                                <th>Metric</th>
                                <th>Value</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>Total Rows</td>
                                <td>{}</td>
                            </tr>
                            <tr>
                                <td>Total Columns</td>
                                <td>{}</td>
                            </tr>
                        </tbody>
                    </table>
                """.format(
                    len(st.session_state.df_meta),
                    len(st.session_state.df_meta.columns)
                ), unsafe_allow_html=True)

                # Preprocessing Summary
                st.markdown("""
                    <h4 style='color: #0066cc; margin-bottom: 10px;'>Preprocessing Summary</h4>
                    <table class='summary-table'>
                        <thead>
                            <tr>
                                <th>Metric</th>
                                <th>Value</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>Initial Rows</td>
                                <td>{}</td>
                            </tr>
                            <tr>
                                <td>Rows Removed</td>
                                <td>{}</td>
                            </tr>
                            <tr>
                                <td>Final Rows</td>
                                <td>{}</td>
                            </tr>
                        </tbody>
                    </table>
                """.format(
                    st.session_state.meta_preprocessing_stats['initial_rows'],
                    st.session_state.meta_preprocessing_stats['total_removed'],
                    st.session_state.meta_preprocessing_stats['final_rows']
                ), unsafe_allow_html=True)

                # Download buttons in a container
                with st.container():
                    download_cols = st.columns(2)
                    with download_cols[0]:
                        st.markdown(
                            download_dataframe(
                                st.session_state.df_meta,
                                "target_data",
                                "excel",
                                button_text="Processed Data"
                            ),
                            unsafe_allow_html=True
                        )
                    with download_cols[1]:
                        removed_df = create_removed_rows_df(
                            st.session_state.meta_preprocessing_stats,
                            raw_df_meta,
                            st.session_state.df_meta
                        )
                        st.markdown(
                            download_dataframe(
                                removed_df,
                                "target_removed_rows",
                                "excel",
                                button_text="Removed Rows"
                            ),
                            unsafe_allow_html=True
                        )

                # Data Preview with reduced height
                st.markdown("<h4 style='color: #0066cc; margin-bottom: 10px;'>Data Preview</h4>", unsafe_allow_html=True)
                with st.container():
                    st.markdown("<div class='detail-section'>", unsafe_allow_html=True)
                    st.dataframe(st.session_state.df_meta.head(5), use_container_width=True)
                    st.markdown("</div>", unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Error loading meta data file: {str(e)}")

    # Attribute comparison section
    if st.session_state.df_meta is not None and st.session_state.df_customer is not None:
        st.markdown("### Compare Attributes")
        st.markdown("#### Attribute Matching Settings")

        # Algorithm selection for attribute matching
        col1, col2, col3 = st.columns(3)
        with col1:
            attr_algorithm = st.selectbox(
                "Select Attribute Matching Algorithm",
                [
                    "Levenshtein Ratio (Basic)",
                    "Partial Ratio (Substring)",
                    "Token Sort Ratio (Word Order)"
                ],
                key="attr_algorithm"
            )

        with col2:
            # Similarity threshold
            attr_threshold = st.slider(
                "Attribute Similarity Threshold (%)",
                min_value=0,
                max_value=100,
                value=60,
                help="Minimum similarity score required for attribute matches",
                key="attr_threshold"
            )

        with col3:
            match_type = st.selectbox(
                "Select Match Type",
                [
                    "Attribute Name",
                    "Business Name",
                    "Attribute Description"
                ],
                key="match_type",
                index=0  # Set default to first option (Attribute Name)
            )

        # Compare attributes only if match type is selected
        if match_type:
            attribute_matches = compare_attributes(
                st.session_state.df_customer,
                st.session_state.df_meta,
                attr_algorithm,
                attr_threshold,
                match_type
            )

            if not attribute_matches.empty:
                # Add Matching Attributes Summary
                st.markdown("#### Matching Attributes Summary")
                match_summary_cols = st.columns(3)
                high_confidence_matches = len(attribute_matches[attribute_matches['Match Score (%)'] >= 80])

                match_summary_cols[0].metric(
                    "Total Matches",
                    len(attribute_matches)
                )
                match_summary_cols[1].metric(
                    "High Confidence Matches (≥80%)",
                    high_confidence_matches
                )
                match_summary_cols[2].metric(
                    "Average Match Score",
                    f"{attribute_matches['Match Score (%)'].mean():.1f}%"
                )

                st.markdown("#### Matching Attributes Details")
                # Add Download button at the top right
                col1, col2 = st.columns([8, 2])
                with col2:
                    st.markdown(
                        download_dataframe(
                            attribute_matches,
                            "matching_attributes",
                            "excel",
                            button_text="Download",
                            match_type=match_type
                        ),
                        unsafe_allow_html=True
                    )

                # Create display version with minimal columns for better readability
                display_df = attribute_matches.copy()

                # For display, show only the main attribute columns and score
                if match_type == "Business Name":
                    display_columns = ['C360 business_name', 'Target Data business_name', 'Match Score (%)']
                elif match_type == "Attribute Description":
                    display_columns = ['C360 attr_description', 'Target Data attr_description', 'Match Score (%)']
                else:  # Default to Attribute Name
                    display_columns = ['C360 attr_name', 'Target Data attr_name', 'Match Score (%)']

                # Ensure all display columns exist in the DataFrame
                display_columns = [col for col in display_columns if col in display_df.columns]

                # If we couldn't find the exact columns, fall back to first columns of each type
                if len(display_columns) < 3:
                    c360_cols = [col for col in display_df.columns if col.startswith('C360 ')]
                    target_cols = [col for col in display_df.columns if col.startswith('Target Data ')]
                    if c360_cols and target_cols:
                        display_columns = [c360_cols[0], target_cols[0], 'Match Score (%)']
                    else:
                        display_columns = ['Match Score (%)']

                display_df = display_df[display_columns]

                st.markdown(
                    """
                    <style>
                    .stDataFrame {
                        max-height: 400px;
                        overflow-y: auto;
                    }
                    </style>
                    """,
                    unsafe_allow_html=True
                )
                st.dataframe(
                    display_df,
                    hide_index=True,
                    height=400,
                    use_container_width=True
                )

            else:
                st.info("No matching attributes found with the current threshold")
    else:
        st.info("Please upload both Customer Demographic and Target Data files to compare attributes")


def download_dataframe(df, file_name, file_format='excel', button_text="Download", match_type="All"):
    """Generate a download link for a dataframe in Excel format"""
    # Create a descriptive file name based on match type
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    match_type_name = match_type.replace(" ", "_").lower()
    file_name = f"{file_name}_{timestamp}"

    # Create a copy of the DataFrame for download
    download_df = df.copy()

    # For matching attributes, ensure proper column ordering with blank separator
    if 'matching_attributes' in file_name:
        # Get column groups
        c360_cols = [col for col in download_df.columns if col.startswith('C360 ')]
        target_cols = [col for col in download_df.columns if col.startswith('Target Data ')]

        # Remove any technical columns if they exist
        if 'Target_Match_Type' in download_df.columns:
            download_df = download_df.drop(['Target_Match_Type'], axis=1)
        if 'Target_Value' in download_df.columns:
            download_df = download_df.drop(['Target_Value'], axis=1)

        # Add blank separator column with a space as the name
        download_df.insert(len(c360_cols), ' ', [''] * len(download_df))

        # Create final column order
        final_columns = c360_cols + [' '] + target_cols + ['Match Score (%)']

        # Reorder columns using only existing columns
        download_df = download_df[final_columns]

    buffer = io.BytesIO()

    # Create Excel writer object with xlsxwriter engine
    writer = pd.ExcelWriter(buffer, engine='xlsxwriter')
    download_df.to_excel(writer, sheet_name='Summary', index=False)
    workbook = writer.book
    worksheet = writer.sheets['Summary']

    # Define formats
    header_format = workbook.add_format({
        'bg_color': '#00FFFF',  # Cyan color for headers
        'bold': True,
        'text_wrap': True,
        'valign': 'vcenter',
        'align': 'center'
    })

    separator_format = workbook.add_format({
        'bg_color': '#ADD8E6',  # Light blue color for separator
        'text_wrap': True,
        'valign':'vcenter',
        'align': 'center'
    })

    # Set column widths and formats
    for idx, column in enumerate(download_df.columns):
        if column == ' ':  # Separator column
            worksheet.set_column(idx, idx, 5, separator_format)  # Narrower width for separator
        else:
            worksheet.set_column(idx, idx, 30)  # Fixed width of 30 for all other columns

    # Apply header format to the first row
    for col_num, value in enumerate(download_df.columns):
        worksheet.write(0, col_num, value, header_format)

    writer.close()

    b64 = base64.b64encode(buffer.getvalue()).decode()
    mime_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    download_link = f'<a href="data:{mime_type};base64,{b64}" download="{file_name}.xlsx" class="download-button">{button_text}</a>'
    return download_link


def show_code_analysis():
    """Display code analysis interface"""
    st.title("🔍 CodeLens")
    st.markdown("### Code Analysis Utility")

# Initialize repo_path
    repo_path = None

    # Input method selection
    input_method = st.sidebar.radio(
        "Choose Input Method",
        ["Upload Files", "Repository Path"]
    )

    # Application name input
    app_name = st.sidebar.text_input("Application Name", "MyApp")

    analysis_triggered = False
    temp_dir = None

    if input_method == "Upload Files":
        uploaded_files = st.sidebar.file_uploader(
            "Upload Code Files",
            accept_multiple_files=True,
            type=['py','java', 'js', 'ts', 'cs', 'php', 'rb', 'xsd']
        )

        if uploaded_files:
            temp_dir = tempfile.mkdtemp()
            for uploaded_file in uploaded_files:
                file_path = os.path.join(temp_dir, uploaded_file.name)  # Fix variable name
                with open(file_path, 'wb') as f:
                    f.write(uploaded_file.getbuffer())

            if st.sidebar.button("Run Analysis"):
                analysis_triggered = True
                repo_path = temp_dir

    else:
        repo_path = st.sidebar.text_input("Enter Repository Path")
        if repo_path and st.sidebar.button("Run Analysis"):
            analysis_triggered = True

    if analysis_triggered:
        try:
            # Validate repo_path before starting analysis
            if not repo_path:
                st.error("Repository path is not set. Please select files or enter a path.")
                return

            st.info(f"Starting analysis with repository path: {repo_path}")

            with st.spinner("Analyzing code..."):
                analyzer = CodeAnalyzer(repo_path, app_name)
                progress_bar = st.progress(0)

                # Run analysis
                results = analyzer.scan_repository()
                progress_bar.progress(100)

                # Create tabs for Dashboard, Analysis Results, Export Reports, and Logs
                tab1, tab2, tab3, tab4 = st.tabs(["Dashboard", "Analysis Results", "Export Reports", "Log"])

                with tab1:
                    st.header("Analysis Dashboard")
                    st.markdown("""
                    This dashboard provides visual insights into the code analysis results,
                    showing distributions of files, demographic fields, and integration patterns.
                    """)
                    create_dashboard_charts(results)

                with tab2:
                    # Summary Stats
                    st.subheader("Summary")
                    stats_cols = st.columns(4)
                    stats_cols[0].metric("Files Analyzed", results['summary']['files_analyzed'])
                    stats_cols[1].metric("Demographic Fields", results['summary']['demographic_fields_found'])
                    stats_cols[2].metric("Integration Patterns", results['summary']['integration_patterns_found'])
                    stats_cols[3].metric("Unique Fields", len(results['summary']['unique_demographic_fields']))

                    # Demographic Fields Summary Table
                    st.subheader("Demographic Fields Summary")
                    demographic_files = [f for f in results['summary']['file_details'] if f['demographic_fields_found'] > 0]
                    if demographic_files:
                        cols = st.columns([0.5, 2, 1, 2])
                        cols[0].markdown("**#**")
                        cols[1].markdown("**File Analyzed**")
                        cols[2].markdown("**Fields Found**")
                        cols[3].markdown("**Fields**")

                        for idx, file_detail in enumerate(demographic_files, 1):
                            file_path = file_detail['file_path']
                            unique_fields = []
                            if file_path in results['demographic_data']:
                                unique_fields = list(results['demographic_data'][file_path].keys())

                            cols = st.columns([0.5, 2, 1, 2])
                            cols[0].text(str(idx))
                            cols[1].text(os.path.basename(file_path))
                            cols[2].text(str(file_detail['demographic_fields_found']))
                            cols[3].text(', '.join(unique_fields))

                    # Integration Patterns Summary Table
                    st.subheader("Integration Patterns Summary")
                    integration_files = [f for f in results['summary']['file_details'] if f['integration_patterns_found'] > 0]
                    if integration_files:
                        cols = st.columns([0.5, 2, 1, 2])
                        cols[0].markdown("**#**")
                        cols[1].markdown("**File Name**")
                        cols[2].markdown("**Patterns Found**")
                        cols[3].markdown("**Pattern Details**")

                        for idx, file_detail in enumerate(integration_files, 1):
                            file_path = file_detail['file_path']
                            pattern_details = set()
                            for pattern in results['integration_patterns']:
                                if pattern['file_path'] == file_path:
                                    pattern_details.add(f"{pattern['pattern_type']}: {pattern['sub_type']}")

                            cols = st.columns([0.5, 2, 1, 2])
                            cols[0].text(str(idx))
                            cols[1].text(os.path.basename(file_path))
                            cols[2].text(str(file_detail['integration_patterns_found']))
                            cols[3].text(', '.join(pattern_details))

                with tab3:
                    st.header("Available Reports")

                    # Get all report files and filter by app_name
                    report_files = [
                        f for f in os.listdir()
                        if f.endswith('.html')
                        and 'CodeLens' in f
                        and f.startswith(app_name)
                    ]

                    # Sort files by timestamp in descending order
                    report_files.sort(key=parse_timestamp_from_filename, reverse=True)

                    if report_files:
                        # Create a table with five columns
                        cols = st.columns([1, 3, 2, 2, 2])
                        cols[0].markdown("**S.No**")
                        cols[1].markdown("**File Name**")
                        cols[2].markdown("**Date**")
                        cols[3].markdown("**Time**")
                        cols[4].markdown("**Download**")

                        # List all reports
                        for idx, report_file in enumerate(report_files, 1):
                            cols = st.columns([1, 3, 2, 2, 2])

                            # Serial number column
                            cols[0].text(f"{idx}")

                            # File name column without .html extension
                            display_name = report_file.replace('.html', '')
                            cols[1].text(display_name)

                            # Extract timestamp and format date and time separately
                            timestamp = parse_timestamp_from_filename(report_file)
                            # Date in DD-MMM-YYYY format
                            cols[2].text(timestamp.strftime('%d-%b-%Y'))
                            # Time in 12-hour format with AM/PM
                            cols[3].text(timestamp.strftime('%I:%M:%S %p'))

                            # Download button column (last)
                            cols[4].markdown(
                                get_file_download_link(report_file),
                                unsafe_allow_html=True
                            )
                    else:
                        st.info("No reports available for this application.")

                with tab4:
                    st.header("Analysis Log")
                    # Add auto-refresh checkbox
                    auto_refresh = st.checkbox("Auto-refresh logs", value=True)

                    # Create a container for logs
                    log_container = st.empty()

                    def update_logs():
                        logs = read_log_file()
                        if logs:
                            log_content = "".join(logs)
                            log_container.code(log_content, language="text")
                        else:
                            log_container.info("No logs available")

                    # Initial log display
                    update_logs()

                    # Auto-refresh logs every 5 seconds if enabled
                    if auto_refresh:
                        while True:
                            time.sleep(5)
                            update_logs()

        except Exception as e:
            st.error(f"Error during analysis: {str(e)}")

        finally:
            if temp_dir:
                import shutil
                shutil.rmtree(temp_dir)

def create_dashboard_charts(results):
    """Create visualization charts for the dashboard"""
    # Summary Stats at the top
    st.subheader("Summary")
    stats_cols = st.columns(4)
    stats_cols[0].metric("Files Analyzed", results['summary']['files_analyzed'])
    stats_cols[1].metric("Demographic Fields", results['summary']['demographic_fields_found'])
    stats_cols[2].metric("Integration Patterns", results['summary']['integration_patterns_found'])
    stats_cols[3].metric("Unique Fields", len(results['summary']['unique_demographic_fields']))

    st.markdown("----")  # Add a separator line

    # 1. Demographic Fields Distribution
    field_frequencies = {}
    for file_data in results['demographic_data'].values():
        for field_name, data in file_data.items():
            if field_name not in field_frequencies:
                field_frequencies[field_name] = len(data['occurrences'])
            else:
                field_frequencies[field_name] += len(data['occurrences'])

    # Create DataFrame for Plotly charts
    df_demographics = pd.DataFrame({
        'Field_Name': list(field_frequencies.keys()),
        'Count': list(field_frequencies.values())    })

    # Create two columns for side-by-side charts
    col1, col2= st.columns(2)

    with col1:
        # Pie Chart
        fig_demo_pie = px.pie(
            df_demographics,
            values='Count',
            names='Field_Name',
            title="Distribution of Demographic Fields (Pie Chart)",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        st.plotly_chart(fig_demo_pie, use_container_width=True)

    with col2:
        # Bar Chart
        fig_demo_bar = px.bar(
            df_demographics,
            x='Field_Name',
            y='Count',
            title="Distribution of Demographic Fields (Bar Chart)",
            color='Field_Name',
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig_demo_bar.update_layout(showlegend=False)
        st.plotly_chart(fig_demo_bar, use_container_width=True)

    # 2. Files by Language Bar Chart
    file_extensions = [Path(file['file_path']).suffix for file in results['summary']['file_details']]
    df_files = pd.DataFrame({
        'Extension': file_extensions,
        'Count': [1] * len(file_extensions)
    }).groupby('Extension').count().reset_index()

    fig_files = px.bar(
        df_files,
        x='Extension',
        y='Count',
        title="Files by Language",
        color='Extension',
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig_files.update_layout(showlegend=False)
    st.plotly_chart(fig_files)

    # Create visualization for pattern types distribution
    st.subheader("Integration Patterns Distribution")
    pattern_counts = Counter(pattern['pattern_type'] for pattern in results['integration_patterns'])
    df_patterns = pd.DataFrame({
        'Pattern_Type': list(pattern_counts.keys()),
        'Count': list(pattern_counts.values())
    })

    fig_patterns = px.bar(
        df_patterns,
        x='Pattern_Type',
        y='Count',
        title="Integration Patterns Distribution",
        color='Pattern_Type',
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig_patterns.update_layout(showlegend=False)
    st.plotly_chart(fig_patterns, use_container_width=True)

    # Files and Fields Correlation
    st.subheader("Files and Fields Correlation")
    df_correlation = pd.DataFrame({
        'File_Name': [os.path.basename(detail['file_path']) for detail in results['summary']['file_details']],
        'Demographic_Fields': [detail['demographic_fields_found'] for detail in results['summary']['file_details']],
        'Integration_Patterns': [detail['integration_patterns_found'] for detail in results['summary']['file_details']]
    })

    fig_correlation = px.bar(
        df_correlation,
        x='File_Name',
        y=['Demographic_Fields', 'Integration_Patterns'],
        title="Files and Fields Correlation",
        barmode='group',
        color_discrete_sequence=['#0066cc', '#90EE90']
    )
    st.plotly_chart(fig_correlation, use_container_width=True)

def show_about_page():
    """Display About page with technical stack and team information"""
    st.title("🔍 CodeLens - About")

    # Application Overview
    st.markdown("""
    ### Application Overview
    CodeLens is an advanced data analysis and visualization platform designed to streamline 
    cross-file data exploration and intelligent attribute matching.
    """)

    # Technical Stack
    st.markdown("""
    ### Technical Stack
    #### Core Technologies
    - **Frontend Framework:** Streamlit
    - **Data Processing:** Pandas, NumPy
    - **Visualization:** Plotly
    - **Pattern Matching:** FuzzyWuzzywith Python-Levenshtein
    - **Code Analysis:** Pygments
    
    #### Key Libraries
    - **streamlit:** Interactive web application framework
    - **pandas:** Data manipulation and analysis
    - **plotly:** Interactive data visualization
    - **fuzzywuzzy:** Fuzzy string matching
    - **python-levenshtein:** Fast string comparison
    - **pygments:** Syntax highlighting
    - **openpyxl:** Excel file handling
    
    #### Features
    - Multi-file Excel data analysis
    - Advanced fuzzy matching algorithms
    - Dynamic column comparison
    - Cross-platform path handling
    - Intelligent attribute matching system
    """)

    # Team Information
    st.markdown("""
    ### Design & Development
    
    ❤️ Zensar Project Diamond Team ❤️
    """)


def main():
    # Sidebar navigation
    analysis_type = st.sidebar.radio(
        "Select Analysis Type",
        ["Demographic Analysis", "Code Analysis", "About"]
    )

    if analysis_type == "Demographic Analysis":
        show_demographic_analysis()
    elif analysis_type == "Code Analysis":
        show_code_analysis()
    else:
        show_about_page()

if __name__ == "__main__":
    main()