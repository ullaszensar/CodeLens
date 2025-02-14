import streamlit as st
import pandas as pd
from rapidfuzz import fuzz, process
from io import BytesIO
import tempfile
import os

def load_excel_file(uploaded_file):
    """Load Excel file and return DataFrame"""
    try:
        return pd.read_excel(uploaded_file)
    except Exception as e:
        st.error(f"Error loading Excel file: {str(e)}")
        return None

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

def main():
    st.title("📊 Excel File Analyzer")
    
    # Sidebar settings
    st.sidebar.header("Excel Analysis Settings")
    match_threshold = st.sidebar.slider(
        "Column Matching Threshold",
        min_value=50,
        max_value=100,
        value=80,
        help="Minimum similarity score (%) for matching columns"
    )

    # File upload section
    st.subheader("Upload Excel Files")
    col1, col2 = st.columns(2)
    
    with col1:
        file1 = st.file_uploader("Upload First Excel File", type=['xlsx', 'xls'])
        if file1:
            df1 = load_excel_file(file1)
            if df1 is not None:
                st.success(f"File 1 loaded: {df1.shape[0]} rows, {df1.shape[1]} columns")
                st.dataframe(df1.head(), use_container_width=True)
    
    with col2:
        file2 = st.file_uploader("Upload Second Excel File", type=['xlsx', 'xls'])
        if file2:
            df2 = load_excel_file(file2)
            if df2 is not None:
                st.success(f"File 2 loaded: {df2.shape[0]} rows, {df2.shape[1]} columns")
                st.dataframe(df2.head(), use_container_width=True)
    
    # Analysis section
    if file1 and file2 and df1 is not None and df2 is not None:
        st.subheader("Column Analysis")
        
        # Find matching columns
        matches = fuzzy_match_columns(df1, df2, match_threshold)
        
        # Display matched columns
        st.write("#### Matched Columns")
        if matches:
            match_df = pd.DataFrame(matches, columns=['File 1 Column', 'File 2 Column', 'Match Score'])
            st.dataframe(match_df, use_container_width=True)
            
            # Compare matched columns
            comparison_results = compare_dataframes(df1, df2, matches)
            
            st.write("#### Detailed Comparison")
            st.dataframe(comparison_results, use_container_width=True)
            
            # Export results
            if st.button("Export Analysis Results"):
                # Create Excel file with multiple sheets
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    comparison_results.to_excel(writer, sheet_name='Comparison Results', index=False)
                    match_df.to_excel(writer, sheet_name='Matched Columns', index=False)
                
                # Offer download
                st.download_button(
                    label="Download Excel Analysis",
                    data=output.getvalue(),
                    file_name="excel_analysis_results.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        else:
            st.warning("No matching columns found with the current threshold")

if __name__ == "__main__":
    main()
