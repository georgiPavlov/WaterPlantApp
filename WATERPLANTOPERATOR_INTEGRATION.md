# WaterPlantOperator Integration Guide

## Overview
This guide provides comprehensive information on integrating WaterPlantOperator (Raspberry Pi client) with WaterPlantApp (Django server). The integration enables seamless communication between the central server and multiple plant automation devices.

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Communication Protocol](#communication-protocol)
3. [Device Registration](#device-registration)
4. [Data Synchronization](#data-synchronization)
5. [Plan Execution](#plan-execution)
6. [Error Handling](#error-handling)
7. [Security Considerations](#security-considerations)
8. [Testing Integration](#testing-integration)
9. [Troubleshooting](#troubleshooting)
10. [Best Practices](#best-practices)

## Architecture Overview

### System Components
```
┌─────────────────┐    HTTP/HTTPS    ┌─────────────────┐
│ WaterPlantApp   │◄─────────────────►│ WaterPlantOperator│
│ (Django Server) │                   │ (Raspberry Pi)   │
│                 │                   │                 │
│ • Device Mgmt   │                   │ • Pump Control  │
│ • Plan Storage  │                   │ • Sensor Reading│
│ • Status Track  │                   │ • Photo Capture │
│ • User Interface│                   │ • Local Storage │
└─────────────────┘                   └─────────────────┘
```

### Data Flow
1. **Device Registration**: WaterPlantOperator registers with WaterPlantApp
2. **Health Checks**: Regular status updates from device to server
3. **Plan Retrieval**: Device fetches watering plans from server
4. **Plan Execution**: Device executes plans and reports results
5. **Data Upload**: Device uploads sensor data and photos to server

## Communication Protocol

### Base Configuration
```python
# WaterPlantOperator configuration
SERVER_URL = "http://your-server.com"  # or https://your-server.com
DEVICE_ID = "DEVICE_001"
DEVICE_KEY = "your_device_secret_key"
API_VERSION = "v1"
BASE_ENDPOINT = f"{SERVER_URL}/api/{API_VERSION}"
```

### Authentication Headers
```python
headers = {
    'Content-Type': 'application/json',
    'X-Device-ID': DEVICE_ID,
    'X-Device-Key': DEVICE_KEY,
    'User-Agent': 'WaterPlantOperator/1.0'
}
```

### Request/Response Format
All API communication uses JSON format:
```json
{
  "device_id": "DEVICE_001",
  "timestamp": "2023-01-01T12:00:00Z",
  "data": {
    // Request-specific data
  }
}
```

## Device Registration

### Initial Registration
When a WaterPlantOperator device first connects, it must register with the server:

```python
import requests
import json
from datetime import datetime

def register_device(server_url, device_id, device_key, device_info):
    """Register device with WaterPlantApp server."""
    url = f"{server_url}/api/v1/devices/register/"
    
    payload = {
        "device_id": device_id,
        "label": device_info.get("label", f"Device {device_id}"),
        "water_level": device_info.get("water_level", 100),
        "moisture_level": device_info.get("moisture_level", 0),
        "water_container_capacity": device_info.get("capacity", 2000),
        "status": "online",
        "device_info": {
            "hardware_version": device_info.get("hw_version", "1.0"),
            "software_version": device_info.get("sw_version", "1.0"),
            "raspberry_pi_model": device_info.get("pi_model", "Pi 4"),
            "camera_available": device_info.get("camera", True),
            "sensors": device_info.get("sensors", ["moisture", "water_level"])
        }
    }
    
    headers = {
        'Content-Type': 'application/json',
        'X-Device-ID': device_id,
        'X-Device-Key': device_key
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 201:
            print(f"Device {device_id} registered successfully")
            return response.json()
        elif response.status_code == 200:
            print(f"Device {device_id} already exists, updated")
            return response.json()
        else:
            print(f"Registration failed: {response.status_code} - {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Registration error: {e}")
        return None

# Usage
device_info = {
    "label": "Living Room Plant",
    "water_level": 75,
    "moisture_level": 45,
    "capacity": 2000,
    "hw_version": "1.2",
    "sw_version": "1.0",
    "pi_model": "Pi 4",
    "camera": True,
    "sensors": ["moisture", "water_level", "temperature"]
}

result = register_device(
    server_url="http://localhost:8000",
    device_id="DEVICE_001",
    device_key="device_secret_key",
    device_info=device_info
)
```

### Device Authentication
After registration, devices authenticate using device-specific keys:

```python
def authenticate_device(server_url, device_id, device_key):
    """Authenticate device with server."""
    url = f"{server_url}/api/v1/auth/device/"
    
    payload = {
        "device_id": device_id,
        "device_key": device_key
    }
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            return data.get('token')
        else:
            print(f"Authentication failed: {response.status_code}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Authentication error: {e}")
        return None
```

## Data Synchronization

### Health Check Updates
Devices should send regular health checks to maintain connection:

```python
def send_health_check(server_url, device_id, device_key, status_data):
    """Send health check to server."""
    url = f"{server_url}/api/v1/devices/{device_id}/health/"
    
    payload = {
        "status": "online",
        "water_level": status_data.get("water_level"),
        "moisture_level": status_data.get("moisture_level"),
        "battery_level": status_data.get("battery_level"),
        "signal_strength": status_data.get("signal_strength"),
        "uptime": status_data.get("uptime"),
        "last_watering": status_data.get("last_watering"),
        "sensor_status": {
            "moisture_sensor": status_data.get("moisture_sensor_ok", True),
            "water_sensor": status_data.get("water_sensor_ok", True),
            "camera": status_data.get("camera_ok", True),
            "pump": status_data.get("pump_ok", True)
        }
    }
    
    headers = {
        'Content-Type': 'application/json',
        'X-Device-ID': device_id,
        'X-Device-Key': device_key
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Health check failed: {response.status_code}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Health check error: {e}")
        return None

# Usage
status_data = {
    "water_level": 75,
    "moisture_level": 45,
    "battery_level": 85,
    "signal_strength": -45,
    "uptime": "2 days, 5 hours",
    "last_watering": "2023-01-01T10:00:00Z",
    "moisture_sensor_ok": True,
    "water_sensor_ok": True,
    "camera_ok": True,
    "pump_ok": True
}

result = send_health_check(
    server_url="http://localhost:8000",
    device_id="DEVICE_001",
    device_key="device_secret_key",
    device_info=status_data
)
```

### Sensor Data Upload
Upload sensor readings to the server:

```python
def upload_sensor_data(server_url, device_id, device_key, sensor_data):
    """Upload sensor data to server."""
    url = f"{server_url}/api/v1/devices/{device_id}/sensor-data/"
    
    payload = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "sensors": {
            "moisture": {
                "value": sensor_data.get("moisture_value"),
                "percentage": sensor_data.get("moisture_percentage"),
                "unit": "percentage"
            },
            "water_level": {
                "value": sensor_data.get("water_level_value"),
                "percentage": sensor_data.get("water_level_percentage"),
                "unit": "percentage"
            },
            "temperature": {
                "value": sensor_data.get("temperature_value"),
                "unit": "celsius"
            },
            "humidity": {
                "value": sensor_data.get("humidity_value"),
                "unit": "percentage"
            }
        }
    }
    
    headers = {
        'Content-Type': 'application/json',
        'X-Device-ID': device_id,
        'X-Device-Key': device_key
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 201:
            return response.json()
        else:
            print(f"Sensor data upload failed: {response.status_code}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Sensor data upload error: {e}")
        return None
```

## Plan Execution

### Fetching Plans
Retrieve watering plans from the server:

```python
def get_watering_plans(server_url, device_id, device_key):
    """Get watering plans from server."""
    url = f"{server_url}/api/v1/devices/{device_id}/plans/"
    
    headers = {
        'Content-Type': 'application/json',
        'X-Device-ID': device_id,
        'X-Device-Key': device_key
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to get plans: {response.status_code}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Get plans error: {e}")
        return None

# Usage
plans = get_watering_plans(
    server_url="http://localhost:8000",
    device_id="DEVICE_001",
    device_key="device_secret_key"
)

if plans:
    for plan in plans:
        print(f"Plan: {plan['name']} - Type: {plan['plan_type']}")
        if plan['plan_type'] == 'basic':
            print(f"  Water Volume: {plan['water_volume']}ml")
        elif plan['plan_type'] == 'moisture':
            print(f"  Moisture Threshold: {plan['moisture_threshold']}")
            print(f"  Check Interval: {plan['check_interval']} minutes")
        elif plan['plan_type'] == 'time_based':
            print(f"  Water Times: {len(plan.get('water_times', []))}")
```

### Plan Execution Reporting
Report plan execution results to the server:

```python
def report_plan_execution(server_url, device_id, device_key, execution_result):
    """Report plan execution result to server."""
    url = f"{server_url}/api/v1/statuses/"
    
    payload = {
        "message": execution_result.get("message"),
        "status_type": "success" if execution_result.get("success") else "error",
        "device": device_id,
        "execution_details": {
            "plan_id": execution_result.get("plan_id"),
            "plan_name": execution_result.get("plan_name"),
            "water_volume": execution_result.get("water_volume"),
            "execution_time": execution_result.get("execution_time"),
            "moisture_before": execution_result.get("moisture_before"),
            "moisture_after": execution_result.get("moisture_after"),
            "water_level_before": execution_result.get("water_level_before"),
            "water_level_after": execution_result.get("water_level_after")
        }
    }
    
    headers = {
        'Content-Type': 'application/json',
        'X-Device-ID': device_id,
        'X-Device-Key': device_key
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 201:
            return response.json()
        else:
            print(f"Plan execution report failed: {response.status_code}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Plan execution report error: {e}")
        return None

# Usage
execution_result = {
    "success": True,
    "message": "Watering completed successfully",
    "plan_id": 1,
    "plan_name": "Morning Watering",
    "water_volume": 150,
    "execution_time": "2023-01-01T12:00:00Z",
    "moisture_before": 30,
    "moisture_after": 65,
    "water_level_before": 80,
    "water_level_after": 70
}

result = report_plan_execution(
    server_url="http://localhost:8000",
    device_id="DEVICE_001",
    device_key="device_secret_key",
    execution_result=execution_result
)
```

## Error Handling

### Network Error Handling
Implement robust error handling for network issues:

```python
import time
import logging
from requests.exceptions import RequestException, Timeout, ConnectionError

def robust_api_call(func, max_retries=3, retry_delay=5):
    """Wrapper for robust API calls with retry logic."""
    for attempt in range(max_retries):
        try:
            result = func()
            if result is not None:
                return result
        except (ConnectionError, Timeout) as e:
            logging.warning(f"Network error (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay * (attempt + 1))  # Exponential backoff
        except RequestException as e:
            logging.error(f"Request error: {e}")
            break
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            break
    
    logging.error("All retry attempts failed")
    return None

# Usage
def get_plans_with_retry():
    return get_watering_plans(
        server_url="http://localhost:8000",
        device_id="DEVICE_001",
        device_key="device_secret_key"
    )

plans = robust_api_call(get_plans_with_retry)
```

### Offline Mode
Handle offline scenarios gracefully:

```python
import json
import os
from datetime import datetime, timedelta

class OfflineManager:
    def __init__(self, data_dir="/tmp/waterplant_offline"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
    
    def save_offline_data(self, data_type, data):
        """Save data for offline processing."""
        timestamp = datetime.utcnow().isoformat()
        filename = f"{data_type}_{timestamp}.json"
        filepath = os.path.join(self.data_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(data, f)
    
    def get_pending_data(self, data_type):
        """Get pending data for upload."""
        pending_files = []
        for filename in os.listdir(self.data_dir):
            if filename.startswith(data_type):
                filepath = os.path.join(self.data_dir, filename)
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    pending_files.append((filepath, data))
        
        return pending_files
    
    def upload_pending_data(self, upload_func):
        """Upload all pending data."""
        for data_type in ['sensor_data', 'execution_results', 'health_checks']:
            pending = self.get_pending_data(data_type)
            for filepath, data in pending:
                try:
                    if upload_func(data_type, data):
                        os.remove(filepath)  # Remove after successful upload
                except Exception as e:
                    logging.error(f"Failed to upload {data_type}: {e}")

# Usage
offline_manager = OfflineManager()

# Save data when offline
offline_manager.save_offline_data('sensor_data', sensor_data)
offline_manager.save_offline_data('execution_results', execution_result)

# Upload pending data when back online
def upload_data(data_type, data):
    if data_type == 'sensor_data':
        return upload_sensor_data(server_url, device_id, device_key, data)
    elif data_type == 'execution_results':
        return report_plan_execution(server_url, device_id, device_key, data)
    return False

offline_manager.upload_pending_data(upload_data)
```

## Security Considerations

### Device Key Management
```python
import hashlib
import secrets
from cryptography.fernet import Fernet

class DeviceSecurity:
    def __init__(self, device_id):
        self.device_id = device_id
        self.key_file = f"/etc/waterplant/{device_id}.key"
    
    def generate_device_key(self):
        """Generate a secure device key."""
        return secrets.token_urlsafe(32)
    
    def load_device_key(self):
        """Load device key from secure storage."""
        try:
            with open(self.key_file, 'r') as f:
                return f.read().strip()
        except FileNotFoundError:
            return None
    
    def save_device_key(self, key):
        """Save device key to secure storage."""
        os.makedirs(os.path.dirname(self.key_file), exist_ok=True)
        with open(self.key_file, 'w') as f:
            f.write(key)
        os.chmod(self.key_file, 0o600)  # Read/write for owner only
    
    def encrypt_sensitive_data(self, data, key):
        """Encrypt sensitive data before transmission."""
        fernet = Fernet(key)
        encrypted_data = fernet.encrypt(json.dumps(data).encode())
        return encrypted_data.decode()
    
    def decrypt_sensitive_data(self, encrypted_data, key):
        """Decrypt sensitive data after reception."""
        fernet = Fernet(key)
        decrypted_data = fernet.decrypt(encrypted_data.encode())
        return json.loads(decrypted_data.decode())
```

### Certificate Validation
```python
import ssl
import certifi

def create_secure_session():
    """Create a secure requests session with certificate validation."""
    session = requests.Session()
    
    # Use certifi for certificate validation
    session.verify = certifi.where()
    
    # Set secure SSL context
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = True
    ssl_context.verify_mode = ssl.CERT_REQUIRED
    
    # Configure session for security
    session.headers.update({
        'User-Agent': 'WaterPlantOperator/1.0',
        'Accept': 'application/json',
        'Connection': 'close'  # Prevent connection reuse
    })
    
    return session

# Usage
secure_session = create_secure_session()
response = secure_session.get("https://your-server.com/api/v1/health/")
```

## Testing Integration

### Mock Server for Testing
```python
from unittest.mock import Mock, patch
import json

class MockWaterPlantApp:
    def __init__(self):
        self.devices = {}
        self.plans = {}
        self.statuses = []
    
    def register_device(self, device_data):
        device_id = device_data['device_id']
        self.devices[device_id] = device_data
        return {"status": "registered", "device_id": device_id}
    
    def get_plans(self, device_id):
        return self.plans.get(device_id, [])
    
    def add_plan(self, device_id, plan_data):
        if device_id not in self.plans:
            self.plans[device_id] = []
        self.plans[device_id].append(plan_data)
        return {"status": "plan_added"}
    
    def add_status(self, status_data):
        self.statuses.append(status_data)
        return {"status": "status_added"}

# Test integration
def test_device_integration():
    mock_server = MockWaterPlantApp()
    
    # Test device registration
    device_data = {
        "device_id": "TEST_DEVICE_001",
        "label": "Test Device",
        "water_level": 75,
        "moisture_level": 45,
        "water_container_capacity": 2000,
        "status": "online"
    }
    
    result = mock_server.register_device(device_data)
    assert result["status"] == "registered"
    
    # Test plan retrieval
    plans = mock_server.get_plans("TEST_DEVICE_001")
    assert plans == []
    
    # Test plan addition
    plan_data = {
        "name": "Test Plan",
        "plan_type": "basic",
        "water_volume": 150
    }
    
    result = mock_server.add_plan("TEST_DEVICE_001", plan_data)
    assert result["status"] == "plan_added"
    
    # Test status reporting
    status_data = {
        "message": "Test status",
        "status_type": "success"
    }
    
    result = mock_server.add_status(status_data)
    assert result["status"] == "status_added"

test_device_integration()
```

### Integration Test Suite
```python
import pytest
import requests_mock

@pytest.fixture
def mock_server():
    with requests_mock.Mocker() as m:
        # Mock device registration
        m.post('http://localhost:8000/api/v1/devices/register/', 
               json={"status": "registered", "device_id": "TEST_DEVICE_001"})
        
        # Mock plan retrieval
        m.get('http://localhost:8000/api/v1/devices/TEST_DEVICE_001/plans/',
              json=[{
                  "id": 1,
                  "name": "Test Plan",
                  "plan_type": "basic",
                  "water_volume": 150
              }])
        
        # Mock status reporting
        m.post('http://localhost:8000/api/v1/statuses/',
               json={"status": "status_added"})
        
        yield m

def test_device_registration(mock_server):
    result = register_device(
        server_url="http://localhost:8000",
        device_id="TEST_DEVICE_001",
        device_key="test_key",
        device_info={"label": "Test Device"}
    )
    assert result["status"] == "registered"

def test_plan_retrieval(mock_server):
    plans = get_watering_plans(
        server_url="http://localhost:8000",
        device_id="TEST_DEVICE_001",
        device_key="test_key"
    )
    assert len(plans) == 1
    assert plans[0]["name"] == "Test Plan"

def test_status_reporting(mock_server):
    result = report_plan_execution(
        server_url="http://localhost:8000",
        device_id="TEST_DEVICE_001",
        device_key="test_key",
        execution_result={"success": True, "message": "Test execution"}
    )
    assert result["status"] == "status_added"
```

## Troubleshooting

### Common Issues and Solutions

#### 1. Connection Timeout
```python
# Increase timeout for slow connections
response = requests.post(url, json=payload, headers=headers, timeout=60)

# Implement connection pooling
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

session = requests.Session()
retry_strategy = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("http://", adapter)
session.mount("https://", adapter)
```

#### 2. Authentication Failures
```python
def validate_device_credentials(device_id, device_key):
    """Validate device credentials before making requests."""
    if not device_id or not device_key:
        raise ValueError("Device ID and key are required")
    
    if len(device_key) < 16:
        raise ValueError("Device key must be at least 16 characters")
    
    return True
```

#### 3. Data Synchronization Issues
```python
def sync_device_data(server_url, device_id, device_key):
    """Synchronize all device data with server."""
    sync_operations = [
        ("health_check", send_health_check),
        ("sensor_data", upload_sensor_data),
        ("plans", get_watering_plans),
        ("statuses", get_device_statuses)
    ]
    
    results = {}
    for operation_name, operation_func in sync_operations:
        try:
            result = operation_func(server_url, device_id, device_key)
            results[operation_name] = result
        except Exception as e:
            logging.error(f"Sync operation {operation_name} failed: {e}")
            results[operation_name] = None
    
    return results
```

#### 4. Network Connectivity Issues
```python
import socket
import subprocess

def check_network_connectivity(host, port=80):
    """Check if network connection is available."""
    try:
        socket.create_connection((host, port), timeout=5)
        return True
    except OSError:
        return False

def check_internet_connectivity():
    """Check if internet connection is available."""
    try:
        subprocess.run(['ping', '-c', '1', '8.8.8.8'], 
                      capture_output=True, timeout=5)
        return True
    except subprocess.TimeoutExpired:
        return False

def wait_for_connectivity(server_url, max_wait=300):
    """Wait for network connectivity to be restored."""
    import time
    
    start_time = time.time()
    while time.time() - start_time < max_wait:
        if check_network_connectivity(server_url):
            return True
        time.sleep(10)
    
    return False
```

## Best Practices

### 1. Error Handling
- Always implement try-catch blocks for network operations
- Use exponential backoff for retry logic
- Log all errors with appropriate detail levels
- Implement graceful degradation for offline scenarios

### 2. Data Management
- Cache frequently accessed data locally
- Implement data compression for large payloads
- Use batch operations when possible
- Validate data before transmission

### 3. Security
- Use HTTPS for all communications
- Implement device key rotation
- Validate server certificates
- Encrypt sensitive data

### 4. Performance
- Use connection pooling
- Implement request batching
- Cache responses when appropriate
- Monitor and log performance metrics

### 5. Monitoring
- Implement health checks
- Monitor network connectivity
- Track API response times
- Log all important events

### 6. Configuration Management
```python
import configparser
import os

class ConfigManager:
    def __init__(self, config_file="/etc/waterplant/config.ini"):
        self.config = configparser.ConfigParser()
        self.config_file = config_file
        self.load_config()
    
    def load_config(self):
        """Load configuration from file."""
        if os.path.exists(self.config_file):
            self.config.read(self.config_file)
        else:
            self.create_default_config()
    
    def create_default_config(self):
        """Create default configuration."""
        self.config['SERVER'] = {
            'url': 'http://localhost:8000',
            'timeout': '30',
            'retry_attempts': '3'
        }
        
        self.config['DEVICE'] = {
            'id': 'DEVICE_001',
            'key': 'device_secret_key',
            'health_check_interval': '300'
        }
        
        self.config['SENSORS'] = {
            'moisture_check_interval': '60',
            'water_level_check_interval': '120',
            'photo_interval': '3600'
        }
        
        self.save_config()
    
    def save_config(self):
        """Save configuration to file."""
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        with open(self.config_file, 'w') as f:
            self.config.write(f)
    
    def get(self, section, key, fallback=None):
        """Get configuration value."""
        return self.config.get(section, key, fallback=fallback)

# Usage
config = ConfigManager()
server_url = config.get('SERVER', 'url')
device_id = config.get('DEVICE', 'id')
device_key = config.get('DEVICE', 'key')
```

This integration guide provides comprehensive information for successfully integrating WaterPlantOperator devices with WaterPlantApp, including communication protocols, error handling, security considerations, and best practices.
