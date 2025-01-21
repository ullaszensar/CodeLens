# ZensarCA (Zensar Code Analysis)

A comprehensive web-based source code analysis tool designed to extract demographic data and integration patterns across multiple programming languages.

## Key Benefits
- **Time-Saving Code Analysis**
  - Automatically scans and analyzes code across 8 programming languages
  - Eliminates manual code review effort for finding data patterns
  - Rapid identification of integration points saves weeks of documentation work

- **Enhanced Security & Compliance**
  - Identifies sensitive demographic data patterns across codebases
  - Helps ensure GDPR and data privacy compliance
  - Tracks where customer data is being handled in the code

- **Better Architecture Understanding**
  - Visual representation of code patterns and relationships
  - Clear mapping of all integration points (APIs, databases, messaging)
  - Helps new team members understand system architecture quickly

- **Data-Driven Decision Making**
  - Interactive dashboards show code metrics and patterns
  - Helps identify areas needing refactoring or standardization
  - Provides concrete metrics for technical debt discussions

- **Improved Documentation**
  - Auto-generates comprehensive HTML reports
  - Creates living documentation that stays current with the code
  - Exports findings in multiple formats for different stakeholders

- **Developer Productivity**
  - Instant insight into unfamiliar codebases
  - Reduces time spent searching for integration points
  - Helps prevent duplicate implementations


## Created by
- **Zensar Project Diamond Team**

## Setup Instructions

### Prerequisites
1. Python 3.11 or higher
2. VSCode with Python extension installed
3. Git (optional, for version control)

### Installation Steps

1. Download the project files:
   - Download all the following files into a new directory named `ZensarCA`:
     - `app.py` (Main application file)
     - `codescan.py` (Core analysis engine)
     - `utils.py` (Utility functions)
     - `styles.py` (Custom styling)
     - `.streamlit/config.toml` (Streamlit configuration)

2. Open the project in VSCode:
   ```bash
   code ZensarCA
   ```

3. Create a Python virtual environment:
   ```bash
   python -m venv venv
   ```

4. Activate the virtual environment:
   - Windows:
     ```bash
     .\venv\Scripts\activate
     ```
   - Linux/Mac:
     ```bash
     source venv/bin/activate
     ```

5. Install required packages:
   ```bash
   pip install streamlit==1.41.1 pygments==2.18.0 plotly==5.18.0
   ```
   This will install:
   - Streamlit: For the web interface
   - Pygments: For code syntax highlighting
   - Plotly: For interactive data visualizations and dashboards

### Running the Application

1. Create the `.streamlit` directory and configuration:
   ```bash
   mkdir .streamlit
   ```

2. Create `.streamlit/config.toml` with:
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

3. Run the Streamlit application:
   ```bash
   streamlit run app.py
   ```

4. Access the application:
   - Local development: `http://localhost:5000`
   - Network access: `http://<your-ip>:5000`

## Project Structure

```
ZensarCA/
├── .streamlit/
│   └── config.toml      # Streamlit configuration
├── app.py              # Main application file
├── codescan.py         # Core code analysis logic
├── utils.py            # Utility functions
├── styles.py           # Custom styling
└── README.md           # This file
```

## Features
- Supports analysis of multiple programming languages:
  - Java
  - Python
  - JavaScript
  - TypeScript
  - C#
  - PHP
  - Ruby
  - XSD
- Advanced code parsing with regex-based pattern detection
- Demographic data extraction:
  - Customer IDs
  - Names
  - Addresses
  - Contact information
- Integration pattern detection:
  - REST APIs
  - SOAP services
  - Database operations
  - Messaging systems
  - File operations
- HTML report generation with detailed findings
- Interactive web interface with syntax highlighting
- Interactive dashboards with:
  - File distribution charts
  - Demographic field analysis
  - Integration pattern visualization
  - Correlation graphs

## Usage
1. Launch the application using the steps above
2. Choose input method:
   - Upload Files: Select multiple source code files
   - Repository Path: Enter path to code directory
3. Enter the application/repository name
4. Click "Run Analysis"
5. View the analysis results:
   - Interactive dashboards
   - Summary statistics
   - Demographic data findings
   - Integration patterns detected
6. Export reports:
   - Download HTML report
   - Download JSON report

## Troubleshooting
- If the application doesn't start, check:
  - Python version (3.11+ required)
  - Virtual environment activation
  - All required packages are installed
  - Correct port availability (5000)
- For permission issues:
  - Ensure write access to the project directory
  - Run with appropriate permissions for file operations

## Notes
- Supported file extensions: .py, .java, .js, .ts, .cs, .php, .rb, .xsd
- Reports are generated in both JSON and HTML formats
- The tool requires read access to the source code files/directory
- Large repositories may take longer to analyze