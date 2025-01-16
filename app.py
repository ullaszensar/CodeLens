import streamlit as st
import tempfile
import os
from pathlib import Path
import time
from codescan import CodeAnalyzer
from utils import display_code_with_highlights, create_file_tree
from styles import apply_custom_styles
import base64

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

def get_file_download_link(file_path, link_text):
    """Generate a download link for a file"""
    with open(file_path, 'r') as f:
        data = f.read()
    b64 = base64.b64encode(data.encode()).decode()
    return f'<a href="data:text/html;base64,{b64}" download="{os.path.basename(file_path)}">{link_text}</a>'

def main():
    st.title("🔍 CodeLens")
    st.markdown("### Source Code Analysis Tool")
    
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
                
                # Run analysis
                results = analyzer.scan_repository()
                progress_bar.progress(100)
                
                # Display Results
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.header("Analysis Results")
                    
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
                                        occurrence['line_number']
                                    )
                    
                    # Integration Patterns
                    st.subheader("Integration Patterns")
                    for pattern in results['integration_patterns']:
                        with st.expander(f"🔌 {pattern['pattern_type']} - {pattern['sub_type']}"):
                            st.write(f"**File:** {os.path.basename(pattern['file_path'])}")
                            st.write(f"**Line:** {pattern['line_number']}")
                            display_code_with_highlights(pattern['code_snippet'], pattern['line_number'])
                
                with col2:
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