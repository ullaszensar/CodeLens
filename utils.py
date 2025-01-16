import streamlit as st
import os
from pathlib import Path
from pygments import highlight, lexers, util
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter

def detect_language(file_path: str, content: str = None) -> tuple:
    """Detect programming language from file extension and content"""
    try:
        # First try to guess from content if provided
        if content:
            try:
                lexer = lexers.guess_lexer(content)
                return lexer.name, lexer
            except util.ClassNotFound:
                pass

        # Try to guess from file extension
        _, ext = os.path.splitext(file_path)
        language_map = {
            '.py': ('Python', 'python'),
            '.js': ('JavaScript', 'javascript'),
            '.ts': ('TypeScript', 'typescript'),
            '.java': ('Java', 'java'),
            '.cs': ('C#', 'csharp'),
            '.php': ('PHP', 'php'),
            '.rb': ('Ruby', 'ruby'),
            '.xsd': ('XML Schema', 'xml')
        }

        if ext in language_map:
            name, lexer_name = language_map[ext]
            return name, get_lexer_by_name(lexer_name)

        # Default to Python if unable to detect
        return 'Unknown', get_lexer_by_name('python')
    except Exception:
        return 'Unknown', get_lexer_by_name('python')

def display_code_with_highlights(code_snippet: str, line_number: int, file_path: str = None):
    """Display code with syntax highlighting and language detection"""
    try:
        # Detect language
        language_name, lexer = detect_language(file_path if file_path else '', code_snippet)

        # Add language badge
        st.markdown(f"""
            <div style="margin-bottom: 5px;">
                <span style="background-color: #0066cc; color: white; padding: 2px 8px; border-radius: 3px; font-size: 0.8em;">
                    {language_name}
                </span>
            </div>
        """, unsafe_allow_html=True)

        # Format and display code
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
                if file.endswith(('.py', '.java', '.js', '.ts', '.cs', '.php', '.rb', '.xsd')):
                    # Detect language for the file
                    try:
                        language_name, _ = detect_language(file)
                        st.markdown(f"{subindent}📄 {file} `{language_name}`")
                    except:
                        st.markdown(f"{subindent}📄 {file}")
    except Exception as e:
        st.error(f"Error creating file tree: {str(e)}")