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
import io  # Add io import for BytesIO
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
import pandas as pd
from fuzzywuzzy import process, fuzz
import re

# Page config
st.set_page_config(
    page_title="CodeLens - Code Utility",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom styles
apply_custom_styles()

# Creator information
st.sidebar.markdown("""
### Created by:
**Zensar Project Diamond Team**
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
        meta_values = df2['business_name'].dropna().unique()
    elif match_type == "Attribute Description":
        customer_values = df1['attr_description'].dropna().unique()
        meta_values = df2['attr_description'].dropna().unique()
    else:  # Default to Attribute Name
        customer_values = df1['attr_name'].dropna().unique()
        meta_values = df2['attr_name'].dropna().unique()

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

        customer_record = df1[df1[customer_value_field] == customer_value].iloc[0]

        # Get top matches from meta data
        value_matches = process.extract(
            customer_value,
            meta_values,
            scorer=scorer,
            limit=3
        )

        # Add matches that meet the threshold
        for meta_value, score in value_matches:
            if score >= threshold:
                meta_record = df2[df2[customer_value_field] == meta_value].iloc[0]

                match_entry = {
                    f'C360 {display_field}': customer_value,
                    f'Meta Data {display_field}': meta_value,
                    'Meta_Match_Type': match_type,
                    'Meta_Value': meta_value,
                    'Match Score (%)': score
                }

                matches.append(match_entry)

    # Create DataFrame and sort by match score
    df_matches = pd.DataFrame(matches)
    if not df_matches.empty:
        # Sort by match score
        df_matches = df_matches.sort_values('Match Score (%)', ascending=False)

    return df_matches

def preprocess_meta_data(df):
    """Preprocess meta data by removing rows with integer-only descriptions or pattern matching syntax"""
    initial_rows = len(df)
    removed_rows = {
        'integer_description': 0,
        'pattern_matching': 0
    }

    # Copy dataframe to avoid modifying original
    processed_df = df.copy()

    # Check description fields for integer-only content
    desc_columns = [col for col in processed_df.columns if 'description' in col.lower()]
    if desc_columns:
        for col in desc_columns:
            integer_mask = processed_df[col].astype(str).str.match(r'^\d+$')
            if integer_mask.any():
                print(f"Found {integer_mask.sum()} rows with integer-only content in column '{col}'")
                removed_rows['integer_description'] += integer_mask.sum()
                processed_df = processed_df[~integer_mask]

    # Check for pattern matching syntax in any column
    pattern_chars = r'[\^\$\*\+\?\{\}\[\]\(\)\|\\]'
    for column in processed_df.columns:
        pattern_mask = processed_df[column].astype(str).str.contains(pattern_chars, regex=True)
        if pattern_mask.any():
            print(f"Found {pattern_mask.sum()} rows with pattern matching syntax in column '{column}'")
            removed_rows['pattern_matching'] += pattern_mask.sum()
            processed_df = processed_df[~pattern_mask]

    # Calculate total rows removed
    total_removed = initial_rows - len(processed_df)
    print(f"\nPreprocessing Summary for Meta Data:")
    print(f"Initial rows: {initial_rows}")
    print(f"Rows removed due to integer-only descriptions: {removed_rows['integer_description']}")
    print(f"Rows removed due to pattern matching syntax: {removed_rows['pattern_matching']}")
    print(f"Final rows: {len(processed_df)}")

    return processed_df, {
        'initial_rows': initial_rows,
        'final_rows': len(processed_df),
        'total_removed': total_removed,
        'details': removed_rows
    }

def preprocess_customer_data(df):
    """Preprocess customer data by removing rows with integer-only descriptions or pattern matching syntax"""
    initial_rows = len(df)
    removed_rows = {
        'integer_description': 0,
        'pattern_matching': 0
    }

    # Copy dataframe to avoid modifying original
    processed_df = df.copy()

    # Check description fields for integer-only content
    desc_columns = [col for col in processed_df.columns if 'description' in col.lower()]
    if desc_columns:
        for col in desc_columns:
            integer_mask = processed_df[col].astype(str).str.match(r'^\d+$')
            if integer_mask.any():
                print(f"Found {integer_mask.sum()} rows with integer-only content in column '{col}'")
                removed_rows['integer_description'] += integer_mask.sum()
                processed_df = processed_df[~integer_mask]

    # Check for pattern matching syntax in any column
    pattern_chars = r'[\^\$\*\+\?\{\}\[\]\(\)\|\\]'
    for column in processed_df.columns:
        pattern_mask = processed_df[column].astype(str).str.contains(pattern_chars, regex=True)
        if pattern_mask.any():
            print(f"Found {pattern_mask.sum()} rows with pattern matching syntax in column '{column}'")
            removed_rows['pattern_matching'] += pattern_mask.sum()
            processed_df = processed_df[~pattern_mask]

    # Calculate total rows removed
    total_removed = initial_rows - len(processed_df)
    print(f"\nPreprocessing Summary for Customer Data:")
    print(f"Initial rows: {initial_rows}")
    print(f"Rows removed due to integer-only descriptions: {removed_rows['integer_description']}")
    print(f"Rows removed due to pattern matching syntax: {removed_rows['pattern_matching']}")
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

    # Pattern matching regex
    pattern_chars = r'[\^\$\*\+\?\{\}\[\]\(\)\|\\]'

    # Check each removed row
    for idx in removed_indices:
        row = original_df.loc[idx]
        reason = []

        # Check for integer-only description
        desc_columns = [col for col in row.index if 'description' in col.lower()]
        if desc_columns:
            for col in desc_columns:
                if str(row[col]).isdigit():
                    reason.append(f"Integer-only description in column '{col}'")

        # Check for pattern matching syntax
        for col in row.index:
            if pd.notna(row[col]) and re.search(pattern_chars, str(row[col])):
                reason.append(f"Pattern matching syntax in column '{col}'")

        # Add row to data with detailed reason
        if reason:
            removed_rows_data.append({
                'Original Row Number': idx + 1,
                'Removal Reason': ' & '.join(reason),
                **row.to_dict()
            })
            print(f"Row {idx + 1} removed: {' & '.join(reason)}")

    # Create DataFrame
    removed_df = pd.DataFrame(removed_rows_data)
    return removed_df


def show_demographic_analysis():
    """Display demographic data analysis interface"""
    st.title("🔍 CodeLens")
    st.markdown("### C360 Demographic & Meta Data Analysis")

    # Application name input in sidebar
    st.sidebar.header("Analysis Settings")
    app_name = st.sidebar.text_input("Application Name", "MyApp")

    # Initialize session state for dataframes if not present
    if 'df_customer' not in st.session_state:
        st.session_state.df_customer = None
    if 'df_meta' not in st.session_state:
        st.session_state.df_meta = None
    if 'meta_preprocessing_stats' not in st.session_state:
        st.session_state.meta_preprocessing_stats = None
    if 'customer_preprocessing_stats' not in st.session_state:
        st.session_state.customer_preprocessing_stats = None

    # Main content area with two columns
    col1, col2 = st.columns(2)

    # First Excel Upload - Customer Demographic
    with col1:
        st.subheader("1. Customer Demographic Data")
        st.markdown("---")  # Add separator

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
                st.success("✅ Customer Demographic file loaded successfully")

                st.markdown("---")  # Add separator

                # File Summary
                st.markdown("**File Summary:**")
                summary_cols = st.columns(2)
                with summary_cols[0]:
                    st.metric("Total Rows", len(st.session_state.df_customer))
                with summary_cols[1]:
                    st.metric("Total Columns", len(st.session_state.df_customer.columns))

                st.markdown("---")  # Add separator

                # Preprocessing Summary
                st.markdown("**Preprocessing Summary:**")
                preprocessing_cols = st.columns(3)
                with preprocessing_cols[0]:
                    st.metric("Initial Rows", st.session_state.customer_preprocessing_stats['initial_rows'])
                with preprocessing_cols[1]:
                    st.metric("Rows Removed", st.session_state.customer_preprocessing_stats['total_removed'])
                with preprocessing_cols[2]:
                    st.metric("Final Rows", st.session_state.customer_preprocessing_stats['final_rows'])

                st.markdown("---")  # Add separator

                # Download buttons in a container
                with st.container():
                    download_cols = st.columns(2)
                    with download_cols[0]:
                        st.markdown(
                            download_dataframe(
                                st.session_state.df_customer,
                                "customer_demographic",
                                "excel",
                                button_text="Download Customer Data"
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
                                button_text="Customer Data Removed Rows"
                            ),
                            unsafe_allow_html=True
                        )

                # Data Preview
                st.markdown("**Data Preview:**")
                st.dataframe(st.session_state.df_customer.head(5), use_container_width=True)

            except Exception as e:
                st.error(f"Error loading customer demographic file: {str(e)}")

    # Second Excel Upload - Meta Data
    with col2:
        st.subheader("2. Meta Data")
        st.markdown("---")  # Add separator

        # Add container for file upload
        with st.container():
            meta_data_file = st.file_uploader(
                "Upload Meta Data Excel",
                type=['xlsx', 'xls'],
                key='meta_data'
            )

        if meta_data_file is not None:
            try:
                raw_df_meta = pd.read_excel(meta_data_file)
                st.session_state.df_meta, st.session_state.meta_preprocessing_stats = preprocess_meta_data(raw_df_meta)
                st.success("✅ Meta Data file loaded and preprocessed successfully")

                st.markdown("---")  # Add separator

                # File Summary
                st.markdown("**File Summary:**")
                summary_cols = st.columns(2)
                with summary_cols[0]:
                    st.metric("Total Rows", len(st.session_state.df_meta))
                with summary_cols[1]:
                    st.metric("Total Columns", len(st.session_state.df_meta.columns))

                st.markdown("---")  # Add separator

                # Preprocessing Summary
                st.markdown("**Preprocessing Summary:**")
                preprocessing_cols = st.columns(3)
                with preprocessing_cols[0]:
                    st.metric("Initial Rows", st.session_state.meta_preprocessing_stats['initial_rows'])
                with preprocessing_cols[1]:
                    st.metric("Rows Removed", st.session_state.meta_preprocessing_stats['total_removed'])
                with preprocessing_cols[2]:
                    st.metric("Final Rows", st.session_state.meta_preprocessing_stats['final_rows'])

                st.markdown("---")  # Add separator

                # Download buttons in a container
                with st.container():
                    download_cols = st.columns(2)
                    with download_cols[0]:
                        st.markdown(
                            download_dataframe(
                                st.session_state.df_meta,
                                "meta_data",
                                "excel",
                                button_text="Download Meta Data"
                            ),
                            unsafe_allow_html=True
                        )
                    with download_cols[1]:
                        # Create detailed removed rows DataFrame
                        removed_df = create_removed_rows_df(
                            st.session_state.meta_preprocessing_stats,
                            raw_df_meta,
                            st.session_state.df_meta
                        )
                        st.markdown(
                            download_dataframe(
                                removed_df,
                                "meta_removed_rows",
                                "excel",
                                button_text="Meta Data Removed Rows"
                            ),
                            unsafe_allow_html=True
                        )

                # Data Preview
                st.markdown("**Data Preview:**")
                st.dataframe(st.session_state.df_meta.head(5), use_container_width=True)

            except Exception as e:
                st.error(f"Error loading meta data file: {str(e)}")

    # Attribute comparison section
    if st.session_state.df_meta is not None:
        if st.session_state.df_customer is not None:
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
                        attribute_matches,
                        hide_index=True,
                        height=400,
                        use_container_width=True  # Make the grid full width
                    )

                else:
                    st.info("No matching attributes found with the current threshold")
        else:
            st.info("Please upload Customer Demographic file to compare attributes")
    else:
        st.info("Please upload Meta Data file to use the matching functionality")


def download_dataframe(df, file_name, file_format='excel', button_text="Download", match_type="All"):
    """Generate a download link for a dataframe in Excel format"""
    # Create a descriptive file name based on match type
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    match_type_name = match_type.replace(" ", "_").lower()
    file_name = f"{file_name}_{timestamp}"

    buffer = io.BytesIO()

    # If this is a removed rows file, add extra formatting
    if 'removed' in file_name:
        # Create Excel writer object with xlsxwriter engine
        writer = pd.ExcelWriter(buffer, engine='xlsxwriter')

        # Write the main statistics
        df.to_excel(writer, sheet_name='Summary', index=False)

        # Auto-adjust columns width
        for column in df:
            column_width = max(df[column].astype(str).map(len).max(), len(column))
            col_idx = df.columns.get_loc(column)
            writer.sheets['Summary'].set_column(col_idx, col_idx, column_width + 2)

        writer.close()
    else:
        df.to_excel(buffer, index=False)

    b64 = base64.b64encode(buffer.getvalue()).decode()
    mime_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    download_link = f'<a href="data:{mime_type};base64,{b64}" download="{file_name}.xlsx" class="download-button">{button_text}</a>'
    return download_link

def create_removed_rows_df(preprocessing_stats, original_df, processed_df):
    """Create a detailed DataFrame of removed rows with reasons"""
    # Find indices of removed rows
    original_indices = set(original_df.index)
    kept_indices = set(processed_df.index)
    removed_indices = original_indices - kept_indices

    # Create list to store removed row information
    removed_rows_data = []

    # Pattern matching regex
    pattern_chars = r'[\^\$\*\+\?\{\}\[\]\(\)\|\\]'

    # Check each removed row
    for idx in removed_indices:
        row = original_df.loc[idx]
        reason = []

        # Check for integer-only description
        desc_columns = [col for col in row.index if 'description' in col.lower()]
        if desc_columns:
            for col in desc_columns:
                if str(row[col]).isdigit():
                    reason.append(f"Integer-only description in column '{col}'")

        # Check for pattern matching syntax
        for col in row.index:
            if pd.notna(row[col]) and re.search(pattern_chars, str(row[col])):
                reason.append(f"Pattern matching syntax in column '{col}'")

        # Add row to data with detailed reason
        if reason:
            removed_rows_data.append({
                'Original Row Number': idx + 1,
                'Removal Reason': ' & '.join(reason),
                **row.to_dict()
            })
            print(f"Row {idx + 1} removed: {' & '.join(reason)}")

    # Create DataFrame
    removed_df = pd.DataFrame(removed_rows_data)
    return removed_df


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
            type=['py', 'java', 'js', 'ts', 'cs', 'php', 'rb', 'xsd']
        )

        if uploaded_files:
            temp_dir = tempfile.mkdtemp()
            for uploaded_file in uploaded_files:
                file_path = os.path.join(temp_dir, uploaded_file.name)
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
        'Count': list(field_frequencies.values())
    })

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
        ["Demographic Analysis", "Code Analysis"]
    )

    if analysis_type == "Demographic Analysis":
        show_demographic_analysis()
    else:
        show_code_analysis()

if __name__ == "__main__":
    main()