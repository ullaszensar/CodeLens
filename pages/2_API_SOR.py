import streamlit as st
from styles import apply_custom_styles
import zipfile
import tempfile
import os
import json
import yaml

# Apply custom styles
apply_custom_styles()

def process_zip_file(uploaded_zip):
    """Process uploaded zip file and extract API-related files"""
    api_files = []
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
                    # Include Java files and common API config files
                    if file.endswith(('.java', '.json', '.yaml', '.yml', '.properties')):
                        file_path = os.path.join(root, file)
                        with open(file_path, 'r') as f:
                            content = f.read()
                            api_files.append({
                                'name': file,
                                'content': content,
                                'path': os.path.relpath(file_path, temp_dir),
                                'type': os.path.splitext(file)[1][1:]
                            })
    return api_files

def show_api_sor():
    st.title("Diamond Project")
    st.markdown("### API/SOR Analysis")
    # File uploader for API documentation or code files
    uploaded_files = st.file_uploader(
        "Upload Java files, API configuration files (JSON, YAML, Properties) or ZIP containing these files",
        type=['java', 'json', 'yaml', 'yml', 'properties', 'zip'],
        accept_multiple_files=True
    )

    if uploaded_files:
        api_files = []

        for uploaded_file in uploaded_files:
            if uploaded_file.name.endswith('.zip'):
                # Process zip file
                extracted_files = process_zip_file(uploaded_file)
                api_files.extend(extracted_files)
                st.success(f"Successfully extracted {len(extracted_files)} files from {uploaded_file.name}")
            else:
                # Process individual file
                content = uploaded_file.getvalue().decode()
                api_files.append({
                    'name': uploaded_file.name,
                    'content': content,
                    'path': uploaded_file.name,
                    'type': uploaded_file.name.split('.')[-1]
                })
                st.success(f"Successfully loaded {uploaded_file.name}")

        if api_files:
            st.info("API/SOR analysis will be implemented here")
            # Display file summary
            st.markdown("### Uploaded Files Summary")
            for file in api_files:
                st.markdown(f"- `{file['path']}` ({file['type'].upper()})")
    else:
        st.info("Please upload Java files or API configuration files for analysis")

    # Settings section in sidebar
    st.sidebar.header("Analysis Settings")
    st.sidebar.checkbox("Show Endpoints", value=True)
    st.sidebar.checkbox("Show Parameters", value=True)
    st.sidebar.checkbox("Show Response Types", value=True)

if __name__ == "__main__":
    show_api_sor()