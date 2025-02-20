import os
import re
import json
from typing import Dict, List, Set, Optional, Tuple
from pathlib import Path
import logging
from dataclasses import dataclass
from datetime import datetime
import javalang
import networkx as nx

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

        # Add Java-specific patterns
        self.java_patterns = {
            'spring_endpoints': {
                'rest_endpoints': r'@(RestController|RequestMapping|GetMapping|PostMapping|PutMapping|DeleteMapping)',
                'feign_clients': r'@FeignClient',
                'eureka_client': r'@EnableEurekaClient|@EnableDiscoveryClient'
            },
            'messaging': {
                'jms': r'@JmsListener|MessageListener|JmsTemplate',
                'kafka': r'@KafkaListener|KafkaTemplate|@EnableKafka',
                'rabbitmq': r'@RabbitListener|RabbitTemplate|@EnableRabbit'
            },
            'security': {
                'spring_security': r'@EnableWebSecurity|@Secured|@PreAuthorize',
                'jwt': r'JwtToken|JwtUtils|SecurityContextHolder',
                'credentials': r'password\s*=|secret\s*=|key\s*='
            },
            'database': {
                'jpa': r'@Entity|@Repository|@Transactional',
                'sql_queries': r'@Query|createQuery|createNativeQuery'
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
            '.rb': 'Ruby',
            '.xsd': 'XSD',
            '.xml': 'XML',
            '.properties': 'Properties'
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
        code_files = []
        test_patterns = [
            'test_',
            '_test.',
            '/tests/',
            '/test/'
        ]

        for root, _, files in os.walk(self.repo_path):
            for file in files:
                file_path = Path(root) / file
                if any(pattern in str(file_path).lower() for pattern in test_patterns):
                    self.logger.info(f"Skipping test file: {file_path}")
                    continue

                if file_path.suffix in self.supported_extensions:
                    code_files.append(file_path)
        return code_files

    def analyze_file(self, file_path: Path) -> Dict:
        results = {
            'demographic_data': {},
            'integration_patterns': []
        }

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.readlines()

            for line_num, line in enumerate(content, 1):
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

                # Check for Java-specific patterns
                if file_path.suffix == '.java':
                    for pattern_category, sub_patterns in self.java_patterns.items():
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

    def analyze_java_file(self, file_path: Path) -> Dict:
        results = {
            'classes': [],
            'methods': [],
            'endpoints': [],
            'dependencies': []
        }

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            tree = javalang.parse.parse(content)

            for path, node in tree.filter(javalang.tree.ClassDeclaration):
                class_info = {
                    'name': node.name,
                    'extends': node.extends.name if node.extends else None,
                    'implements': [i.name for i in node.implements] if node.implements else [],
                    'annotations': [a.name for a in node.annotations] if node.annotations else []
                }
                results['classes'].append(class_info)

                for method in node.methods:
                    method_info = {
                        'name': method.name,
                        'return_type': method.return_type.name if method.return_type else None,
                        'parameters': [(param.type.name, param.name) for param in method.parameters],
                        'annotations': [a.name for a in method.annotations] if method.annotations else []
                    }
                    results['methods'].append(method_info)

                    if any(a.name in ['GetMapping', 'PostMapping', 'RequestMapping'] for a in method.annotations):
                        endpoint_info = {
                            'method': method.name,
                            'path': self._extract_mapping_path(method.annotations),
                            'http_method': self._extract_http_method(method.annotations)
                        }
                        results['endpoints'].append(endpoint_info)

        except Exception as e:
            self.logger.error(f"Error analyzing Java file {file_path}: {str(e)}")

        return results

    def _extract_mapping_path(self, annotations) -> str:
        for annotation in annotations:
            if hasattr(annotation, 'element') and annotation.element:
                for elem in annotation.element:
                    if isinstance(elem, javalang.tree.ElementValuePair):
                        if elem.value.value.startswith('/'):
                            return elem.value.value
        return ''

    def _extract_http_method(self, annotations) -> str:
        method_map = {
            'GetMapping': 'GET',
            'PostMapping': 'POST',
            'PutMapping': 'PUT',
            'DeleteMapping': 'DELETE'
        }
        for annotation in annotations:
            if annotation.name in method_map:
                return method_map[annotation.name]
        return 'GET'

    def update_results(self, main_results: Dict, file_results: Dict, file_path: Path):
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

        integration_patterns_count = len(file_results['integration_patterns'])
        main_results['integration_patterns'].extend(
            file_results['integration_patterns']
        )

        main_results['summary']['demographic_fields_found'] = sum(
            sum(len(data['occurrences']) for data in fields.values())
            for fields in main_results['demographic_data'].values()
        )
        main_results['summary']['integration_patterns_found'] = len(
            main_results['integration_patterns']
        )

        main_results['summary']['file_details'].append({
            'file_path': str(file_path),
            'demographic_fields_found': demographic_fields_count,
            'integration_patterns_found': integration_patterns_count
        })

    def generate_report(self, results: Dict):
        results['summary']['unique_demographic_fields'] = list(results['summary']['unique_demographic_fields'])

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        html_report = f'{self.app_name}_CodeLens_{timestamp}.html'
        self.generate_html_report(results, html_report)

        self.logger.info(f"Analysis report generated: {html_report}")

    def generate_html_report(self, results: Dict, filename: str):
        self.results = results
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

                {self._generate_field_frequency_html(results)}

                {self._generate_demographic_summary_html(results['summary']['file_details'])}
                {self._generate_integration_summary_html(results['summary']['file_details'])}
            </div>

            <div class="section">
                <h2>Demographic Data Fields by File</h2>
                {self._generate_demographic_html(results['demographic_data'])}
            </div>

            <div class="section">
                <h2>Integration Patterns</h2>
                {self._generate_integration_html(results['integration_patterns'])}
            </div>
            """
        java_files = [f for f in results['summary']['file_details'] if Path(f['file_path']).suffix == '.java']
        if java_files:
            html_content += f"""
                <div class="section">
                    <h2>Java Code Analysis</h2>
                    {self._generate_java_analysis_html(results)}
                </div>
                {self._generate_microservices_graph_html(results)}
            """

        html_content += """
        </body>
        </html>
        """

        with open(filename, 'w') as f:
            f.write(html_content)

    def _generate_demographic_summary_html(self, file_details: List[Dict]) -> str:
        demographic_files = [f for f in file_details if f['demographic_fields_found'] > 0]

        if not demographic_files:
            return ""

        html = """
        <h3>Demographic Fields Summary</h3>
        <table>
            <tr>
                <th>#</th>
                <th>File Analyzed</th>
                <th>Demographic Fields Occurrences</th>
                <th>Fields</th>
            </tr>
        """

        for index, file_detail in enumerate(demographic_files, 1):
            file_path = file_detail['file_path']
            unique_fields = []
            if file_path in self.results['demographic_data']:
                unique_fields = list(self.results['demographic_data'][file_path].keys())

            html += f"""
            <tr>
                <td>{index}</td>
                <td>{file_path}</td>
                <td>{file_detail['demographic_fields_found']}</td>
                <td>{', '.join(unique_fields)}</td>
            </tr>
            """
        return html + "</table>"

    def _generate_integration_summary_html(self, file_details: List[Dict]) -> str:
        integration_files = [f for f in file_details if f['integration_patterns_found'] > 0]

        if not integration_files:
            return ""

        html = """
        <h3>Integration Patterns Summary</h3>
        <table>
            <tr>
                <th>#</th>
                <th>File Name</th>
                <th>Integration Patterns Found</th>
                <th>Patterns Found Details</th>
            </tr>
        """

        for index, file_detail in enumerate(integration_files, 1):
            file_path = file_detail['file_path']
            pattern_details = set()
            for pattern in self.results['integration_patterns']:
                if pattern['file_path'] == file_path:
                    pattern_details.add(f"{pattern['pattern_type']}: {pattern['sub_type']}")

            html += f"""
            <tr>
                <td>{index}</td>
                <td>{file_detail['file_path']}</td>
                <td>{file_detail['integration_patterns_found']}</td>
                <td>{', '.join(pattern_details)}</td>
            </tr>
            """
        return html + "</table>"

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

    def _generate_field_frequency_html(self, results: Dict) -> str:
        field_frequencies = {}
        for file_data in results['demographic_data'].values():
            for field_name, data in file_data.items():
                if field_name not in field_frequencies:
                    field_frequencies[field_name] = {
                        'count': len(data['occurrences']),
                        'type': data['data_type']
                    }
                else:
                    field_frequencies[field_name]['count'] += len(data['occurrences'])

        html = """
        <div class="section">
            <h3>Field Frequency Analysis</h3>
            <p>Below table shows how many times each demographic field appears across all analyzed files:</p>
            <table>
                <tr>
                    <th style="width: 5%;">#</th>
                    <th style="width: 35%;">Field Name</th>
                    <th style="width: 30%;">Field Type</th>
                    <th style="width: 30%;">Total Occurrences</th>
                </tr>
        """

        for idx, (field_name, data) in enumerate(sorted(field_frequencies.items(), key=lambda x: x[1]['count'], reverse=True), 1):
            html += f"""
                <tr>
                    <td>{idx}</td>
                    <td>{field_name}</td>
                    <td>{data['type']}</td>
                    <td>{data['count']}</td>
                </tr>
            """

        html += """
            </table>
        </div>
        <br>
        """
        return html

    def _generate_java_analysis_html(self, results: Dict) -> str:
        html = "<h3>Java Components Analysis</h3>"
        for file_details in results['summary']['file_details']:
            file_path = file_details['file_path']
            if Path(file_path).suffix == '.java':
                java_analysis = next((item for item in results['demographic_data'].items() if item[0] == file_path), (None, None))[1]
                if java_analysis:
                    html += f"<h4>File: {file_path}</h4>"
                    html += "<table border='1'>"
                    html += "<tr><th>Class Name</th><th>Extends</th><th>Implements</th><th>Annotations</th></tr>"
                    for class_data in java_analysis['java_analysis']['classes']:
                        html += "<tr>"
                        html += f"<td>{class_data['name']}</td>"
                        html += f"<td>{class_data['extends']}</td>"
                        html += f"<td>{', '.join(class_data['implements'])}</td>"
                        html += f"<td>{', '.join(class_data['annotations'])}</td>"
                        html += "</tr>"
                    html += "</table>"
        return html



    def _generate_microservices_graph_html(self, results: Dict) -> str:
        # Placeholder for microservices graph generation.  Requires more complex logic to build the graph and render it in HTML.
        return """<p>Microservices graph visualization will be implemented in a future version.</p>"""


def main():
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
# - code_analysis_report_[timestamp].html