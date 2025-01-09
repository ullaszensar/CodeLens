# Local Installation Guide for ZensarCA

## Prerequisites
1. Python 3.11 or higher
2. pip (Python package manager)

## Step-by-Step Installation

### 1. Clone or Download the Project
```bash
git clone <repository-url>
cd ZensarCA
```

### 2. Set Up Python Virtual Environment (Optional but Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Required Packages
```bash
pip install streamlit plotly pygments radon openai
```

### 4. Configure OpenAI API Key
1. Get your API key from [OpenAI Platform](https://platform.openai.com/api-keys)
2. Set it as an environment variable:
   ```bash
   # Windows
   set OPENAI_API_KEY=your-api-key-here

   # macOS/Linux
   export OPENAI_API_KEY=your-api-key-here
   ```
   Or create a `.env` file in the project root:
   ```
   OPENAI_API_KEY=your-api-key-here
   ```

### 5. Create Required Directory Structure
```bash
mkdir -p .streamlit
```

### 6. Configure Streamlit
Create `.streamlit/config.toml` with the following content:
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

### 7. Run the Application
```bash
streamlit run app.py
```
The application will be available at `http://localhost:5000`

## Troubleshooting

### Common Issues and Solutions

1. **Import Error for OpenAI**
   - Ensure you have installed the latest version of the openai package:
     ```bash
     pip install --upgrade openai
     ```

2. **Streamlit Port Already in Use**
   - Change the port in `.streamlit/config.toml` to another number (e.g., 8501)
   - Kill the process using the current port:
     ```bash
     # Windows
     netstat -ano | findstr :5000
     taskkill /PID <PID> /F

     # macOS/Linux
     lsof -i :5000
     kill -9 <PID>
     ```

3. **Missing Dependencies**
   - Install any missing packages using pip:
     ```bash
     pip install <package-name>
     ```

4. **File Permission Issues**
   - Ensure you have write permissions in the project directory
   - Run the terminal/command prompt as administrator if needed

## Additional Configuration

### Custom Port Configuration
To use a different port, modify the `port` value in `.streamlit/config.toml`:
```toml
[server]
port = <your-preferred-port>
```

### Development Mode
For development, you can enable debug mode in `.streamlit/config.toml`:
```toml
[server]
runOnSave = true
enableCORS = false
enableXsrfProtection = false
```

## Support
If you encounter any issues not covered in this guide, please:
1. Check the project's issue tracker
2. Review the error logs in `code_analysis.log`
3. Create a new issue with detailed error information
