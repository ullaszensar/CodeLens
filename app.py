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
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
import pandas as pd
from fuzzywuzzy import process, fuzz

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

def compare_attributes(df1, df2, algorithm_type, threshold):
    """Compare attributes between two dataframes using fuzzy matching"""
    # Select scoring function based on algorithm type
    if algorithm_type == "Levenshtein Ratio (Basic)":
        scorer = fuzz.ratio
    elif algorithm_type == "Partial Ratio (Substring)":
        scorer = fuzz.partial_ratio
    else:  # Token Sort Ratio
        scorer = fuzz.token_sort_ratio

    matches = []
    for attr1 in df1['attr_name'].unique():
        best_matches = process.extract(
            attr1,
            df2['attr_name'].unique(),
            scorer=scorer,
            limit=3
        )
        for attr2, score in best_matches:
            if score >= threshold:
                matches.append({
                    'Customer_Attribute': attr1,
                    'Meta_Attribute': attr2,
                    'Similarity_Score': score
                })

    return pd.DataFrame(matches)

def show_demographic_analysis():
    """Display demographic data analysis interface"""
    st.title("🔍 CodeLens")
    st.markdown("### Demographic Data Analysis")

    # Application name input in sidebar
    st.sidebar.header("Analysis Settings")
    app_name = st.sidebar.text_input("Application Name", "MyApp")

    # Main content area with two columns
    col1, col2 = st.columns(2)

    # First Excel Upload - Customer Demographic
    with col1:
        st.subheader("1. Customer Demographic Data")
        customer_demo_file = st.file_uploader(
            "Upload Customer Demographic Excel",
            type=['xlsx', 'xls'],
            key='customer_demo'
        )

        if customer_demo_file is not None:
            try:
                df_customer = pd.read_excel(customer_demo_file)
                st.success("✅ Customer Demographic file loaded successfully")

                # Display summary
                st.markdown("**File Summary:**")
                summary_cols = st.columns(2)
                summary_cols[0].metric("Total Rows", len(df_customer))
                summary_cols[1].metric("Total Columns", len(df_customer.columns))

                # Display data overview
                st.markdown("**Data Preview:**")
                st.dataframe(df_customer.head(5))

            except Exception as e:
                st.error(f"Error loading customer demographic file: {str(e)}")

    # Second Excel Upload - Meta Data
    with col2:
        st.subheader("2. Meta Data")
        meta_data_file = st.file_uploader(
            "Upload Meta Data Excel",
            type=['xlsx', 'xls'],
            key='meta_data'
        )

        if meta_data_file is not None:
            try:
                df_meta = pd.read_excel(meta_data_file)
                st.success("✅ Meta Data file loaded successfully")

                # Display summary
                st.markdown("**File Summary:**")
                summary_cols = st.columns(2)
                summary_cols[0].metric("Total Rows", len(df_meta))
                summary_cols[1].metric("Total Columns", len(df_meta.columns))

                # Display data overview
                st.markdown("**Data Preview:**")
                st.dataframe(df_meta.head(5))

            except Exception as e:
                st.error(f"Error loading meta data file: {str(e)}")

    # Table name filter with fuzzy search
    st.markdown("### Filter Meta Data by Table Name")
    if meta_data_file is not None:
        # Fuzzy search settings
        st.markdown("#### Search Settings")
        col1, col2 = st.columns(2)

        with col1:
            # Algorithm selection
            algorithm = st.selectbox(
                "Select Fuzzy Matching Algorithm",
                [
                    "Levenshtein Ratio (Basic)",
                    "Partial Ratio (Substring)",
                    "Token Sort Ratio (Word Order)"
                ],
                key="table_algorithm"
            )

        with col2:
            # Similarity threshold
            threshold = st.slider(
                "Similarity Threshold (%)",
                min_value=0,
                max_value=100,
                value=60,
                help="Minimum similarity score required for a match",
                key="table_threshold"
            )

        # Search input
        table_name = st.text_input("Enter Table Name to Filter:", "")

        filtered_data = None
        if table_name:
            try:
                # Get unique table names
                unique_tables = df_meta['table_name'].unique()

                # Select scoring function based on algorithm choice
                if algorithm == "Levenshtein Ratio (Basic)":
                    scorer = fuzz.ratio
                    algorithm_description = """
                    **Levenshtein Ratio:** Calculates the minimum number of character edits required to transform one string into another.
                    Best for exact matches with minor typos.
                    """
                elif algorithm == "Partial Ratio (Substring)":
                    scorer = fuzz.partial_ratio
                    algorithm_description = """
                    **Partial Ratio:** Finds the best matching substring, useful when the search term is a part of the full table name.
                    Best for partial matches and substrings.
                    """
                else:  # Token Sort Ratio
                    scorer = fuzz.token_sort_ratio
                    algorithm_description = """
                    **Token Sort Ratio:** Sorts the words in both strings before comparing, making it order-independent.
                    Best for matching strings with the same words in different orders.
                    """

                # Display algorithm description
                st.markdown(algorithm_description)

                # Perform fuzzy matching
                matches = process.extract(
                    table_name,
                    unique_tables,
                    scorer=scorer,
                    limit=5
                )

                # Filter matches above threshold
                good_matches = [match for match in matches if match[1] >= threshold]

                if good_matches:
                    # Display matches with scores
                    st.markdown("**Matching Tables Found:**")
                    for match, score in good_matches:
                        st.markdown(f"- {match} (Similarity: {score}%)")

                    # Filter and display data
                    matched_tables = [match[0] for match in good_matches]
                    filtered_data = df_meta[df_meta['table_name'].isin(matched_tables)]

                    if len(filtered_data) > 0:
                        st.markdown(f"**Filtered Results:**")
                        st.dataframe(filtered_data)
                    else:
                        st.warning("No data found for the matched table names")
                else:
                    st.warning(f"No similar table names found for: {table_name} (threshold: {threshold}%)")
            except Exception as e:
                st.error(f"Error filtering data: {str(e)}")

        # Attribute comparison section
        if filtered_data is not None and customer_demo_file is not None:
            st.markdown("### Compare Attributes")
            st.markdown("#### Attribute Matching Settings")

            # Algorithm selection for attribute matching
            col1, col2 = st.columns(2)
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
                attr_threshold = st.slider(
                    "Attribute Similarity Threshold (%)",
                    min_value=0,
                    max_value=100,
                    value=60,
                    help="Minimum similarity score required for attribute matches",
                    key="attr_threshold"
                )

            # Compare attributes
            attribute_matches = compare_attributes(
                df_customer, #Corrected order of dataframes
                filtered_data, #Corrected order of dataframes
                attr_algorithm,
                attr_threshold
            )

            if not attribute_matches.empty:
                st.markdown("#### Matching Attributes")
                st.dataframe(
                    attribute_matches.sort_values('Similarity_Score', ascending=False),
                    hide_index=True
                )
            else:
                st.info("No matching attributes found with the current threshold")

    else:
        st.info("Please upload Meta Data file to use the filter functionality")


def show_code_analysis():
    """Display code analysis interface"""
    st.title("🔍 CodeLens")
    st.markdown("### Code Analysis Utility")

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

    # 1. Demographic Fields Distribution - Side by side charts
    field_frequencies = {}
    for file_data in results['demographic_data'].values():
        for field_name, data in file_data.items():
            if field_name not in field_frequencies:
                field_frequencies[field_name] = len(data['occurrences'])
            else:
                field_frequencies[field_name] += len(data['occurrences'])

    # Create two columns for side-by-side charts
    col1, col2 = st.columns(2)

    with col1:
        # Pie Chart
        fig_demo_pie = px.pie(
            values=list(field_frequencies.values()),
            names=list(field_frequencies.keys()),
            title="Distribution of Demographic Fields (Pie Chart)",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        st.plotly_chart(fig_demo_pie, use_container_width=True)

    with col2:
        # Bar Chart
        fig_demo_bar = px.bar(
            x=list(field_frequencies.keys()),
            y=list(field_frequencies.values()),
            title="Distribution of Demographic Fields (Bar Chart)",
            labels={'x': 'Field Name', 'y': 'Occurrences'},
            color=list(field_frequencies.keys()),
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig_demo_bar.update_layout(showlegend=False)
        st.plotly_chart(fig_demo_bar, use_container_width=True)

    # 2. Files by Language Bar Chart
    file_extensions = [Path(file['file_path']).suffix for file in results['summary']['file_details']]
    file_counts = Counter(file_extensions)

    fig_files = px.bar(
        x=list(file_counts.keys()),
        y=list(file_counts.values()),
        title="Files by Language",
        labels={'x': 'File Extension', 'y': 'Count'},
        color=list(file_counts.keys()),
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig_files.update_layout(showlegend=False)
    st.plotly_chart(fig_files)

    # 3. Integration Patterns Line Graph
    pattern_types = Counter(pattern['pattern_type'] for pattern in results['integration_patterns'])

    fig_patterns = go.Figure()
    fig_patterns.add_trace(go.Scatter(
        x=list(pattern_types.keys()),
        y=list(pattern_types.values()),
        mode='lines+markers',
        name='Pattern Count',
        line=dict(color='#0066cc', width=2),
        marker=dict(size=10)
    ))
    fig_patterns.update_layout(
        title="Integration Patterns Distribution",
        xaxis_title="Pattern Type",
        yaxis_title="Count",
        showlegend=False
    )
    st.plotly_chart(fig_patterns)

    # 4. Files and Fields Correlation
    fig_correlation = go.Figure()

    # Extract data for each file
    file_names = [os.path.basename(detail['file_path']) for detail in results['summary']['file_details']]
    demographic_counts = [detail['demographic_fields_found'] for detail in results['summary']['file_details']]
    integration_counts = [detail['integration_patterns_found'] for detail in results['summary']['file_details']]

    fig_correlation.add_trace(go.Bar(
        name='Demographic Fields',
        x=file_names,
        y=demographic_counts,
        marker_color='#0066cc'
    ))
    fig_correlation.add_trace(go.Bar(
        name='Integration Patterns',
        x=file_names,
        y=integration_counts,
        marker_color='#90EE90'
    ))

    fig_correlation.update_layout(
        title="Fields and Patterns by File",
        xaxis_title="File Name",
        yaxis_title="Count",
        barmode='group'
    )
    st.plotly_chart(fig_correlation)


def main():
    # Sidebar navigation
    analysis_type = st.sidebar.radio(
        "Select Analysis Type",
        ["Code Analysis", "Demographic Data Analysis"]
    )

    if analysis_type == "Code Analysis":
        show_code_analysis()
    else:
        show_demographic_analysis()

if __name__ == "__main__":
    main()