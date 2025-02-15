git clone [repository-url]
   cd CodeLens
   ```

2. Install required dependencies:
   ```bash
   pip install streamlit==1.41.1      # Web application framework
   pip install pandas==2.1.4          # Data processing
   pip install plotly==5.18.0         # Interactive visualizations
   pip install fuzzywuzzy==0.18.0     # Fuzzy string matching
   pip install python-levenshtein     # Fast string comparison
   pip install pygments==2.18.0       # Syntax highlighting
   pip install openpyxl==3.1.2        # Excel file handling
   ```

   Or install all dependencies at once:
   ```bash
   pip install streamlit pandas plotly fuzzywuzzy python-levenshtein pygments openpyxl
   ```

## Usage

1. Start the application:
   ```bash
   streamlit run app.py
   ```

2. Access the web interface:
   - Local: `http://localhost:8501`
   - Network: `http://<your-ip>:8501`

### Key Features

1. **C360 - Meta Demographic Analysis**
   - Upload Excel files containing demographic data
   - Use fuzzy matching to compare and analyze attributes
   - Adjust similarity thresholds for precise matching

2. **Code Analysis**
   - Upload source code files or provide repository path
   - View detailed analysis of code patterns
   - Generate comprehensive reports

3. **Data Visualization**
   - Explore interactive charts and graphs
   - Analyze data patterns and correlations
   - Export visualizations and reports

## Project Structure
```
CodeLens/
├── .streamlit/
│   └── config.toml      # Streamlit configuration
├── app.py              # Main application file
├── codescan.py         # Code analysis engine
├── styles.py           # Custom styling
├── utils.py           # Utility functions
└── README.md          # Documentation