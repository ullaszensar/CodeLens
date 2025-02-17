# Install core packages
pip install streamlit==1.41.1
pip install plotly==5.18.0
pip install pandas==2.1.4
pip install pygments==2.18.0

# Install data processing packages
pip install fuzzywuzzy==0.18.0
pip install python-levenshtein==0.23.0
pip install openpyxl==3.1.2

# Install optional web scraping package
pip install trafilatura==1.6.4
```

Alternatively, you can install all packages at once using:

```bash
pip install -r requirements.txt
```

Contents of `requirements.txt`:
```
streamlit==1.41.1
plotly==5.18.0
pandas==2.1.4
pygments==2.18.0
fuzzywuzzy==0.18.0
python-levenshtein==0.23.0
openpyxl==3.1.2
trafilatura==1.6.4
```

### 2. Configure Streamlit

Create `.streamlit/config.toml` with:
```toml
[server]
headless = true
address = "0.0.0.0"
port = 5000

[theme]
primaryColor = "#0066cc"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
font = "sans serif"
```

### 3. Run the Application
```bash
streamlit run app.py
```

### 4. Access the Application
- Local development: `http://localhost:5000`
- Network access: `http://<your-ip>:5000`

## Project Structure
```
CodeLens/
├── .streamlit/
│   └── config.toml      # Streamlit configuration
├── app.py              # Main application file
├── codescan.py         # Core analysis logic
├── utils.py            # Utility functions
├── styles.py           # Custom styling
└── README.md           # Documentation