import streamlit as st

def main():
    try:
        st.set_page_config(
            page_title="CodeLens",
            page_icon="🔍",
            layout="wide"
        )
        st.title("CodeLens")
        st.write("Testing Streamlit Setup")

        # Add a simple interactive element
        if st.button("Click me to test"):
            st.success("✅ Streamlit is working correctly!")

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        print(f"Error in Streamlit app: {str(e)}")  # Console logging for debugging

if __name__ == "__main__":
    main()