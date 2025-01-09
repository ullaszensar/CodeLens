import streamlit as st
import tempfile
import os
from pathlib import Path
import time
from codescan import CodeAnalyzer
from utils import display_code_with_highlights, create_file_tree
from styles import apply_custom_styles
from complexity import generate_complexity_heatmap, calculate_file_complexity, display_complexity_metrics
import base64
from typing import List, Dict

# Page config
st.set_page_config(
    page_title="ZensarCA - Code Analysis",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom styles
apply_custom_styles()

# Creator information
st.sidebar.markdown("""
### Created by:
**AES Team**  
Zensar
""")

def get_file_download_link(file_path, link_text):
    """Generate a download link for a file"""
    with open(file_path, 'r') as f:
        data = f.read()
    b64 = base64.b64encode(data.encode()).decode()
    return f'<a href="data:text/html;base64,{b64}" download="{os.path.basename(file_path)}">{link_text}</a>'

def format_matching_records(file_data):
    """Format matching records for display in table"""
    records = []
    for field_name, data in file_data.items():
        for occurrence in data['occurrences']:
            records.append(f"Line {occurrence['line_number']} - {field_name}")
    return "\n".join(records)

def filter_results(results: Dict, file_extensions: List[str] = None, pattern_types: List[str] = None, search_term: str = None):
    """Filter analysis results based on criteria"""
    filtered_data = {}

    for file_path, fields in results['demographic_data'].items():
        # Filter by file extension
        if file_extensions and not any(file_path.endswith(ext) for ext in file_extensions):
            continue

        # Filter by search term
        if search_term:
            matches_search = False
            for field_name, data in fields.items():
                if (search_term.lower() in field_name.lower() or 
                    any(search_term.lower() in occ['code_snippet'].lower() 
                        for occ in data['occurrences'])):
                    matches_search = True
                    break
            if not matches_search:
                continue

        # Filter by pattern type
        if pattern_types:
            matches_pattern = False
            for field_name, data in fields.items():
                if data['data_type'] in pattern_types:
                    matches_pattern = True
                    break
            if not matches_pattern:
                continue

        filtered_data[file_path] = fields

    return filtered_data

def main():
    st.title("🔍 ZensarCA")
    st.markdown("### Code Analysis Utility")

    # Sidebar
    st.sidebar.header("Analysis Settings")
    st.sidebar.markdown("*Source Code Analysis Utility*")

    # Input method selection
    input_method = st.sidebar.radio(
        "Choose Input Method",
        ["Upload Files", "Repository Path"]
    )

    # Application name input
    app_name = st.sidebar.text_input("Application/Repository Name", "MyApp")

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
                results = analyzer.scan_repository()
                progress_bar.progress(100)

                # Display Results
                col1, col2 = st.columns([2, 1])

                with col1:
                    st.header("Analysis Results")

                    # Summary Statistics in expander
                    with st.expander("Summary Statistics", expanded=False):
                        stats_cols = st.columns(4)
                        stats_cols[0].metric("Files Analyzed", results['summary']['files_analyzed'])
                        stats_cols[1].metric("Demographic Fields", results['summary']['demographic_fields_found'])
                        stats_cols[2].metric("Integration Patterns", results['summary']['integration_patterns_found'])
                        stats_cols[3].metric("Unique Fields", len(results['summary']['unique_demographic_fields']))

                    # Add filtering options
                    st.subheader("Filter Results")

                    # File extension filter
                    available_extensions = ['.py', '.java', '.js', '.ts', '.cs', '.php', '.rb', '.xsd']
                    selected_extensions = st.multiselect(
                        "Filter by File Type",
                        available_extensions,
                        default=available_extensions
                    )

                    # Pattern type filter
                    pattern_types = ['name', 'address', 'contact', 'identity', 'demographics']
                    selected_patterns = st.multiselect(
                        "Filter by Pattern Type",
                        pattern_types,
                        default=pattern_types
                    )

                    # Search box
                    search_term = st.text_input("Search in Results", "")

                    # Sort options
                    sort_by = st.selectbox(
                        "Sort Results By",
                        ["File Name", "Number of Matches"]
                    )

                    # Apply filters
                    filtered_results = filter_results(
                        results,
                        file_extensions=selected_extensions,
                        pattern_types=selected_patterns,
                        search_term=search_term
                    )

                    # Create and sort table data
                    table_data = []
                    for file_path, fields in filtered_results.items():
                        matches = format_matching_records(fields)
                        table_data.append({
                            "Class/File Name": os.path.basename(file_path),
                            "Matching Records": matches,
                            "_match_count": matches.count('\n') + 1  # For sorting
                        })

                    # Sort table data
                    if sort_by == "File Name":
                        table_data.sort(key=lambda x: x["Class/File Name"])
                    else:  # Number of Matches
                        table_data.sort(key=lambda x: x["_match_count"], reverse=True)

                    # Remove sorting helper field
                    for row in table_data:
                        del row["_match_count"]

                    # Display table
                    st.subheader("Matching Records")
                    if table_data:
                        st.table(table_data)
                    else:
                        st.info("No matching records found with current filters.")

                with col2:
                    st.header("Code Complexity Analysis")

                    # Generate and display complexity heat map
                    heatmap = generate_complexity_heatmap(
                        repo_path,
                        ['.py', '.java', '.js', '.ts', '.cs', '.php', '.rb', '.xsd']
                    )
                    if heatmap:
                        st.plotly_chart(heatmap, use_container_width=True)

                        st.markdown("""
                        ### Understanding the Heat Map
                        - **Green**: Low complexity (Good)
                        - **Yellow**: Medium complexity (Moderate)
                        - **Orange**: High complexity (Warning)
                        - **Red**: Very high complexity (Critical)

                        Hover over the cells to see detailed metrics for each file.
                        """)

                        # Add expandable section for complexity metrics explanation
                        with st.expander("What do these metrics mean?"):
                            st.markdown("""
                            - **Cyclomatic Complexity**: Measures the number of linearly independent paths through code
                            - **Complexity Rank**: Grade from A (best) to F (worst) based on complexity
                            - **Lines of Code**: Total number of code lines
                            - **Logical Lines**: Number of executable statements
                            - **Functions**: Number of functions/methods in the file
                            """)

                    st.header("File Structure")
                    create_file_tree(repo_path)

                    # Download Reports
                    st.header("Export Reports")
                    report_files = [f for f in os.listdir() if f.endswith(('.html', '.json')) and 'code_analysis' in f]

                    for report_file in report_files:
                        st.markdown(
                            get_file_download_link(report_file, f"Download {report_file}"),
                            unsafe_allow_html=True
                        )

        except Exception as e:
            st.error(f"Error during analysis: {str(e)}")

        finally:
            if temp_dir:
                import shutil
                shutil.rmtree(temp_dir)

if __name__ == "__main__":
    main()