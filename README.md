```
Contents of `requirements.txt`:
```
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

### Fuzzy Matching Algorithms

The application uses three different fuzzy matching algorithms, each specialized for specific matching scenarios:

#### 1. Levenshtein Ratio (Basic)
- **What it does**: Calculates the minimum number of single-character edits required to change one string into another.
- **Best for**: 
  - Catching typos and minor spelling variations
  - Comparing strings of similar length
  - Finding exact matches with slight differences
- **Example**:
  ```python
  String 1: "customer_id"
  String 2: "customerid"
  Score: 90% (high match due to minimal character difference)
  ```

#### 2. Partial Ratio (Substring)
- **What it does**: Finds the best matching substring between two strings
- **Best for**:
  - Finding matches where one string is contained within another
  - Handling prefixes/suffixes
  - Matching partial attributes
- **Example**:
  ```python
  String 1: "customer_phone_number"
  String 2: "phone_number"
  Score: 100% (perfect substring match)
  ```

#### 3. Token Sort Ratio (Word Order)
- **What it does**: Sorts the words in both strings before comparing, making the comparison order-independent
- **Best for**:
  - Matching strings with words in different orders
  - Handling multi-word attributes
  - Finding semantic matches
- **Example**:
  ```python
  String 1: "first_name last_name"
  String 2: "last_name first_name"
  Score: 100% (perfect match despite different word order)
  ```

### Java Project Analysis Features

| Category | Feature | Description |
|----------|---------|-------------|
| 📂 Java Code Analysis | Extract Java Classes & Methods | Analyze class structure, method signatures, inheritance, and parameters. |
| | Track Function Calls & Dependencies | Identify interdependencies between classes, services, and functions. |
| | Extract API Endpoints & Services | Detect Spring Boot API endpoints, @RequestMapping, @GetMapping. |
| | Analyze JMS & Message Queues | Extract message-based communication, including JMS & Kafka usage. |
| | Identify Database Queries | Detect SQL queries inside Java services & repositories. |
| | Find Security Issues | Scan for hardcoded credentials, SQL injection risks, and bad authentication patterns. |

| 🔗 Microservices & API Tracking | Analyze REST API Calls | Identify external/internal API calls made via RestTemplate, FeignClient. |
| | Track Microservice Dependencies | Map how services communicate with each other (e.g., Eureka, Feign, Kafka). |
| | Generate Service-to-Service Graph | Visualize interaction between microservices in a Spring Boot project. |

| 📊 Diagram & Visualization | Generate UML Class Diagram | Convert Java classes & relationships into a UML diagram (PlantUML). |
| | Generate Function Call Graph | Show function dependencies and flow (Graphviz). |
| | Create Sequence Diagrams | Track function execution order using sequence diagrams. |

### Required Dependencies
Java analysis capabilities are powered by these Python packages:

| Functionality | Python Library | Installation |
|--------------|----------------|--------------|
| Java Code Parsing | javalang | `pip install javalang` |
| Bytecode Analysis | pyjvm | `pip install pyjvm` |
| UML Class Diagrams | plantuml | `pip install plantuml` |
| Sequence Diagrams | graphviz | `pip install graphviz` |
| Function Call Tracking | networkx | `pip install networkx` |
| Database & ORM Analysis | sqlalchemy | `pip install sqlalchemy` |
| Web Framework | Flask | `pip install flask` |
| Frontend UI (Optional) | Streamlit | `pip install streamlit` |

### Configuration
1. Ensure Java code files have proper package declarations
2. Spring Boot applications should follow standard conventions
3. Database configurations should be properly annotated

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