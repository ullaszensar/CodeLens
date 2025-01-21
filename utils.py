import streamlit as st
import os
from pathlib import Path
from pygments import highlight, lexers, util
from pygments.lexers import get_lexer_by_name
from pygments.formatters import TerminalFormatter

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

        # Add language badge using native Streamlit components
        st.caption(f"Language: {language_name}")

        # Format the code using Pygments with Terminal formatter
        formatted_code = highlight(code_snippet, lexer, TerminalFormatter())

        # Add line number prefix and display using Streamlit's native code block
        code_with_line = f"Line {line_number}:\n{formatted_code}"
        st.code(code_with_line, language=language_name.lower())

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