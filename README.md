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
   - Create a new folder named `ZensarCA`
   - Copy all provided Python files into it:
     - app.py
     - codescan.py
     - complexity.py
     - styles.py
     - utils.py
   - Create `.streamlit/config.toml` with the provided configuration

4. Run Application:
   - Open VSCode: `code .`
   - Open Terminal in VSCode: View → Terminal
   - Activate virtual environment: `venv\Scripts\activate`
   - Run: `streamlit run app.py`
   - Access at http://localhost:5000

Note: The application now excludes matches found in comments from the analysis results, reducing the HTML report size.

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