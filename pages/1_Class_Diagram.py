import streamlit as st
from styles import apply_custom_styles
import zipfile
import tempfile
import os

# Apply custom styles
apply_custom_styles()

def process_zip_file(uploaded_zip):
    """Process uploaded zip file and extract Python files"""
    python_files = []
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
                    if file.endswith('.py'):
                        file_path = os.path.join(root, file)
                        with open(file_path, 'r') as f:
                            content = f.read()
                            python_files.append({
                                'name': file,
                                'content': content,
                                'path': os.path.relpath(file_path, temp_dir)
                            })
    return python_files

def show_class_diagram():
    st.title("🔍 CodeLens - Class Diagram Generator")
    st.markdown("### Generate and analyze class diagrams from your codebase")

    # File uploader for code files
    uploaded_files = st.file_uploader(
        "Upload Python files or ZIP containing Python files",
        type=['py', 'zip'],
        accept_multiple_files=True
    )

    if uploaded_files:
        python_files = []

        for uploaded_file in uploaded_files:
            if uploaded_file.name.endswith('.zip'):
                # Process zip file
                zip_files = process_zip_file(uploaded_file)
                python_files.extend(zip_files)
                st.success(f"Successfully extracted {len(zip_files)} Python files from {uploaded_file.name}")
            else:
                # Process individual Python file
                content = uploaded_file.getvalue().decode()
                python_files.append({
                    'name': uploaded_file.name,
                    'content': content,
                    'path': uploaded_file.name
                })
                st.success(f"Successfully loaded {uploaded_file.name}")

        if python_files:
            st.info("Class diagram generation will be implemented here")
            # Display file summary
            st.markdown("### Uploaded Files Summary")
            for file in python_files:
                st.markdown(f"- `{file['path']}`")
    else:
        st.info("Please upload Python files or ZIP archives to generate class diagrams")

    # Settings section in sidebar
    st.sidebar.header("Diagram Settings")
    st.sidebar.checkbox("Show Attributes", value=True)
    st.sidebar.checkbox("Show Methods", value=True)
    st.sidebar.checkbox("Show Relationships", value=True)

if __name__ == "__main__":
    show_class_diagram()