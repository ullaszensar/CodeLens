import streamlit as st
from styles import apply_custom_styles
import zipfile
import tempfile
import os
import graphviz

# Apply custom styles
apply_custom_styles()

def process_zip_file(uploaded_zip):
    """Process uploaded zip file and extract Java files"""
    java_files = []
    with tempfile.TemporaryDirectory() as temp_dir:
        # Save uploaded file to temp directory
        zip_path = os.path.join(temp_dir, "uploaded.zip")
        with open(zip_path, "wb") as f:
            f.write(uploaded_zip.getvalue())

        # Extract files
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)

            # Walk through extracted files
            for root, dirs, files in os.walk(temp_dir):
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

def create_class_diagram():
    """Create a class diagram using graphviz"""
    dot = graphviz.Digraph(comment='CodeLens Class Diagram')
    dot.attr(rankdir='TB', bgcolor='white')

    # Core Application Components (Blue)
    with dot.subgraph(name='cluster_0') as c:
        c.attr(label='Core Application Components', style='filled', color='#E3F2FD', fontcolor='#1976D2')
        c.node('MainApp', '''MainApp
        ----
        + show_demographic_analysis()
        + show_code_analysis()
        + show_about_page()''',
        style='filled', fillcolor='white', fontcolor='black')
        c.node('Styles', '''Styles
        ----
        + apply_custom_styles()''',
        style='filled', fillcolor='white', fontcolor='black')
        c.edge('MainApp', 'Styles', color='#1976D2')

    # Analysis Modules (Green)
    with dot.subgraph(name='cluster_1') as c:
        c.attr(label='Analysis Modules', style='filled', color='#E8F5E9', fontcolor='#2E7D32')
        c.node('ClassDiagram', '''ClassDiagram
        ----
        + show_class_diagram()
        + process_zip_file()''',
        style='filled', fillcolor='white', fontcolor='black')
        c.node('APISOR', '''APISOR
        ----
        + show_api_sor()
        + process_zip_file()''',
        style='filled', fillcolor='white', fontcolor='black')
        c.node('FlowDiagram', '''FlowDiagram
        ----
        + show_flow_diagram()
        + process_zip_file()''',
        style='filled', fillcolor='white', fontcolor='black')
        c.edge('ClassDiagram', 'APISOR', dir='none', color='#2E7D32')
        c.edge('APISOR', 'FlowDiagram', dir='none', color='#2E7D32')

    # Utility Components (Orange)
    with dot.subgraph(name='cluster_2') as c:
        c.attr(label='Utility Components', style='filled', color='#FFF3E0', fontcolor='#E65100')
        c.node('CodeScanner', '''CodeScanner
        ----
        + analyze_code()
        + extract_patterns()''',
        style='filled', fillcolor='white', fontcolor='black')
        c.node('Utils', '''Utils
        ----
        + display_code_with_highlights()
        + create_file_tree()''',
        style='filled', fillcolor='white', fontcolor='black')
        c.edge('CodeScanner', 'Utils', color='#E65100')

    # Cross-component relationships
    dot.edge('MainApp', 'ClassDiagram', color='#1976D2')
    dot.edge('MainApp', 'APISOR', color='#1976D2')
    dot.edge('MainApp', 'FlowDiagram', color='#1976D2')
    dot.edge('MainApp', 'CodeScanner', color='#1976D2')

    return dot

def show_class_diagram():
    st.title("Diamond Project")
    st.markdown("### Class Diagram Generator")
    # Create tabs for different views
    tab1, tab2 = st.tabs(["Project Class Diagram", "Upload & Analyze"])

    with tab1:
        st.markdown("### CodeLens Project Structure")
        dot = create_class_diagram()
        st.graphviz_chart(dot)

    with tab2:
        # File uploader for code files
        uploaded_files = st.file_uploader(
            "Upload Java files or ZIP containing Java project files",
            type=['java', 'zip'],
            accept_multiple_files=True
        )

        if uploaded_files:
            java_files = []
            for uploaded_file in uploaded_files:
                if uploaded_file.name.endswith('.zip'):
                    zip_files = process_zip_file(uploaded_file)
                    java_files.extend(zip_files)
                    st.success(f"Successfully extracted {len(zip_files)} Java files from {uploaded_file.name}")
                else:
                    content = uploaded_file.getvalue().decode()
                    java_files.append({
                        'name': uploaded_file.name,
                        'content': content,
                        'path': uploaded_file.name
                    })
                    st.success(f"Successfully loaded {uploaded_file.name}")

            if java_files:
                st.info("Custom class diagram generation will be implemented here")
        else:
            st.info("Please upload Java files or ZIP archives to generate custom class diagrams")

    # Settings section in sidebar
    st.sidebar.header("Diagram Settings")
    st.sidebar.checkbox("Show Attributes", value=True)
    st.sidebar.checkbox("Show Methods", value=True)
    st.sidebar.checkbox("Show Relationships", value=True)

if __name__ == "__main__":
    show_class_diagram()