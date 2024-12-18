import os  
import re  
import json  
from typing import Dict, List, Set  
from pathlib import Path  
import logging  
from dataclasses import dataclass  
from datetime import datetime  

@dataclass  
class IntegrationPattern:  
    pattern_type: str  
    file_path: str  
    line_number: int  
    code_snippet: str  
    data_fields: Set[str]  

@dataclass  
class DemographicData:  
    field_name: str  
    data_type: str  
    occurrences: List[Dict]  

class CodeAnalyzer:  
    def __init__(self, repo_path: str, app_name: str):  
        self.repo_path = Path(repo_path)
        self.app_name = app_name
        self.setup_logging()  

        # Define demographic data patterns  
        self.demographic_patterns = {  
            'id': r'\b(customerId|cm_15)\b',
            'name': r'\b(first_name|last_name|full_name|name|amount)\b', 
            'address': r'\b(address|street|city|state|zip|postal_code)\b',  
            'contact': r'\b(phone|email|contact)\b',  
            'identity': r'\b(ssn|social_security|tax_id|passport)\b',  
            'demographics': r'\b(age|gender|dob|date_of_birth|nationality|ethnicity)\b'  
        }  
    
        self.integration_patterns = {
            'rest_api': {
                'http_methods': r'\b(get|post|put|delete|patch)\b.*\b(api|endpoint)\b',
                'url_patterns': r'https?://[^\s<>"]+|www\.[^\s<>"]+',
                'api_endpoints': r'@RequestMapping|@GetMapping|@PostMapping|@PutMapping|@DeleteMapping'
            },
            'soap_services': {
                'soap_components': r'\b(soap|wsdl|xml)\b',
                'wsdl': r'wsdl|WSDL|\.wsdl|getWSDL|WebService[Client]?',
                'soap_operations': r'SOAPMessage|SOAPEnvelope|SOAPBody|SOAPHeader|SoapClient|SoapBinding',
                'xml_namespaces': r'xmlns[:=]|namespace|schemaLocation',
                'soap_annotations': r'@WebService|@WebMethod|@SOAPBinding|@WebResult|@WebParam',
                'soap_endpoints': r'endpoint[_\s]?url|service[_\s]?url|wsdl[_\s]?url'
            },
            'database': {
                'sql_operations': r'\b(select|insert|update|delete)\s+from|into\b',
                'db_connections': r'jdbc:|connection[_\s]?string|database[_\s]?url'
            },
            'messaging': {
                'kafka': r'kafka|producer|consumer|topic',
                'rabbitmq': r'rabbitmq|amqp',
                'jms': r'jms|queue|topic'
            },
            'file':{
                'file_operations': r'\b(csv|excel|xlsx|json|properties).*(read|write|load|save)\b'
            }
        }
    
        # Supported file extensions
        self.supported_extensions = {  
            '.py': 'Python',  
            '.java': 'Java',  
            '.js': 'JavaScript',  
            '.ts': 'TypeScript',  
            '.cs': 'C#',  
            '.php': 'PHP',  
            '.rb': 'Ruby'  
        }  

    def setup_logging(self):  
        logging.basicConfig(  
            level=logging.INFO,  
            format='%(asctime)s - %(levelname)s - %(message)s',  
            handlers=[  
                logging.FileHandler('code_analysis.log'),  
                logging.StreamHandler()  
            ]  
        )  
        self.logger = logging.getLogger(__name__)  

    def scan_repository(self) -> Dict:  
        """  
        Main method to scan the repository and analyze code  
        """  
        results = {
            'metadata': {
                'application_name': self.app_name,
                'scan_timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'repository_path': str(self.repo_path)
            },
            'demographic_data': {},
            'integration_patterns': [],
            'summary': {
                'files_analyzed': 0,
                'unique_demographic_fields': set(),
                'demographic_fields_found': 0,
                'integration_patterns_found': 0,
                'file_details': []
            }  
        }  

        try:  
            for file_path in self.get_code_files():  
                self.logger.info(f"Analyzing file: {file_path}")  
                file_results = self.analyze_file(file_path)  
                self.update_results(results, file_results, file_path)  
                results['summary']['files_analyzed'] += 1  

            self.generate_report(results)  
            return results  

        except Exception as e:  
            self.logger.error(f"Error during repository scan: {str(e)}")  
            raise  

    def get_code_files(self) -> List[Path]:  
        """  
        Get all supported code files in the repository  
        """  
        code_files = []  
        for root, _, files in os.walk(self.repo_path):  
            for file in files:  
                file_path = Path(root) / file  
                if file_path.suffix in self.supported_extensions:  
                    code_files.append(file_path)  
        return code_files  

    def analyze_file(self, file_path: Path) -> Dict:  
        """  
        Analyze a single file for demographic data and integration patterns  
        """  
        results = {  
            'demographic_data': {},  
            'integration_patterns': []  
        }  

        try:  
            with open(file_path, 'r', encoding='utf-8') as f:  
                content = f.readlines()  

            for line_num, line in enumerate(content, 1):  
                # Check for demographic data  
                for data_type, pattern in self.demographic_patterns.items():  
                    matches = re.finditer(pattern, line, re.IGNORECASE)  
                    for match in matches:  
                        field_name = match.group(0)  
                        if str(file_path) not in results['demographic_data']:  
                            results['demographic_data'][str(file_path)] = {}  
                        if field_name not in results['demographic_data'][str(file_path)]:  
                            results['demographic_data'][str(file_path)][field_name] = {  
                                'data_type': data_type,  
                                'occurrences': []  
                            }  
                        results['demographic_data'][str(file_path)][field_name]['occurrences'].append({  
                            'line_number': line_num,  
                            'code_snippet': line.strip()  
                        })  

                # Check for integration patterns  
                for pattern_category, sub_patterns in self.integration_patterns.items():
                    for sub_type, pattern in sub_patterns.items():
                        if re.search(pattern, line, re.IGNORECASE):
                            results['integration_patterns'].append({
                                'pattern_type': pattern_category,
                                'sub_type': sub_type,
                                'file_path': str(file_path),
                                'line_number': line_num,
                                'code_snippet': line.strip()
                            })

        except Exception as e:  
            self.logger.error(f"Error analyzing file {file_path}: {str(e)}")  

        return results  

    def update_results(self, main_results: Dict, file_results: Dict, file_path: Path):  
        """  
        Update the main results dictionary with results from a single file  
        """  
        # Update demographic data  
        demographic_fields_count = 0  
        for file, fields in file_results['demographic_data'].items():  
            if file not in main_results['demographic_data']:  
                main_results['demographic_data'][file] = fields  
            else:  
                for field_name, data in fields.items():  
                    if field_name not in main_results['demographic_data'][file]:  
                        main_results['demographic_data'][file][field_name] = data  
                    else:  
                        main_results['demographic_data'][file][field_name]['occurrences'].extend(data['occurrences'])  
            demographic_fields_count += sum(len(data['occurrences']) for data in fields.values())  
            main_results['summary']['unique_demographic_fields'].update(fields.keys())  

        # Update integration patterns  
        integration_patterns_count = len(file_results['integration_patterns'])  
        main_results['integration_patterns'].extend(  
            file_results['integration_patterns']  
        )  

        # Update summary  
        main_results['summary']['demographic_fields_found'] = sum(  
            sum(len(data['occurrences']) for data in fields.values())  
            for fields in main_results['demographic_data'].values()  
        )  
        main_results['summary']['integration_patterns_found'] = len(  
            main_results['integration_patterns']  
        )  

        # Add file details to summary  
        main_results['summary']['file_details'].append({  
            'file_path': str(file_path),  
            'demographic_fields_found': demographic_fields_count,  
            'integration_patterns_found': integration_patterns_count  
        })  

    def generate_report(self, results: Dict):  
        """  
        Generate a detailed report of the analysis  
        """  
        # Convert the set of unique demographic fields to a list for JSON serialization  
        results['summary']['unique_demographic_fields'] = list(results['summary']['unique_demographic_fields'])  

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')  
        report_file = f'{self.app_name}_code_analysis_{timestamp}.json'  

        with open(report_file, 'w') as f:  
            json.dump(results, f, indent=2)  

        # Generate HTML report for better visualization  
        html_report = f'{self.app_name}_code_analysis_{timestamp}.html'  
        self.generate_html_report(results, html_report)  

        self.logger.info(f"Analysis reports generated: {report_file} and {html_report}")  

    def generate_html_report(self, results: Dict, filename: str):  
        """  
        Generate an HTML report for better visualization  
        """  
        unique_fields = list(results['summary']['unique_demographic_fields'])  
        html_content = f"""  
        <!DOCTYPE html>  
        <html>  
        <head>  
            <title>{self.app_name} - Code Analysis Report</title>  
            <style>  
                body {{ font-family: Arial, sans-serif; margin: 20px; }}  
                .section {{ margin-bottom: 30px; }}  
                .pattern {{ margin-bottom: 20px; padding: 10px; border: 1px solid #ddd; }}  
                .code {{ background-color: #f5f5f5; padding: 10px; }}  
                table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; }}  
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}  
                th {{ background-color: #f2f2f2; }}
                .metadata {{ background-color: #e9ecef; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}  
            </style>  
        </head>  
        <body>  
            <div class="header">
                <h1>{self.app_name} - Code Analysis Report</h1>
                <div class="metadata">
                    <p><strong>Application Name:</strong> {results['metadata']['application_name']}</p>
                    <p><strong>Generated:</strong> {results['metadata']['scan_timestamp']}</p>
                    <p><strong>Repository Path:</strong> {results['metadata']['repository_path']}</p>
                </div>
            </div>
            <div class="section">  
                <h2>Summary</h2>  
                <p>Files Analyzed: {results['summary']['files_analyzed']}</p>  
                <p>Unique Demographic Fields: {len(unique_fields)} [{', '.join(unique_fields)}]</p>  
                <p>Demographic Fields Occurrences Found: {results['summary']['demographic_fields_found']}</p>  
                <p>Integration Patterns Found: {results['summary']['integration_patterns_found']}</p>  
                <h3>File-wise Summary</h3>  
                <table>  
                    <tr>  
                        <th>#</th>  
                        <th>File Analyzed</th>  
                        <th>Demographic Fields Occurrences Found</th>  
                        <th>Integration Patterns Found</th>  
                    </tr>  
                    {self._generate_file_summary_html(results['summary']['file_details'])}  
                </table>  
            </div>  

            <div class="section">  
                <h2>Demographic Data Fields by File</h2>  
                {self._generate_demographic_html(results['demographic_data'])}  
            </div>  

            <div class="section">  
                <h2>Integration Patterns</h2>  
                {self._generate_integration_html(results['integration_patterns'])}  
            </div>  
        </body>  
        </html>  
        """  

        with open(filename, 'w') as f:  
            f.write(html_content)  

    def _generate_file_summary_html(self, file_details: List[Dict]) -> str:  
        html = ""  
        for index, file_detail in enumerate(file_details, 1):  
            html += f"""  
            <tr>  
                <td>{index}</td>  
                <td>{file_detail['file_path']}</td>  
                <td>{file_detail['demographic_fields_found']}</td>  
                <td>{file_detail['integration_patterns_found']}</td>  
            </tr>  
            """  
        return html  

    def _generate_demographic_html(self, demographic_data: Dict) -> str:  
        html = ""  
        for file_path, fields in demographic_data.items():  
            html += f"<h3>File: {file_path}</h3>"  
            for field_name, data in fields.items():  
                html += f"""  
                <div class="pattern">  
                    <h4>Field: {field_name} (Type: {data['data_type']})</h4>  
                    """  
                for occurrence in data['occurrences']:  
                    html += f"""  
                    <div class="code">  
                        <p>Line {occurrence['line_number']}: {occurrence['code_snippet']}</p>  
                    </div>  
                    """  
                html += "</div>"  
        return html  

    def _generate_integration_html(self, integration_patterns: List) -> str:  
        html = ""  
        for pattern in integration_patterns:  
            html += f"""  
            <div class="pattern">
                <h3>Pattern Type: {pattern['pattern_type']}</h3>
                <p>Sub Type: {pattern['sub_type']}</p>
                <p>File: {pattern['file_path']}</p>
                <p>Line: {pattern['line_number']}</p>
                <div class="code">
                    <p>{pattern['code_snippet']}</p>
                </div>
            </div>
            """  
        return html  

def main():  
    """
    Main function to run the code analyzer
    """
    app_name = input("Enter Application/Repository Name: ")
    repo_path = input("Enter the path to your code repository: ")
    
    try:
        analyzer = CodeAnalyzer(repo_path, app_name)  
        results = analyzer.scan_repository()  
        print(f"Analysis complete. Check the generated reports for details.")  
    except Exception as e:
       print(f"Error during analysis: {str(e)}")

if __name__ == "__main__":  
    main()  

# Created/Modified files during execution:  
# - code_analysis.log  
# - code_analysis_report_[timestamp].json  
# - code_analysis_report_[timestamp].html  