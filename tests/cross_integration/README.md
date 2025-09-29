# Cross-Integration Tests

Comprehensive integration tests for WaterPlantApp (Django) and WaterPlantOperator (Raspberry Pi) systems with full macOS compatibility.

## 🌟 Overview

This test suite verifies the complete integration between:
- **WaterPlantApp**: Django web application for device management and monitoring
- **WaterPlantOperator**: Raspberry Pi automation system for plant watering

## 🧪 Test Categories

### 1. API Integration Tests (`test_api_integration.py`)
Tests the Django REST API endpoints with expected JSON outcomes:

- **Device API**: CRUD operations, filtering, searching, ordering
- **Plan API**: Basic, moisture, and time-based plan management
- **Status API**: Status reporting and retrieval
- **JSON Structure Validation**: Ensures consistent API responses

### 2. Cross-System Integration Tests (`test_cross_system_integration.py`)
Tests data flow and communication between systems:

- **Data Model Compatibility**: Ensures models work together seamlessly
- **API to Operator Communication**: Tests plan execution and status updates
- **Operator to API Communication**: Tests health checks and status reporting
- **Data Synchronization**: Verifies data consistency between systems
- **Error Handling**: Tests failure scenarios and recovery

### 3. macOS Compatibility Tests (`test_macos_compatibility.py`)
Tests WaterPlantOperator components on macOS with mocked hardware:

- **GPIO Components**: Relay and moisture sensor mocking
- **Camera Component**: PiCamera mocking
- **Pump Operations**: All watering methods with mocked hardware
- **Server Communication**: HTTP communication testing
- **Model Compatibility**: All data models work without hardware

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Both WaterPlantApp and WaterPlantOperator projects
- macOS, Linux, or Windows (tests are cross-platform)

### Installation

1. **Clone both projects:**
   ```bash
   git clone https://github.com/georgiPavlov/WaterPlantApp.git
   git clone https://github.com/georgiPavlov/WaterPlantOperator.git
   ```

2. **Set up cross-integration tests:**
   ```bash
   cd cross_integration_tests
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   python run_tests.py --install-deps --setup-env
   ```

### Running Tests

#### Run All Tests
```bash
python run_tests.py --test-type all
```

#### Run Specific Test Categories
```bash
# Unit tests (macOS compatibility)
python run_tests.py --test-type unit

# API integration tests
python run_tests.py --test-type api

# Cross-system integration tests
python run_tests.py --test-type cross-system
```

#### Run with Coverage
```bash
python run_tests.py --test-type coverage
```

#### Manual pytest Commands
```bash
# Run all tests
pytest -v --tb=short --color=yes

# Run specific test file
pytest test_api_integration.py -v

# Run with coverage
pytest --cov=. --cov-report=html --cov-report=term-missing

# Run specific test class
pytest test_macos_compatibility.py::TestMacOSPumpCompatibility -v
```

## 📊 Expected JSON Outcomes

### Device API Response
```json
{
  "success": true,
  "count": 1,
  "data": [
    {
      "id": 1,
      "device_id": "TEST_DEVICE_001",
      "label": "Test Plant Device",
      "owner_username": "testuser",
      "water_level": 75,
      "water_level_ml": 1500,
      "moisture_level": 45,
      "water_container_capacity": 2000,
      "water_reset": false,
      "send_email": true,
      "is_connected": true,
      "is_online": true,
      "status": "online",
      "last_seen": null,
      "location": "",
      "notes": "",
      "needs_water_refill": false,
      "needs_watering": false,
      "basic_plans": [],
      "time_plans": [],
      "moisture_plans": [],
      "recent_statuses": [],
      "water_charts": [],
      "created_at": "2023-01-01T00:00:00Z",
      "updated_at": "2023-01-01T00:00:00Z"
    }
  ]
}
```

### Plan API Response
```json
{
  "success": true,
  "count": 1,
  "data": [
    {
      "id": 1,
      "name": "Test Basic Plan",
      "plan_type": "basic",
      "water_volume": 150,
      "has_been_executed": false,
      "devices": [],
      "is_executable": true,
      "created_at": "2023-01-01T00:00:00Z",
      "updated_at": "2023-01-01T00:00:00Z"
    }
  ]
}
```

### Status API Response
```json
{
  "success": true,
  "count": 1,
  "data": [
    {
      "id": 1,
      "execution_status": true,
      "message": "Test status message",
      "status_id": "uuid-string",
      "status_time": "2023-01-01T00:00:00Z",
      "status_type": "success",
      "device_id": "TEST_DEVICE_001",
      "created_at": "2023-01-01T00:00:00Z",
      "updated_at": "2023-01-01T00:00:00Z"
    }
  ]
}
```

## 🔧 macOS Compatibility

### Hardware Mocking

The tests automatically mock all Raspberry Pi hardware components:

- **GPIO Pins**: `gpiozero.Relay`, `gpiozero.Moisture`
- **Camera**: `picamera.PiCamera`
- **Network**: HTTP requests via `requests` library

### Mock Configuration

```python
@pytest.fixture
def mock_gpio_components():
    """Mock GPIO components for macOS compatibility."""
    with patch('gpiozero.Relay') as mock_relay, \
         patch('gpiozero.Moisture') as mock_moisture, \
         patch('gpiozero.Device.pin_factory', Mock()):
        
        # Mock relay
        mock_relay_instance = Mock()
        mock_relay_instance.on.return_value = None
        mock_relay_instance.off.return_value = None
        mock_relay.return_value = mock_relay_instance
        
        # Mock moisture sensor
        mock_moisture_instance = Mock()
        mock_moisture_instance.value = 0.5
        mock_moisture.return_value = mock_moisture_instance
        
        yield {
            'relay': mock_relay_instance,
            'moisture': mock_moisture_instance
        }
```

## 🧪 Test Structure

### Fixtures (`conftest.py`)

- **Django Fixtures**: User, device, plan, status objects
- **Operator Fixtures**: WaterPlantOperator model instances
- **Mock Fixtures**: Hardware and network mocking
- **API Fixtures**: Expected JSON structures

### Test Classes

1. **TestDeviceAPI**: Device CRUD operations and JSON validation
2. **TestPlanAPI**: Plan management and validation
3. **TestStatusAPI**: Status reporting and retrieval
4. **TestAPIFilteringAndSearch**: Advanced filtering and search
5. **TestDataModelCompatibility**: Model compatibility between systems
6. **TestAPIToOperatorCommunication**: API to operator data flow
7. **TestOperatorToAPICommunication**: Operator to API data flow
8. **TestDataSynchronization**: Data consistency verification
9. **TestErrorHandlingAndRecovery**: Error scenarios and recovery
10. **TestMacOSGPIOCompatibility**: GPIO component mocking
11. **TestMacOSPumpCompatibility**: Pump operations on macOS
12. **TestMacOSServerCheckerCompatibility**: Server checker on macOS
13. **TestMacOSServerCommunicatorCompatibility**: HTTP communication
14. **TestMacOSTimeKeeperCompatibility**: Time operations
15. **TestMacOSModelCompatibility**: Model operations on macOS

## 📈 Coverage Reports

The test suite provides comprehensive coverage reporting:

```bash
# Generate HTML coverage report
pytest --cov=. --cov-report=html

# View coverage in terminal
pytest --cov=. --cov-report=term-missing
```

Coverage reports are generated in `htmlcov/index.html`.

## 🔍 Debugging

### Verbose Output
```bash
pytest -v --tb=long --color=yes
```

### Specific Test Debugging
```bash
# Run single test with maximum verbosity
pytest test_api_integration.py::TestDeviceAPI::test_list_devices_api_json_structure -vvv

# Run with pdb debugger
pytest --pdb test_cross_system_integration.py
```

### Logging
```bash
# Enable logging output
pytest --log-cli-level=INFO
```

## 🚨 Common Issues

### Import Errors
- Ensure both projects are in the Python path
- Run `python run_tests.py --setup-env` to configure paths

### Django Settings
- Set `DJANGO_SETTINGS_MODULE` environment variable
- Ensure Django is properly configured for testing

### Hardware Dependencies
- All hardware components are automatically mocked
- No physical hardware required for testing

### Network Issues
- HTTP requests are mocked for testing
- No external network calls required

## 📝 Adding New Tests

### API Tests
```python
def test_new_api_endpoint(self):
    """Test new API endpoint with expected JSON structure."""
    url = reverse('api:new-endpoint')
    response = self.api_client.get(url)
    
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    data = response.json()
    
    # Assert expected JSON structure
    expected_keys = ['success', 'data']
    for key in expected_keys:
        self.assertIn(key, data)
```

### Cross-System Tests
```python
def test_new_cross_system_feature(self):
    """Test new cross-system feature."""
    # Test Django side
    django_object = self.create_django_object()
    
    # Test operator side
    operator_object = self.create_operator_object()
    
    # Assert compatibility
    self.assertEqual(django_object.field, operator_object.field)
```

### macOS Compatibility Tests
```python
@patch('hardware.component.HardwareComponent')
def test_new_hardware_component(self, mock_component):
    """Test new hardware component on macOS."""
    mock_instance = Mock()
    mock_component.return_value = mock_instance
    
    # Test component operations
    component = HardwareComponent()
    result = component.operation()
    
    # Assert mocked behavior
    mock_instance.operation.assert_called_once()
```

## 🤝 Contributing

1. **Add Tests**: Create comprehensive tests for new features
2. **Update Fixtures**: Add new fixtures for test data
3. **Document JSON**: Update expected JSON structures
4. **Mock Hardware**: Ensure all hardware is properly mocked
5. **Run Coverage**: Maintain high test coverage

## 📄 License

This test suite is part of the WaterPlantApp and WaterPlantOperator projects and follows the same license terms.

---

**Cross-Integration Tests** - Ensuring seamless integration between web and hardware systems! 🌱💧🔧
