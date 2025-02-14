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
from rapidfuzz import fuzz, process
from io import BytesIO

# Page config
st.set_page_config(
    page_title="CodeLens - Code Analysis Platform",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom styles
apply_custom_styles()

# App Description and Benefits
st.sidebar.markdown("""
### Key Benefits:

• **Time-Saving Analysis**
  - Scan multiple code files instantly
  - Find data patterns automatically
  - Quick identification of integration points

• **Enhanced Code Understanding**
  - Visual insights into code structure
  - Clear view of data flow patterns
  - Easy tracking of API integrations

• **Smart Excel Comparison**
  - Compare Excel files intelligently
  - Find matching columns automatically
  - Identify data discrepancies quickly

• **Better Documentation**
  - Auto-generate detailed reports
  - Track findings systematically
  - Export results in multiple formats

• **Integration Detection**
  - Find API endpoints automatically
  - Identify database connections
  - Spot messaging system usage
""")

# Creator information in sidebar footer
st.sidebar.markdown("""
---
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
        date_time_str = filename.split('_')[-2] + '_' + filename.split('_')[-1].split('.')[0]
        return datetime.strptime(date_time_str, '%Y%m%d_%H%M%S')
    except:
        return datetime.min

# Excel Analysis Functions
def load_excel_file(uploaded_file):
    """Load Excel file and return DataFrame"""
    try:
        return pd.read_excel(uploaded_file)
    except Exception as e:
        st.error(f"Error loading Excel file: {str(e)}")
        return None

def fuzzy_match_columns(df1, df2, threshold=80):
    """Match columns between two DataFrames using fuzzy matching"""
    matches = []
    for col1 in df1.columns:
        match = process.extractOne(col1, df2.columns, scorer=fuzz.ratio)
        if match and match[1] >= threshold:
            matches.append((col1, match[0], match[1]))
    return matches

def compare_dataframes(df1, df2, matched_columns):
    """Compare two DataFrames based on matched columns"""
    comparison_results = []

    for col1, col2, score in matched_columns:
        # Get basic statistics
        stats1 = df1[col1].describe()
        stats2 = df2[col2].describe()

        # Calculate differences
        differences = {
            'column_1': col1,
            'column_2': col2,
            'match_score': score,
            'unique_values_1': df1[col1].nunique(),
            'unique_values_2': df2[col2].nunique(),
            'null_count_1': df1[col1].isnull().sum(),
            'null_count_2': df2[col2].isnull().sum(),
        }
        comparison_results.append(differences)

    return pd.DataFrame(comparison_results)

def display_excel_analysis():
    st.title("📊 Excel File Analysis")

    # Sidebar settings
    st.sidebar.header("Excel Analysis Settings")
    match_threshold = st.sidebar.slider(
        "Column Matching Threshold",
        min_value=50,
        max_value=100,
        value=80,
        help="Minimum similarity score (%) for matching columns"
    )

    # File upload section
    st.subheader("Upload Excel Files")
    col1, col2 = st.columns(2)

    with col1:
        file1 = st.file_uploader("Upload First Excel File", type=['xlsx', 'xls'])
        if file1:
            df1 = load_excel_file(file1)
            if df1 is not None:
                st.success(f"File 1 loaded: {df1.shape[0]} rows, {df1.shape[1]} columns")
                st.dataframe(df1.head(), use_container_width=True)

    with col2:
        file2 = st.file_uploader("Upload Second Excel File", type=['xlsx', 'xls'])
        if file2:
            df2 = load_excel_file(file2)
            if df2 is not None:
                st.success(f"File 2 loaded: {df2.shape[0]} rows, {df2.shape[1]} columns")
                st.dataframe(df2.head(), use_container_width=True)

    # Analysis section
    if file1 and file2 and df1 is not None and df2 is not None:
        st.subheader("Column Analysis")

        # Find matching columns
        matches = fuzzy_match_columns(df1, df2, match_threshold)

        # Display matched columns
        st.write("#### Matched Columns")
        if matches:
            match_df = pd.DataFrame(matches, columns=['File 1 Column', 'File 2 Column', 'Match Score'])
            st.dataframe(match_df, use_container_width=True)

            # Compare matched columns
            comparison_results = compare_dataframes(df1, df2, matches)

            st.write("#### Detailed Comparison")
            st.dataframe(comparison_results, use_container_width=True)

            # Export results
            if st.button("Export Analysis Results"):
                # Create Excel file with multiple sheets
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    comparison_results.to_excel(writer, sheet_name='Comparison Results', index=False)
                    match_df.to_excel(writer, sheet_name='Matched Columns', index=False)

                # Offer download
                st.download_button(
                    label="Download Excel Analysis",
                    data=output.getvalue(),
                    file_name="excel_analysis_results.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        else:
            st.warning("No matching columns found with the current threshold")

def create_dashboard_charts(results):
    """Create visualization charts for the dashboard"""
    # Summary Stats at the top
    st.subheader("Summary")
    stats_cols = st.columns(4)
    stats_cols[0].metric("Files Analyzed", results['summary']['files_analyzed'])
    stats_cols[1].metric("Demographic Fields", results['summary']['demographic_fields_found'])
    stats_cols[2].metric("Integration Patterns", results['summary']['integration_patterns_found'])
    stats_cols[3].metric("Unique Fields", len(results['summary']['unique_demographic_fields']))

    st.markdown("---")  # Add a separator line

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


def display_analysis_results(results):
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

def display_export_reports(app_name):
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


def display_code_analysis():
    st.title("🔍 Code Analysis")
    st.markdown("### Source Code Analysis Utility")

    # Analysis Settings in sidebar
    st.sidebar.header("Analysis Settings")

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

                # Create tabs for Dashboard, Analysis Results, and Export Reports
                tab1, tab2, tab3 = st.tabs(["Dashboard", "Analysis Results", "Export Reports"])

                with tab1:
                    st.header("Analysis Dashboard")
                    st.markdown("""
                    This dashboard provides visual insights into the code analysis results,
                    showing distributions of files, demographic fields, and integration patterns.
                    """)
                    create_dashboard_charts(results)

                with tab2:
                    display_analysis_results(results)

                with tab3:
                    display_export_reports(app_name)

        except Exception as e:
            st.error(f"Error during analysis: {str(e)}")

        finally:
            if temp_dir:
                import shutil
                shutil.rmtree(temp_dir)

def main():
    # Navigation menu in sidebar
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Select Page", ["Code Analysis", "Excel Analysis"])

    if page == "Code Analysis":
        display_code_analysis()
    else:
        display_excel_analysis()

if __name__ == "__main__":
    main()