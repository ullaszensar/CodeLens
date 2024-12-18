import streamlit as st
import os
from pathlib import Path
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter

def display_code_with_highlights(code_snippet: str, line_number: int):
    """Display code with syntax highlighting"""
    # Determine language from file extension or default to Python
    try:
        lexer = get_lexer_by_name("python")
        formatted_code = highlight(
            code_snippet,
            lexer,
            HtmlFormatter(style='monokai', linenos=True, linenostart=line_number)
        )
        
        st.markdown(
            f"""
            <style>
                .highlight pre {{ background-color: #272822; padding: 10px; border-radius: 5px; }}
                .highlight .linenos {{ color: #8f908a; }}
            </style>
            {formatted_code}
            """,
            unsafe_allow_html=True
        )
    except Exception:
        st.code(code_snippet)

def create_file_tree(path: str):
    """Create an interactive file tree visualization"""
    try:
        for root, dirs, files in os.walk(path):
            level = root.replace(path, '').count(os.sep)
            indent = ' ' * 4 * level
            folder_name = os.path.basename(root)
            if level == 0:
                st.markdown("📁 **/**")
            else:
                st.markdown(f"{indent}📁 **{folder_name}**")
            
            subindent = ' ' * 4 * (level + 1)
            for file in files:
                if file.endswith(('.py', '.java', '.js', '.ts', '.cs', '.php', '.rb')):
                    st.markdown(f"{subindent}📄 {file}")
    except Exception as e:
        st.error(f"Error creating file tree: {str(e)}")
