"""
API Tools Module
Handles API development, testing, mocking, and performance testing
"""
import sys
import subprocess
import json
import requests
from pathlib import Path
from typing import List, Optional, Dict, Any
from core.menu import Menu, MenuItem
from core.security.validator import SecurityValidator


class APITools:
    """Handles API development and testing tasks"""

    def __init__(self):
        self.validator = SecurityValidator()

    def create_api_client(self) -> None:
        """Help create an API client for testing"""
        print("\n" + "="*70)
        print("API CLIENT GENERATOR")
        print("="*70)
        
        print("\nThis tool helps create an API client for testing your APIs.")
        
        api_base_url = input("Enter API base URL (e.g., http://localhost:8000/api/v1): ").strip()
        if not api_base_url:
            print("API base URL is required!")
            input("\nPress Enter to continue...")
            return
        
        # Validate URL
        if not api_base_url.startswith(('http://', 'https://')):
            print("Please enter a valid URL starting with http:// or https://")
            input("\nPress Enter to continue...")
            return
        
        print(f"\nExample API client code for {api_base_url}:")
        print("```python")
        print("# api_client.py")
        print("import requests")
        print("from typing import Dict, Any")
        print()
        print("class APIClient:")
        print(f"    BASE_URL = \"{api_base_url}\"")
        print()
        print("    def __init__(self, api_key: str = None):")
        print("        self.session = requests.Session()")
        print("        if api_key:")
        print("            self.session.headers.update({'Authorization': f'Bearer {api_key}'})")
        print()
        print("    def get(self, endpoint: str, params: Dict[str, Any] = None):")
        print("        url = f\"{api_base_url}/{endpoint.lstrip('/')}\"")
        print("        response = self.session.get(url, params=params)")
        print("        response.raise_for_status()")
        print("        return response.json()")
        print()
        print("    def post(self, endpoint: str, data: Dict[str, Any] = None):")
        print("        url = f\"{api_base_url}/{endpoint.lstrip('/')}\"")
        print("        response = self.session.post(url, json=data)")
        print("        response.raise_for_status()")
        print("        return response.json()")
        print()
        print("    def put(self, endpoint: str, data: Dict[str, Any] = None):")
        print("        url = f\"{api_base_url}/{endpoint.lstrip('/')}\"")
        print("        response = self.session.put(url, json=data)")
        print("        response.raise_for_status()")
        print("        return response.json()")
        print()
        print("    def delete(self, endpoint: str):")
        print("        url = f\"{api_base_url}/{endpoint.lstrip('/')}\"")
        print("        response = self.session.delete(url)")
        print("        response.raise_for_status()")
        print("        return response.json()")
        print("```")
        
        # Optionally create the file
        create_file = input("\nCreate api_client.py file? (y/n): ").lower()
        if create_file == 'y':
            client_content = f'''import requests
from typing import Dict, Any

class APIClient:
    BASE_URL = "{api_base_url}"

    def __init__(self, api_key: str = None):
        self.session = requests.Session()
        if api_key:
            self.session.headers.update({{'Authorization': f'Bearer {{api_key}}'}})

    def get(self, endpoint: str, params: Dict[str, Any] = None):
        url = f"{api_base_url}/{{endpoint.lstrip('/')}}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def post(self, endpoint: str, data: Dict[str, Any] = None):
        url = f"{api_base_url}/{{endpoint.lstrip('/')}}"
        response = self.session.post(url, json=data)
        response.raise_for_status()
        return response.json()

    def put(self, endpoint: str, data: Dict[str, Any] = None):
        url = f"{api_base_url}/{{endpoint.lstrip('/')}}"
        response = self.session.put(url, json=data)
        response.raise_for_status()
        return response.json()

    def delete(self, endpoint: str):
        url = f"{api_base_url}/{{endpoint.lstrip('/')}}"
        response = self.session.delete(url)
        response.raise_for_status()
        return response.json()

# Example usage:
if __name__ == "__main__":
    client = APIClient()
    # Example API call
    # data = client.get("/items")
    # print(data)
'''
            
            with open("api_client.py", "w") as f:
                f.write(client_content)
            
            print("✓ API client created as api_client.py")
        
        input("\nPress Enter to continue...")

    def test_api_endpoint(self) -> None:
        """Test an API endpoint"""
        print("\n" + "="*70)
        print("API ENDPOINT TESTING")
        print("="*70)
        
        api_url = input("Enter API endpoint URL: ").strip()
        if not api_url:
            print("API URL is required!")
            input("\nPress Enter to continue...")
            return
        
        # Validate URL
        if not api_url.startswith(('http://', 'https://')):
            print("Please enter a valid URL starting with http:// or https://")
            input("\nPress Enter to continue...")
            return
        
        method = input("HTTP method (GET, POST, PUT, DELETE) [default: GET]: ").strip().upper() or "GET"
        if method not in ["GET", "POST", "PUT", "DELETE"]:
            print("Invalid HTTP method. Using GET.")
            method = "GET"
        
        # Get headers
        headers = {}
        headers_input = input("Add headers? (format: key=value,key2=value2) [optional]: ").strip()
        if headers_input:
            try:
                for pair in headers_input.split(","):
                    key, value = pair.split("=", 1)
                    headers[key.strip()] = value.strip()
            except ValueError:
                print("Invalid header format. Continuing without headers.")
        
        # Get data for POST/PUT
        data = None
        if method in ["POST", "PUT"]:
            data_input = input("Request body (JSON format) [optional]: ").strip()
            if data_input:
                try:
                    data = json.loads(data_input)
                except json.JSONDecodeError:
                    print("Invalid JSON. Continuing without data.")
        
        try:
            print(f"\nMaking {method} request to: {api_url}")
            
            # Make the API call
            if method == "GET":
                response = requests.get(api_url, headers=headers)
            elif method == "POST":
                response = requests.post(api_url, json=data, headers=headers)
            elif method == "PUT":
                response = requests.put(api_url, json=data, headers=headers)
            elif method == "DELETE":
                response = requests.delete(api_url, headers=headers)
            
            print(f"\nResponse Status: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")
            try:
                response_json = response.json()
                print(f"Response JSON: {json.dumps(response_json, indent=2)}")
            except:
                print(f"Response Text: {response.text[:500]}")  # Limit output
                if len(response.text) > 500:
                    print("... (response truncated)")
        
        except requests.exceptions.RequestException as e:
            print(f"\nError making request: {e}")
        except Exception as e:
            print(f"\nUnexpected error: {e}")
        
        input("\nPress Enter to continue...")

    def mock_api_server(self) -> None:
        """Create a simple mock API server"""
        print("\n" + "="*70)
        print("MOCK API SERVER")
        print("="*70)
        
        print("\nThis creates a simple mock API server for frontend development.")
        print("It requires the 'flask' package.")
        
        # Check if Flask is available
        try:
            import flask
            print("✓ Flask is available")
        except ImportError:
            install = input("Flask is not installed. Install Flask? (y/n): ").lower()
            if install == 'y':
                try:
                    subprocess.run([sys.executable, "-m", "pip", "install", "flask"], check=True)
                    print("✓ Flask installed successfully")
                    import flask
                except subprocess.CalledProcessError:
                    print("⚠ Failed to install Flask")
                    input("\nPress Enter to continue...")
                    return
            else:
                print("Cannot create mock server without Flask.")
                input("\nPress Enter to continue...")
                return
        
        # Get mock configuration
        port = input("Enter port for mock server [default: 5000]: ").strip()
        port = int(port) if port.isdigit() else 5000
        
        print("\nCreating mock endpoints...")
        
        mock_content = f'''from flask import Flask, jsonify, request
import json
import os

app = Flask(__name__)

# Sample data
MOCK_DATA = {{
    "users": [
        {{"id": 1, "name": "John Doe", "email": "john@example.com"}},
        {{"id": 2, "name": "Jane Smith", "email": "jane@example.com"}}
    ],
    "items": [
        {{"id": 1, "name": "Sample Item", "price": 10.99}},
        {{"id": 2, "name": "Another Item", "price": 24.99}}
    ]
}}

@app.route('/users', methods=['GET'])
def get_users():
    return jsonify(MOCK_DATA['users'])

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = next((u for u in MOCK_DATA['users'] if u['id'] == user_id), None)
    if user:
        return jsonify(user)
    else:
        return jsonify({{'error': 'User not found'}}), 404

@app.route('/items', methods=['GET'])
def get_items():
    return jsonify(MOCK_DATA['items'])

@app.route('/items', methods=['POST'])
def create_item():
    data = request.get_json()
    # Add ID to item (in a real app, this would be generated)
    if data:
        data['id'] = len(MOCK_DATA['items']) + 1
        MOCK_DATA['items'].append(data)
        return jsonify(data), 201
    else:
        return jsonify({{'error': 'Invalid data'}}), 400

@app.route('/', methods=['GET'])
def home():
    return jsonify({{'message': 'Mock API Server is running!', 'endpoints': ['/users', '/items']}})

if __name__ == '__main__':
    print(f"Mock API Server running on http://localhost:{port}")
    app.run(debug=True, host='0.0.0.0', port={port})
'''
        
        # Create mock server file
        with open("mock_server.py", "w") as f:
            f.write(mock_content)
        
        print(f"\n✓ Mock API server created as mock_server.py")
        print(f"Run with: python mock_server.py")
        print(f"Access at: http://localhost:{port}")
        
        run_now = input(f"\nRun the mock server now? (y/n): ").lower()
        if run_now == 'y':
            try:
                # Run the server in background
                import threading
                import time
                
                def run_server():
                    exec(mock_content)
                
                server_thread = threading.Thread(target=run_server, daemon=True)
                server_thread.start()
                
                print(f"Mock server started in background on port {port}")
                print("Press Ctrl+C to stop the server")
                time.sleep(2)  # Give server a moment to start
            except Exception as e:
                print(f"Error running server: {e}")
                print(f"Try running manually: python mock_server.py")
        
        input("\nPress Enter to continue...")

    def run_api_load_test(self) -> None:
        """Run API load testing"""
        print("\n" + "="*70)
        print("API LOAD TESTING")
        print("="*70)
        
        print("\nThis feature would run load testing on your API.")
        print("For proper load testing, tools like 'locust' or 'wrk' are recommended.")
        
        # Check if Locust is available
        try:
            import locust
            print("✓ Locust is available")
        except ImportError:
            install = input("Locust is not installed. Install Locust? (y/n): ").lower()
            if install == 'y':
                try:
                    subprocess.run([sys.executable, "-m", "pip", "install", "locust"], check=True)
                    print("✓ Locust installed successfully")
                except subprocess.CalledProcessError:
                    print("⚠ Failed to install Locust")
        
        api_url = input("Enter API endpoint URL to test: ").strip()
        if not api_url:
            print("API URL is required!")
            input("\nPress Enter to continue...")
            return
        
        # Validate URL
        if not api_url.startswith(('http://', 'https://')):
            print("Please enter a valid URL starting with http:// or https://")
            input("\nPress Enter to continue...")
            return
        
        print(f"\nExample Locust test file for: {api_url}")
        print("```python")
        print("# locustfile.py")
        print("from locust import HttpUser, task, between")
        print()
        print(f"class APIUser(HttpUser):")
        print(f"    host = \"{api_url.rsplit('/', 1)[0]}\"  # Base URL")
        print(f"    wait_time = between(1, 3)  # Wait 1-3 seconds between requests")
        print()
        print(f"    @task")
        print(f"    def api_request(self):")
        print(f"        response = self.client.get(\"/{api_url.split('/')[-1]}\")")
        print(f"        print(f'Response: {{response.status_code}}')")
        print("```")
        
        print("\nTo run the load test:")
        print("1. Install Locust: pip install locust")
        print("2. Create the locustfile.py with the code above")
        print("3. Run: locust")
        print("4. Open http://localhost:8089 in your browser")
        print("5. Configure test parameters and start the test")
        
        create_locustfile = input("\nCreate example locustfile.py? (y/n): ").lower()
        if create_locustfile == 'y':
            # Determine base URL and endpoint
            if '/' in api_url:
                base_url = api_url.rsplit('/', 1)[0]
                endpoint = api_url.split('/')[-1]
            else:
                base_url = api_url
                endpoint = ""
            
            locust_content = f'''from locust import HttpUser, task, between

class APIUser(HttpUser):
    host = "{base_url}"
    wait_time = between(1, 3)  # Wait 1-3 seconds between requests

    @task
    def api_request(self):
        response = self.client.get("/{endpoint}")
        print(f"Response: {{response.status_code}}")
    
    @task
    def api_status_check(self):
        # Example of another common endpoint
        response = self.client.get("/health")
        print(f"Health check: {{response.status_code}}")
'''
            
            with open("locustfile.py", "w") as f:
                f.write(locust_content)
            
            print("✓ Example locustfile.py created")
        
        input("\nPress Enter to continue...")

    def generate_api_documentation(self) -> None:
        """Generate API documentation from code or OpenAPI spec"""
        print("\n" + "="*70)
        print("API DOCUMENTATION GENERATOR")
        print("="*70)
        
        print("\nAPI documentation generation depends on the framework used.")
        
        # Check for common API frameworks
        frameworks = []
        
        # Check for FastAPI
        try:
            import fastapi
            frameworks.append("FastAPI")
        except ImportError:
            pass
        
        # Check for Flask
        try:
            import flask
            frameworks.append("Flask")
        except ImportError:
            pass
        
        if frameworks:
            print(f"Detected frameworks: {', '.join(frameworks)}")
            
            if "FastAPI" in frameworks:
                print("\nFor FastAPI, automatic documentation is available at:")
                print("  - /docs (Swagger UI)")
                print("  - /redoc (ReDoc)")
                
            if "Flask" in frameworks:
                print("\nFor Flask, consider using:")
                print("  - Flask-Smorest (Flask + Marshmallow + OpenAPI)")
                print("  - Flasgger (Swagger UI for Flask)")
        else:
            print("\nNo common API frameworks detected.")
            print("Documentation generation requires framework-specific tools.")
        
        # Create sample OpenAPI spec
        create_openapi = input("\nCreate sample OpenAPI specification file? (y/n): ").lower()
        if create_openapi == 'y':
            openapi_spec = {
                "openapi": "3.0.0",
                "info": {
                    "title": "Sample API",
                    "description": "A sample API generated by Magic CLI",
                    "version": "1.0.0"
                },
                "paths": {
                    "/users": {
                        "get": {
                            "summary": "Get all users",
                            "responses": {
                                "200": {
                                    "description": "A list of users",
                                    "content": {
                                        "application/json": {
                                            "schema": {
                                                "type": "array",
                                                "items": {
                                                    "$ref": "#/components/schemas/User"
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        },
                        "post": {
                            "summary": "Create a user",
                            "requestBody": {
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "$ref": "#/components/schemas/User"
                                        }
                                    }
                                }
                            },
                            "responses": {
                                "201": {
                                    "description": "User created",
                                    "content": {
                                        "application/json": {
                                            "schema": {
                                                "$ref": "#/components/schemas/User"
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                "components": {
                    "schemas": {
                        "User": {
                            "type": "object",
                            "properties": {
                                "id": {
                                    "type": "integer",
                                    "example": 1
                                },
                                "name": {
                                    "type": "string",
                                    "example": "John Doe"
                                },
                                "email": {
                                    "type": "string",
                                    "format": "email",
                                    "example": "john@example.com"
                                }
                            },
                            "required": ["name", "email"]
                        }
                    }
                }
            }
            
            with open("openapi_spec.json", "w") as f:
                json.dump(openapi_spec, f, indent=2)
            
            print("✓ Sample OpenAPI specification created as openapi_spec.json")
        
        input("\nPress Enter to continue...")


class APIMenu(Menu):
    """Menu for API tools"""

    def __init__(self):
        self.api = APITools()
        super().__init__("API Development & Testing Tools")

    def setup_items(self) -> None:
        """Setup menu items for API tools"""
        self.items = [
            MenuItem("Create API Client", self.api.create_api_client),
            MenuItem("Test API Endpoint", self.api.test_api_endpoint),
            MenuItem("Create Mock API Server", self.api.mock_api_server),
            MenuItem("Run API Load Test", self.api.run_api_load_test),
            MenuItem("Generate API Documentation", self.api.generate_api_documentation),
            MenuItem("Back to Main Menu", lambda: "exit")
        ]