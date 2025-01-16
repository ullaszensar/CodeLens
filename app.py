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

def create_dashboard_charts(results):
    """Create visualization charts for the dashboard"""
    # Prepare data for visualizations

    # 1. Files by Language Bar Chart
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

    # 2. Demographic Fields Distribution Pie Chart
    field_frequencies = {}
    for file_data in results['demographic_data'].values():
        for field_name, data in file_data.items():
            if field_name not in field_frequencies:
                field_frequencies[field_name] = len(data['occurrences'])
            else:
                field_frequencies[field_name] += len(data['occurrences'])

    fig_demo = px.pie(
        values=list(field_frequencies.values()),
        names=list(field_frequencies.keys()),
        title="Distribution of Demographic Fields",
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    st.plotly_chart(fig_demo)

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
    st.title("🔍 CodeLens")
    st.markdown("### Code Analysis Utility")

    # Sidebar
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

                # Create tabs for Analysis Results, Dashboard, and Export Reports
                tab1, tab2, tab3 = st.tabs(["Analysis Results", "Dashboard", "Export Reports"])

                with tab1:
                    # Summary Stats
                    st.subheader("Summary")
                    stats_cols = st.columns(4)
                    stats_cols[0].metric("Files Analyzed", results['summary']['files_analyzed'])
                    stats_cols[1].metric("Demographic Fields", results['summary']['demographic_fields_found'])
                    stats_cols[2].metric("Integration Patterns", results['summary']['integration_patterns_found'])
                    stats_cols[3].metric("Unique Fields", len(results['summary']['unique_demographic_fields']))

                    # Demographic Data
                    st.subheader("Demographic Data Findings")
                    for file_path, fields in results['demographic_data'].items():
                        with st.expander(f"📄 {os.path.basename(file_path)}"):
                            for field_name, data in fields.items():
                                st.write(f"**Field:** {field_name} ({data['data_type']})")
                                for occurrence in data['occurrences']:
                                    display_code_with_highlights(
                                        occurrence['code_snippet'],
                                        occurrence['line_number'],
                                        file_path
                                    )

                    # Integration Patterns
                    st.subheader("Integration Patterns")
                    for pattern in results['integration_patterns']:
                        with st.expander(f"🔌 {pattern['pattern_type']} - {pattern['sub_type']}"):
                            st.write(f"**File:** {os.path.basename(pattern['file_path'])}")
                            st.write(f"**Line:** {pattern['line_number']}")
                            display_code_with_highlights(
                                pattern['code_snippet'],
                                pattern['line_number'],
                                pattern['file_path']
                            )

                with tab2:
                    st.header("Analysis Dashboard")
                    st.markdown("""
                    This dashboard provides visual insights into the code analysis results,
                    showing distributions of files, demographic fields, and integration patterns.
                    """)
                    create_dashboard_charts(results)

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
                        cols = st.columns([1, 3, 2, 2, 1])
                        cols[0].markdown("**S.No**")
                        cols[1].markdown("**File Name**")
                        cols[2].markdown("**Date**")
                        cols[3].markdown("**Time**")
                        cols[4].markdown("**Download**")

                        # List all reports
                        for idx, report_file in enumerate(report_files, 1):
                            cols = st.columns([1, 3, 2, 2, 1])

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

        except Exception as e:
            st.error(f"Error during analysis: {str(e)}")

        finally:
            if temp_dir:
                import shutil
                shutil.rmtree(temp_dir)

if __name__ == "__main__":
    main()