# ZensarCA (Zensar Code Analysis)

## Mac Setup Instructions with PyCharm

1. Install Python 3.11 if not already installed:
```bash
brew install python@3.11
```

2. Create project directory:
```bash
mkdir ~/Projects/ZensarCA
cd ~/Projects/ZensarCA
```

3. Set up project structure:
```bash
mkdir .streamlit
touch .streamlit/config.toml
touch app.py codescan.py complexity.py styles.py utils.py
```

4. Create and set up PyCharm project:
- Open PyCharm
- Click "Open"
- Navigate to ~/Projects/ZensarCA
- Select "Open as Project"
- Go to PyCharm → Preferences → Project: ZensarCA → Python Interpreter
- Click ⚙️ icon → Add Interpreter → Add Local Interpreter
- Select "New Environment" using Python 3.11
- Click "OK"

5. Install required packages in PyCharm terminal:
```bash
pip install streamlit plotly pygments radon
```

6. Copy the following content into `.streamlit/config.toml`:
```toml
[server]
headless = true
address = "0.0.0.0"
port = 5000

[theme]
primaryColor = "#FF4B4B"
backgroundColor = "#0E1117"
secondaryBackgroundColor = "#262730"
textColor = "#FAFAFA"
font = "sans serif"
```

7. Copy the provided Python files:
- app.py: Main Streamlit application file
- codescan.py: Code analysis implementation
- complexity.py: Code complexity metrics
- styles.py: Custom styling for the application
- utils.py: Utility functions

8. Run the application:
- Open app.py in PyCharm
- Right-click in the editor
- Select "Run 'app'"
- Access the application at http://localhost:5000

## Windows Setup Instructions with VSCode

1. Install Python 3.11:
   - Download Python 3.11 from [python.org](https://www.python.org/downloads/)
   - During installation, check "Add Python to PATH"
   - Verify installation: `python --version` in Command Prompt

2. Install VSCode:
   - Download from [code.visualstudio.com](https://code.visualstudio.com)
   - Install Python extension in VSCode

3. Create project directory:
```cmd
md ZensarCA
cd ZensarCA
```

4. Set up Python environment:
```cmd
python -m venv venv
venv\Scripts\activate
pip install streamlit plotly pygments radon
```

5. Set up project structure:
```cmd
md .streamlit
type nul > .streamlit\config.toml
type nul > app.py
type nul > codescan.py
type nul > complexity.py
type nul > styles.py
type nul > utils.py
```

6. Copy the following content into `.streamlit/config.toml`:
```toml
[server]
headless = true
address = "0.0.0.0"
port = 5000

[theme]
primaryColor = "#FF4B4B"
backgroundColor = "#0E1117"
secondaryBackgroundColor = "#262730"
textColor = "#FAFAFA"
font = "sans serif"
```

7. Copy the provided Python files:
- app.py: Main Streamlit application file
- codescan.py: Code analysis implementation
- complexity.py: Code complexity metrics
- styles.py: Custom styling for the application
- utils.py: Utility functions

8. Run the application:
- Open VSCode in project directory: `code .`
- Open Terminal in VSCode (View → Terminal)
- Ensure venv is activated: `venv\Scripts\activate`
- Run: `streamlit run app.py`
- Access at http://localhost:5000

## Project Files Description

1. app.py: Main Streamlit application that provides the user interface
2. codescan.py: Implements code analysis functionality for multiple programming languages
3. complexity.py: Contains code complexity calculation and visualization tools
4. styles.py: Custom CSS styles for better UI appearance
5. utils.py: Helper functions for file operations and code display

## Package Dependencies
- streamlit: Web application framework
- plotly: Interactive visualization library for complexity heatmaps
- pygments: Syntax highlighting for code snippets
- radon: Code complexity analysis tool

## Features

1. Multi-Language Code Analysis
   - Supported Languages: Java, Python, JavaScript, TypeScript, C#, PHP, Ruby, XSD
   - File Extensions: .java, .py, .js, .ts, .cs, .php, .rb, .xsd

2. Code Complexity Analysis
   - Cyclomatic complexity calculation
   - Interactive complexity heatmaps
   - Complexity ranking (A-F grade system)
   - Lines of code metrics
   - Function count analysis

3. Pattern Detection
   - REST API patterns
   - SOAP service patterns
   - Database operations
   - Messaging systems (Kafka, RabbitMQ, JMS)
   - File operations
   - Demographic data patterns

4. Interactive Visualization
   - File tree visualization
   - Syntax-highlighted code snippets
   - Interactive complexity heatmaps
   - Custom themed UI