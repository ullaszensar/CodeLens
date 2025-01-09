# ZensarCA (Zensar Code Analysis)

## Quick Start Guide for VSCode (Windows)

1. Prerequisites:
   - Install [Python 3.11](https://www.python.org/downloads/)
   - Install [VSCode](https://code.visualstudio.com)
   - Install VSCode Python extension

2. Quick Setup:
```cmd
md ZensarCA
cd ZensarCA
python -m venv venv
venv\Scripts\activate
pip install streamlit plotly pygments radon
```

3. Download and Copy Files:
   - Create a new folder named `.streamlit` and create `config.toml` inside with:
```toml
[server]
headless = true
address = "0.0.0.0"
port = 5000
```

4. Copy these Python files to your project:
   - app.py (Main application)
   - codescan.py (Code analyzer)
   - complexity.py (Complexity metrics)
   - styles.py (UI styling)
   - utils.py (Helper functions)

5. Run Application:
   - Open VSCode: `code .`
   - Open Terminal in VSCode: View → Terminal
   - Activate virtual environment: `venv\Scripts\activate`
   - Run: `streamlit run app.py`
   - Access at http://localhost:5000

Note: The application excludes matches found in comments from the analysis results, reducing the HTML report size.

## Features

1. Multi-Language Code Analysis
   - Supported Languages: Java, Python, JavaScript, TypeScript, C#, PHP, Ruby, XSD
   - Analyzes source code patterns and complexity

2. Code Complexity Analysis
   - Cyclomatic complexity calculation
   - Interactive complexity heatmaps
   - Complexity ranking (A-F grade system)

3. Pattern Detection
   - REST API patterns
   - SOAP service patterns
   - Database operations
   - Messaging systems
   - File operations

4. Interactive Visualization
   - File tree visualization
   - Syntax-highlighted code snippets
   - Interactive complexity heatmaps