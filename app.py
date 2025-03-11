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
import zipfile

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


def process_zip_file(zip_file):
    """Process a ZIP file, extracting Java files and returning file contents"""
    try:
        temp_dir = tempfile.mkdtemp()
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)

        java_files = []
        for root, _, files in os.walk(temp_dir):
            for file in files:
                if file.endswith('.java'):
                    file_path = os.path.join(root, file)
                    with open(file_path, 'r') as f:
                        content = f.read()
                    java_files.append({
                        'name': file,
                        'content': content,
                        'path': os.path.relpath(file_path, temp_dir)
                    })
        return java_files
    except Exception as e:
        st.error(f"Error processing ZIP file: {str(e)}")
        return []


def show_code_analysis():
    """Display code analysis interface"""
    st.title("Code Analysis")

    # Application name input in sidebar
    st.sidebar.header("Analysis Settings")
    app_name = st.sidebar.text_input("Application Name", "MyApp")

    # File uploader with drag and drop support
    uploaded_files = st.file_uploader(
        "Upload Java files or ZIP containing project files",
        type=['java', 'zip'],
        accept_multiple_files=True,
        help="Drag and drop files here or click to browse"
    )

    if uploaded_files:
        all_files = []
        for uploaded_file in uploaded_files:
            if uploaded_file.name.endswith('.zip'):
                # Process zip file
                zip_files = process_zip_file(uploaded_file)
                all_files.extend(zip_files)
                st.success(f"Successfully extracted {len(zip_files)} files from {uploaded_file.name}")
            else:
                # Process individual Java file
                content = uploaded_file.getvalue().decode()
                all_files.append({
                    'name': uploaded_file.name,
                    'content': content,
                    'path': uploaded_file.name
                })
                st.success(f"Successfully loaded {uploaded_file.name}")

        if all_files:
            st.markdown("### Repository Structure")

            # Create and display file tree
            file_tree = create_file_tree([file['path'] for file in all_files])
            st.code(file_tree, language='text')

            # Create analyzer instance
            analyzer = CodeAnalyzer()

            # Process each file
            for file in all_files:
                try:
                    analysis_results = analyzer.analyze_file(
                        file['content'],
                        file['name']
                    )

                    st.markdown(f"### Analysis Results for `{file['name']}`")

                    # Display code with syntax highlighting
                    with st.expander("View Code"):
                        display_code_with_highlights(
                            file['content'],
                            analysis_results.get('highlights', [])
                        )

                    # Generate HTML report
                    report_file = f"{app_name}_CodeLens_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
                    analyzer.generate_report(
                        analysis_results,
                        report_file
                    )

                    # Provide download link for report
                    st.markdown(
                        get_file_download_link(report_file),
                        unsafe_allow_html=True
                    )

                except Exception as e:
                    st.error(f"Error analyzing {file['name']}: {str(e)}")
    else:
        st.info("Please upload Java source files or a ZIP archive containing your project")

    # Display logs if available
    logs = read_log_file()
    if logs:
        with st.expander("Analysis Logs"):
            for log in logs:
                st.text(log.strip())


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
    # Main page navigation
    analysis_type = st.sidebar.radio(
        "Select Analysis Type",
        ["Demographic Analysis", "Code Analysis", "About"]
    )

    # Add navigation instructions for new pages
    st.sidebar.markdown("""
    ### Navigation
    Use the pages in the sidebar to access additional tools:
    - Class Diagram Generator
    - API/SOR Analysis
    - Flow Diagram Generator
    """)

    if analysis_type == "Demographic Analysis":
        show_demographic_analysis()
    elif analysis_type == "Code Analysis":
        show_code_analysis()
    else:
        show_about_page()

if __name__ == "__main__":
    main()