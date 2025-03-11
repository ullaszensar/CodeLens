import streamlit as st
from styles import apply_custom_styles
import zipfile
import tempfile
import os

# Apply custom styles
apply_custom_styles()

def process_zip_file(uploaded_zip):
    """Process uploaded zip file and extract flow diagram input files"""
    flow_files = []
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
                    if file.endswith(('.txt', '.md', '.py')):
                        file_path = os.path.join(root, file)
                        with open(file_path, 'r') as f:
                            content = f.read()
                            flow_files.append({
                                'name': file,
                                'content': content,
                                'path': os.path.relpath(file_path, temp_dir)
                            })
    return flow_files

def show_flow_diagram():
    st.title("🔍 CodeLens - Flow Diagram Generator")
    st.markdown("### Generate and visualize process flows")

    # File uploader for flow diagram input
    uploaded_files = st.file_uploader(
        "Upload process description files (TXT, MD, PY) or ZIP containing these files",
        type=['txt', 'md', 'py', 'zip'],
        accept_multiple_files=True
    )

    if uploaded_files:
        flow_files = []

        for uploaded_file in uploaded_files:
            if uploaded_file.name.endswith('.zip'):
                # Process zip file
                extracted_files = process_zip_file(uploaded_file)
                flow_files.extend(extracted_files)
                st.success(f"Successfully extracted {len(extracted_files)} files from {uploaded_file.name}")
            else:
                # Process individual file
                content = uploaded_file.getvalue().decode()
                flow_files.append({
                    'name': uploaded_file.name,
                    'content': content,
                    'path': uploaded_file.name
                })
                st.success(f"Successfully loaded {uploaded_file.name}")

        if flow_files:
            st.info("Flow diagram generation will be implemented here")
            # Display file summary
            st.markdown("### Uploaded Files Summary")
            for file in flow_files:
                st.markdown(f"- `{file['path']}`")
    else:
        st.info("Please upload process description files to generate flow diagrams")

    # Settings section in sidebar
    st.sidebar.header("Diagram Settings")
    st.sidebar.checkbox("Show Decision Points", value=True)
    st.sidebar.checkbox("Show Process Steps", value=True)
    st.sidebar.checkbox("Show Connections", value=True)

if __name__ == "__main__":
    show_flow_diagram()