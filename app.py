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
import pandas as pd
from io import BytesIO
from collections import Counter

# Page config
st.set_page_config(
    page_title="CodeLens - Advanced Code Analysis Platform",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom styles
apply_custom_styles()

# Main title in sidebar
st.sidebar.title("CodeLens")
st.sidebar.markdown("*Advanced Code Analysis Platform*")

# Navigation
st.sidebar.markdown("### Navigation")
page = st.sidebar.radio("", ["Code Analysis", "Demographic Analysis", "About"])

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

def display_demographic_analysis():
    st.title("📊 Demographic Data Analysis")

    # File upload section for main data
    st.subheader("Upload Project File")
    uploaded_file = st.file_uploader("Upload Main Excel File", type=['xlsx', 'xls'], key="primary_file")

    # Second file upload for matching
    st.subheader("Upload Customer C360 File")
    secondary_file = st.file_uploader("Upload Secondary Excel File", type=['xlsx', 'xls'], key="secondary_file")

    if uploaded_file:
        try:
            # Load the primary Excel file
            df = pd.read_excel(uploaded_file)

            # Display original data in a standard table
            st.subheader("Primary Data Preview")
            st.dataframe(
                df,
                height=300,
                use_container_width=True
            )

            # Search interface
            st.subheader("Search Data")
            col1, col2 = st.columns([2, 1])

            with col1:
                search_term = st.text_input("Enter search term")

            with col2:
                # Get column names from the DataFrame
                columns = list(df.columns)
                selected_column = st.selectbox("Select column to search", columns)

            # Filter data based on search criteria
            if search_term and selected_column:
                # Simple case-insensitive string matching
                filtered_df = df[df[selected_column].astype(str).str.contains(search_term, case=False, na=False)]

                st.subheader("Search Results")
                if not filtered_df.empty:
                    st.dataframe(
                        filtered_df,
                        height=300,
                        use_container_width=True
                    )

                    st.info(f"Found {len(filtered_df)} matches")

                    # If secondary file is uploaded, show matching interface
                    if secondary_file is not None:
                        try:
                            # Load secondary file
                            df2 = pd.read_excel(secondary_file)

                            # Check if 'sub Group' exists in both dataframes
                            if 'sub Group' in filtered_df.columns and 'sub Group' in df2.columns:
                                st.subheader("Matching Results with Secondary File")

                                # Get unique sub Group values from filtered results
                                sub_groups = filtered_df['sub Group'].unique()

                                # Find matches in secondary file
                                matches = df2[df2['sub Group'].isin(sub_groups)]

                                if not matches.empty:
                                    st.dataframe(
                                        matches,
                                        height=300,
                                        use_container_width=True
                                    )
                                    st.success(f"Found {len(matches)} matching records in secondary file")

                                    # Export matched results button
                                    output = BytesIO()
                                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                                        matches.to_excel(writer, index=False, sheet_name='Matching Results')

                                    st.download_button(
                                        label="📥 Export Matching Results to Excel",
                                        data=output.getvalue(),
                                        file_name="matching_results.xlsx",
                                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                                    )
                                else:
                                    st.warning("No matching records found in secondary file")
                            else:
                                st.error("'sub Group' column not found in one or both files")
                        except Exception as e:
                            st.error(f"Error processing secondary file: {str(e)}")

                    # Export search results button
                    output = BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        filtered_df.to_excel(writer, index=False, sheet_name='Search Results')

                    st.download_button(
                        label="📥 Export Search Results to Excel",
                        data=output.getvalue(),
                        file_name="search_results.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                else:
                    st.warning("No matches found")

        except Exception as e:
            st.error(f"Error processing file: {str(e)}")


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

    # 1. Demographic Fields Distribution
    field_frequencies = {}
    for file_data in results['demographic_data'].values():
        for field_name, data in file_data.items():
            if field_name not in field_frequencies:
                field_frequencies[field_name] = len(data['occurrences'])
            else:
                field_frequencies[field_name] += len(data['occurrences'])

    # Create DataFrame for charts
    df_frequencies = pd.DataFrame({
        'Field': list(field_frequencies.keys()),
        'Count': list(field_frequencies.values())
    })

    # Create two columns for side-by-side charts
    col1, col2 = st.columns(2)

    with col1:
        # Pie Chart
        fig_demo_pie = px.pie(
            df_frequencies,
            values='Count',
            names='Field',
            title="Distribution of Demographic Fields (Pie Chart)",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        st.plotly_chart(fig_demo_pie, use_container_width=True)

    with col2:
        # Bar Chart
        fig_demo_bar = px.bar(
            df_frequencies,
            x='Field',
            y='Count',
            title="Distribution of Demographic Fields (Bar Chart)",
            color='Field',
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig_demo_bar.update_layout(showlegend=False)
        st.plotly_chart(fig_demo_bar, use_container_width=True)

    # 2. Files by Language Bar Chart
    file_extensions = [Path(file['file_path']).suffix for file in results['summary']['file_details']]
    extension_counts = Counter(file_extensions)
    df_extensions = pd.DataFrame({
        'Extension': list(extension_counts.keys()),
        'Count': list(extension_counts.values())
    })

    fig_files = px.bar(
        df_extensions,
        x='Extension',
        y='Count',
        title="Files by Language",
        color='Extension',
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig_files.update_layout(showlegend=False)
    st.plotly_chart(fig_files)

    # 3. Integration Patterns Line Graph
    pattern_types = Counter(pattern['pattern_type'] for pattern in results['integration_patterns'])
    df_patterns = pd.DataFrame({
        'Pattern': list(pattern_types.keys()),
        'Count': list(pattern_types.values())
    })

    fig_patterns = px.line(
        df_patterns,
        x='Pattern',
        y='Count',
        title="Integration Patterns Distribution",
        markers=True
    )
    fig_patterns.update_traces(line_color='#0066cc', line_width=2)
    st.plotly_chart(fig_patterns)

    # 4. Files and Fields Correlation
    df_correlation = pd.DataFrame({
        'File': [os.path.basename(detail['file_path']) for detail in results['summary']['file_details']],
        'Demographic Fields': [detail['demographic_fields_found'] for detail in results['summary']['file_details']],
        'Integration Patterns': [detail['integration_patterns_found'] for detail in results['summary']['file_details']]
    })

    fig_correlation = px.bar(
        df_correlation,
        x='File',
        y=['Demographic Fields', 'Integration Patterns'],
        title="Fields and Patterns by File",
        barmode='group'
    )
    fig_correlation.update_layout(
        xaxis_title="File Name",
        yaxis_title="Count"
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


def display_logs():
    """Display and provide download link for log files"""
    st.subheader("📋 Analysis Logs")

    # Check if log file exists
    log_file = "code_analysis.log"
    if os.path.exists(log_file):
        # Read log contents
        with open(log_file, 'r') as f:
            log_contents = f.read()

        # Create columns for the log section
        col1, col2 = st.columns([3, 1])

        with col1:
            st.text_area("Log Contents", value=log_contents, height=300, key="log_viewer")

        with col2:
            # Download button for logs
            st.download_button(
                label="📥 Download Logs",
                data=log_contents,
                file_name="code_analysis.log",
                mime="text/plain"
            )

            # Clear logs button
            if st.button("🗑️ Clear Logs"):
                with open(log_file, 'w') as f:
                    f.write("")
                st.experimental_rerun()
    else:
        st.info("No log file found. Run a code analysis to generate logs.")

def display_code_analysis():
    st.title("🔍 Code Analysis")
    st.markdown("### Source Code Analysis Utility")

    # Create tabs for main sections
    tab1, tab2, tab3, tab4 = st.tabs(["Analysis", "Dashboard", "Reports", "Logs"])

    with tab1:
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

                    # Display analysis results
                    display_analysis_results(results)

            except Exception as e:
                st.error(f"Error during analysis: {str(e)}")

            finally:
                if temp_dir:
                    import shutil
                    shutil.rmtree(temp_dir)

    with tab2:
        st.header("Analysis Dashboard")
        st.markdown("""
        This dashboard provides visual insights into the code analysis results,
        showing distributions of files, demographic fields, and integration patterns.
        """)
        if 'results' in locals():
            create_dashboard_charts(results)
        else:
            st.info("Run an analysis to view the dashboard.")

    with tab3:
        if app_name:
            display_export_reports(app_name)
        else:
            st.info("Enter an application name to view available reports.")

    with tab4:
        display_logs()

def display_about_page():
    st.title("ℹ️ About CodeLens")
    st.markdown("### Advanced Code Analysis Platform")

    # Technical Stack Table
    st.subheader("🛠️ Technical Stack")
    tech_stack_data = {
        "Technology": [
            "Streamlit",
            "Pandas",
            "Plotly",
            "Openpyxl",
            "Pygments"
        ],
        "Purpose": [
            "Web application framework for data apps",
            "Data manipulation and analysis",
            "Interactive data visualization",
            "Excel file processing and handling",
            "Code syntax highlighting"
        ],
        "Key Benefits": [
            "Rapid development, interactive UI components",
            "Efficient handling of large datasets",
            "Rich, interactive charts and dashboards",
            "Seamless Excel file operations",
            "Beautiful code presentation"
        ]
    }

    tech_df = pd.DataFrame(tech_stack_data)
    st.table(tech_df)

    # Features Section
    st.subheader("🎯 Key Features")
    features = {
        "Feature": [
            "Code Analysis",
            "Demographic Data Analysis",
            "Excel Data Matching",
            "Interactive Visualizations",
            "Export Capabilities",
            "Pattern Recognition"
        ],
        "Description": [
            "Deep analysis of source code for patterns and integrations",
            "Analysis of demographic data with advanced filtering",
            "Match and compare data between Excel files",
            "Interactive charts and dashboards for data insights",
            "Export results to Excel for further analysis",
            "Regex-based pattern detection for code structure analysis"
        ],
        "Details": [
            "Supports multiple programming languages, identifies integration patterns",
            "Excel file analysis with column-based searching",
            "Match records using 'sub Group' identifiers across files",
            "Powered by Plotly for dynamic, interactive charts",
            "Generate detailed reports in Excel format",
            "Regular expression based pattern detection for demographic data and integration points"
        ]
    }

    features_df = pd.DataFrame(features)
    st.table(features_df)

    # Data Processing Section
    st.subheader("📊 Data Processing Capabilities")
    st.markdown("""
    CodeLens provides advanced data processing capabilities:

    - **Pattern Detection**
        - Regular expression based pattern matching
        - Identification of demographic data fields
        - Detection of integration patterns (REST, SOAP, Database)
        - Code structure analysis using regex patterns

    - **Excel File Handling**
        - Support for XLSX and XLS formats
        - Multiple file upload capabilities
        - Column-based searching and filtering
        - Data matching between files

    - **Search and Match Features**
        - Simple text-based search across columns
        - Cross-file data matching using key columns
        - Results preview with pagination
        - Export functionality for matched records

    - **Data Analysis Tools**
        - Column-based data filtering
        - Record matching across files
        - Export capabilities for further analysis
        - Interactive data previews

    #### Use Cases
    - Cross-referencing data between Excel files
    - Finding matching records across datasets
    - Analyzing demographic data patterns
    - Generating filtered data exports
    """)

def main():
    # Navigation menu in sidebar
    if page == "Code Analysis":
        display_code_analysis()
    elif page == "Demographic Analysis":
        display_demographic_analysis()
    else:
        display_about_page()

if __name__ == "__main__":
    main()