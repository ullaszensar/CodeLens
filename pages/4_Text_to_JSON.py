import streamlit as st
from styles import apply_custom_styles
import json
import zipfile
import tempfile
import os

# Apply custom styles
apply_custom_styles()

def process_zip_file(uploaded_zip):
    """Process uploaded zip file and extract text files"""
    text_files = []
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
                    if file.endswith(('.txt', '.log', '.md')):
                        file_path = os.path.join(root, file)
                        with open(file_path, 'r') as f:
                            content = f.read()
                            text_files.append({
                                'name': file,
                                'content': content,
                                'path': os.path.relpath(file_path, temp_dir)
                            })
    return text_files

def show_text_to_json():
    st.title("Text to JSON Converter")
    st.markdown("### Convert text files to structured JSON format")

    # File uploader for text files
    uploaded_files = st.file_uploader(
        "Upload text files or ZIP containing text files",
        type=['txt', 'log', 'md', 'zip'],
        accept_multiple_files=True
    )

    if uploaded_files:
        text_files = []
        for uploaded_file in uploaded_files:
            if uploaded_file.name.endswith('.zip'):
                # Process zip file
                extracted_files = process_zip_file(uploaded_file)
                text_files.extend(extracted_files)
                st.success(f"Successfully extracted {len(extracted_files)} files from {uploaded_file.name}")
            else:
                # Process individual file
                content = uploaded_file.getvalue().decode()
                text_files.append({
                    'name': uploaded_file.name,
                    'content': content,
                    'path': uploaded_file.name
                })
                st.success(f"Successfully loaded {uploaded_file.name}")

        if text_files:
            # Conversion settings
            st.subheader("Conversion Settings")
            conversion_type = st.selectbox(
                "Select Conversion Type",
                ["Key-Value Pairs", "Structured Data", "Array of Lines"]
            )

            if st.button("Convert to JSON"):
                for file in text_files:
                    st.subheader(f"JSON Output for {file['name']}")
                    try:
                        if conversion_type == "Key-Value Pairs":
                            # Convert text with "key: value" format
                            lines = file['content'].split('\n')
                            data = {}
                            for line in lines:
                                if ':' in line:
                                    key, value = line.split(':', 1)
                                    data[key.strip()] = value.strip()
                        elif conversion_type == "Structured Data":
                            # Convert text with structured format (assuming sections)
                            sections = file['content'].split('\n\n')
                            data = {'sections': [{'content': section.strip()} for section in sections if section.strip()]}
                        else:  # Array of Lines
                            # Convert each non-empty line to array element
                            lines = file['content'].split('\n')
                            data = [line.strip() for line in lines if line.strip()]

                        # Display JSON output
                        st.json(data)
                        
                        # Download button
                        json_str = json.dumps(data, indent=2)
                        st.download_button(
                            label="Download JSON",
                            data=json_str,
                            file_name=f"{os.path.splitext(file['name'])[0]}.json",
                            mime="application/json"
                        )
                    except Exception as e:
                        st.error(f"Error converting {file['name']}: {str(e)}")
    else:
        st.info("Please upload text files or ZIP archives to convert to JSON")

    # Settings section in sidebar
    st.sidebar.header("JSON Settings")
    st.sidebar.checkbox("Pretty Print", value=True)
    st.sidebar.checkbox("Sort Keys", value=False)
    st.sidebar.checkbox("Include Metadata", value=False)

if __name__ == "__main__":
    show_text_to_json()
