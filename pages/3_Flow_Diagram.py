import streamlit as st
from styles import apply_custom_styles

# Apply custom styles
apply_custom_styles()

def show_flow_diagram():
    st.title("🔍 CodeLens - Flow Diagram Generator")
    st.markdown("### Generate and visualize process flows")

    # File uploader for flow diagram input
    uploaded_files = st.file_uploader(
        "Upload process description files",
        type=['txt', 'md', 'py'],
        accept_multiple_files=True
    )

    if uploaded_files:
        st.info("Flow diagram generation will be implemented here")
        # TODO: Implement flow diagram generation logic
        # This will include:
        # - Process flow extraction
        # - Diagram generation
        # - Interactive flow visualization
        
    else:
        st.info("Please upload process description files to generate flow diagrams")

    # Settings section in sidebar
    st.sidebar.header("Diagram Settings")
    st.sidebar.checkbox("Show Decision Points", value=True)
    st.sidebar.checkbox("Show Process Steps", value=True)
    st.sidebar.checkbox("Show Connections", value=True)

if __name__ == "__main__":
    show_flow_diagram()
