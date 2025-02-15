import streamlit as st
import tempfile
import os
from pathlib import Path
import time
from datetime import datetime
from typing import List, Dict, Optional
from collections import Counter

# Custom modules
from codescan import CodeAnalyzer
from utils import display_code_with_highlights, create_file_tree
from styles import apply_custom_styles

# Visualization libraries
import plotly.express as px
import plotly.graph_objects as go
import base64

# Page configuration
st.set_page_config(
    page_title="CodeLens - Code Analysis Utility",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom styles
apply_custom_styles()

def get_file_download_link(file_path: str) -> str:
    """
    Generate an HTML download link for a file

    Args:
        file_path: Path to the file to be downloaded

    Returns:
        HTML string containing the download link with custom styling
    """
    with open(file_path, 'r') as f:
        data = f.read()
    b64 = base64.b64encode(data.encode()).decode()
    filename = os.path.basename(file_path)
    return f'<a href="data:text/html;base64,{b64}" download="{filename}" class="download-button">Download</a>'

def parse_timestamp_from_filename(filename: str) -> datetime:
    """
    Extract timestamp from filename with format app_name_code_analysis_YYYYMMDD_HHMMSS

    Args:
        filename: Name of the file containing timestamp

    Returns:
        datetime object representing the timestamp
    """
    try:
        date_time_str = filename.split('_')[-2] + '_' + filename.split('_')[-1].split('.')[0]
        return datetime.strptime(date_time_str, '%Y%m%d_%H%M%S')
    except:
        return datetime.min

def read_log_file() -> List[str]:
    """
    Read and format the contents of the analysis log file

    Returns:
        List of formatted log lines
    """
    try:
        if os.path.exists('code_analysis.log'):
            with open('code_analysis.log', 'r') as f:
                logs = f.readlines()
            return [log.strip() for log in logs]
        return []
    except Exception as e:
        return [f"Error reading log file: {str(e)}"]

def display_logs():
    """
    Display formatted logs grouped by log level with appropriate icons
    """
    logs = read_log_file()
    if not logs:
        st.info("No logs available yet. Run an analysis to generate logs.")
        return

    # Group logs by level
    log_groups = {
        'error': ('❌', 'Errors', [log for log in logs if 'ERROR' in log]),
        'info': ('ℹ️', 'Information', [log for log in logs if 'INFO' in log]),
        'other': ('📝', 'Other Logs', [log for log in logs if 'ERROR' not in log and 'INFO' not in log])
    }

    # Display each group if it has logs
    for icon, title, group_logs in log_groups.values():
        if group_logs:
            st.subheader(title)
            for log in group_logs:
                st.markdown(f"{icon} {log}")

def create_dashboard_charts(results: Dict):
    """
    Create interactive visualization charts for the analysis dashboard

    Args:
        results: Dictionary containing analysis results
    """
    # Display summary metrics
    metrics = {
        "Files Analyzed": results['summary']['files_analyzed'],
        "Demographic Fields": results['summary']['demographic_fields_found'],
        "Integration Patterns": results['summary']['integration_patterns_found'],
        "Unique Fields": len(results['summary']['unique_demographic_fields'])
    }

    cols = st.columns(len(metrics))
    for col, (label, value) in zip(cols, metrics.items()):
        col.metric(label, value)

    st.markdown("---")

    # Create visualization charts
    col1, col2 = st.columns(2)

    # Field Distribution Charts
    field_frequencies = {}
    for file_data in results['demographic_data'].values():
        for field_name, data in file_data.items():
            field_frequencies[field_name] = field_frequencies.get(field_name, 0) + len(data['occurrences'])

    with col1:
        fig_pie = px.pie(
            values=list(field_frequencies.values()),
            names=list(field_frequencies.keys()),
            title="Distribution of Demographic Fields",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with col2:
        fig_bar = px.bar(
            x=list(field_frequencies.keys()),
            y=list(field_frequencies.values()),
            title="Field Occurrences",
            labels={'x': 'Field Name', 'y': 'Count'},
            color=list(field_frequencies.keys()),
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig_bar.update_layout(showlegend=False)
        st.plotly_chart(fig_bar, use_container_width=True)

    # Language Distribution Chart
    file_extensions = [Path(file['file_path']).suffix for file in results['summary']['file_details']]
    extension_counts = Counter(file_extensions)
    fig_languages = px.bar(
        x=list(extension_counts.keys()),
        y=list(extension_counts.values()),
        title="Files by Programming Language",
        labels={'x': 'Language', 'y': 'Count'},
        color=list(extension_counts.keys()),
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    st.plotly_chart(fig_languages)

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
    """
    Main application function that handles user input and displays analysis results
    """
    st.title("🔍 CodeLens")
    st.markdown("### Advanced Code Analysis Utility")

    # Sidebar configuration
    st.sidebar.header("Analysis Settings")
    input_method = st.sidebar.radio("Choose Input Method", ["Upload Files", "Repository Path"])
    app_name = st.sidebar.text_input("Application Name", "MyApp")

    analysis_triggered = False
    temp_dir = None

    try:
        # Handle file input method
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

        # Handle repository path input method
        else:
            repo_path = st.sidebar.text_input("Enter Repository Path")
            if repo_path and st.sidebar.button("Run Analysis"):
                analysis_triggered = True

        # Perform analysis if triggered
        if analysis_triggered:
            with st.spinner("Analyzing code..."):
                analyzer = CodeAnalyzer(repo_path, app_name)
                progress_bar = st.progress(0)
                results = analyzer.scan_repository()
                progress_bar.progress(100)

                # Display results in tabs
                tab_names = ["Dashboard", "Analysis Results", "Export Reports", "Logs"]
                tabs = st.tabs(tab_names)

                with tabs[0]:  # Dashboard
                    st.header("Analysis Dashboard")
                    create_dashboard_charts(results)

                with tabs[1]:  # Analysis Results
                    st.subheader("Analysis Summary")
                    cols = st.columns(4)
                    cols[0].metric("Files Analyzed", results['summary']['files_analyzed'])
                    cols[1].metric("Demographic Fields", results['summary']['demographic_fields_found'])
                    cols[2].metric("Integration Patterns", results['summary']['integration_patterns_found'])
                    cols[3].metric("Unique Fields", len(results['summary']['unique_demographic_fields']))

                    # Display detailed results
                    st.subheader("Demographic Fields")
                    for file_detail in results['summary']['file_details']:
                        if file_detail['demographic_fields_found'] > 0:
                            st.text(f"File: {file_detail['file_path']}")
                            st.text(f"Fields found: {file_detail['demographic_fields_found']}")

                    st.subheader("Integration Patterns")
                    for file_detail in results['summary']['file_details']:
                        if file_detail['integration_patterns_found'] > 0:
                            st.text(f"File: {file_detail['file_path']}")
                            st.text(f"Patterns found: {file_detail['integration_patterns_found']}")



                with tabs[2]:  # Export Reports
                    st.header("Available Reports")
                    report_files = [
                        f for f in os.listdir()
                        if f.endswith('.html') and 'CodeLens' in f 
                        and f.startswith(app_name)
                    ]

                    if report_files:
                        report_files.sort(key=parse_timestamp_from_filename, reverse=True)
                        for idx, report_file in enumerate(report_files, 1):
                            cols = st.columns([1, 3, 2, 2, 2])
                            timestamp = parse_timestamp_from_filename(report_file)

                            cols[0].text(f"{idx}")
                            cols[1].text(report_file.replace('.html', ''))
                            cols[2].text(timestamp.strftime('%d-%b-%Y'))
                            cols[3].text(timestamp.strftime('%I:%M:%S %p'))
                            cols[4].markdown(get_file_download_link(report_file), unsafe_allow_html=True)
                    else:
                        st.info("No reports available for this application.")

                with tabs[3]:  # Logs
                    st.header("Analysis Logs")
                    st.markdown("""
                    This section shows the detailed logs of the code analysis process, 
                    including information about files being processed and any errors encountered.
                    """)
                    display_logs()

    except Exception as e:
        st.error(f"Error during analysis: {str(e)}")

    finally:
        if temp_dir:
            import shutil
            shutil.rmtree(temp_dir)

if __name__ == "__main__":
    main()