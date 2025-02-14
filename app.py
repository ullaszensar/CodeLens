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
from st_aggrid import AgGrid, GridOptionsBuilder

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

# Demographic Analysis Functions (Previously Excel Analysis)

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

def display_demographic_analysis():
    st.title("📊 Demographic Data Analysis")

    # File upload section
    uploaded_file = st.file_uploader("Upload Excel File", type=['xlsx', 'xls'])

    if uploaded_file:
        try:
            # Load the Excel file
            df = pd.read_excel(uploaded_file)

            # Display original data in a compact grid
            st.subheader("Original Data Preview")
            gb = GridOptionsBuilder.from_dataframe(df)
            gb.configure_pagination(paginationAutoPageSize=True)
            gb.configure_side_bar()
            grid_response = AgGrid(
                df,
                gridOptions=gb.build(),
                height=300,
                data_return_mode='AS_INPUT'
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

            # Add fuzzy search threshold slider
            fuzzy_threshold = st.slider(
                "Fuzzy Search Similarity Threshold (%)",
                min_value=50,
                max_value=100,
                value=80,
                help="Lower values will return more approximate matches"
            )

            # Filter data based on search criteria
            if search_term and selected_column:
                # Initialize empty mask for fuzzy matching
                mask = pd.Series(False, index=df.index)

                # Perform fuzzy matching on the selected column
                for idx, value in df[selected_column].astype(str).items():
                    # Calculate similarity ratio between search term and value
                    similarity = fuzz.ratio(search_term.lower(), value.lower())
                    if similarity >= fuzzy_threshold:
                        mask.at[idx] = True

                filtered_df = df[mask]

                st.subheader("Search Results")
                if not filtered_df.empty:
                    # Display filtered results in a grid
                    gb_filtered = GridOptionsBuilder.from_dataframe(filtered_df)
                    gb_filtered.configure_pagination(paginationAutoPageSize=True)
                    AgGrid(
                        filtered_df,
                        gridOptions=gb_filtered.build(),
                        height=300,
                        data_return_mode='AS_INPUT'
                    )

                    st.info(f"Found {len(filtered_df)} matches")

                    # Export results button
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
            "RapidFuzz",
            "Streamlit-AgGrid",
            "Pygments",
            "OpenAI API" #This line was added
        ],
        "Purpose": [
            "Web application framework for data apps",
            "Data manipulation and analysis",
            "Interactive data visualization",
            "Fuzzy string matching and search",
            "Advanced interactive data tables",
            "Code syntax highlighting",
            "AI-powered code analysis"
        ],
        "Key Benefits": [
            "Rapid development, interactive UI components",
            "Efficient handling of large datasets",
            "Rich, interactive charts and dashboards",
            "Intelligent search capabilities",
            "Enhanced data grid with sorting and filtering",
            "Beautiful code presentation",
            "Intelligent code pattern recognition"
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
            "Fuzzy Search",
            "Interactive Visualizations",
            "Export Capabilities",
            "Pattern Recognition"
        ],
        "Description": [
            "Deep analysis of source code for patterns and integrations",
            "Analysis of demographic data with advanced filtering",
            "Intelligent search using fuzzy matching algorithms",
            "Interactive charts and dashboards for data insights",
            "Export results to Excel for further analysis",
            "Identification of code patterns and potential issues"
        ],
        "Details": [
            "Supports multiple programming languages, identifies integration patterns",
            "Excel file analysis with column-based searching",
            "Uses RapidFuzz with adjustable similarity threshold (50-100%)",
            "Powered by Plotly for dynamic, interactive charts",
            "Generate detailed reports in Excel format",
            "AI-powered pattern detection and code structure analysis"
        ]
    }

    features_df = pd.DataFrame(features)
    st.table(features_df)

    # Fuzzy Logic Section
    st.subheader("🔍 Fuzzy Search Technology")
    st.markdown("""
    CodeLens implements advanced fuzzy search capabilities using the RapidFuzz library, which provides:

    - **Similarity Matching**: Uses Levenshtein distance algorithm to find approximate matches
    - **Adjustable Threshold**: Customizable similarity threshold (50-100%)
    - **Case-Insensitive**: Matches regardless of letter case
    - **Performance**: Optimized for large datasets

    #### How it Works
    1. User enters a search term
    2. System calculates similarity ratio between search term and each value
    3. Returns matches above the specified threshold
    4. Results are ranked by similarity score

    #### Use Cases
    - Finding similar names or terms
    - Matching patterns in code
    - Identifying related demographic data
    - Handling typos and variations in search
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