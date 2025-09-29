# WaterPlantApp Testing Guide

## Overview
This guide provides comprehensive information on testing WaterPlantApp, including unit tests, integration tests, cross-integration tests, and testing best practices.

## Table of Contents
1. [Testing Architecture](#testing-architecture)
2. [Test Types](#test-types)
3. [Running Tests](#running-tests)
4. [Unit Testing](#unit-testing)
5. [Integration Testing](#integration-testing)
6. [Cross-Integration Testing](#cross-integration-testing)
7. [API Testing](#api-testing)
8. [Performance Testing](#performance-testing)
9. [Test Data Management](#test-data-management)
10. [Continuous Integration](#continuous-integration)
11. [Best Practices](#best-practices)

## Testing Architecture

### Test Structure
```
WaterPlantApp/
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── test_models.py
│   │   ├── test_views.py
│   │   ├── test_serializers.py
│   │   └── test_helpers.py
│   ├── integration/
│   │   ├── __init__.py
│   │   ├── test_api_workflow.py
│   │   └── test_database_operations.py
│   └── cross_integration/
│       ├── __init__.py
│       ├── conftest.py
│       ├── test_simple_macos_compatibility.py
│       ├── test_api_integration.py
│       ├── test_cross_system_integration.py
│       └── test_macos_compatibility.py
├── pytest.ini
├── requirements-test.txt
└── run_tests.py
```

### Test Dependencies
```bash
# Core testing dependencies
pytest>=7.0.0
pytest-django>=4.5.0
pytest-cov>=4.0.0
pytest-mock>=3.10.0

# API testing
requests-mock>=1.10.0
factory-boy>=3.2.0

# Cross-integration testing
gpiozero>=1.6.0
picamera>=1.13.0

# Performance testing
locust>=2.0.0
```

## Test Types

### 1. Unit Tests
- **Purpose**: Test individual components in isolation
- **Scope**: Models, views, serializers, helpers
- **Mocking**: External dependencies
- **Speed**: Fast execution

### 2. Integration Tests
- **Purpose**: Test component interactions
- **Scope**: API workflows, database operations
- **Mocking**: Minimal mocking
- **Speed**: Medium execution

### 3. Cross-Integration Tests
- **Purpose**: Test WaterPlantApp ↔ WaterPlantOperator communication
- **Scope**: End-to-end system integration
- **Mocking**: Hardware components for macOS compatibility
- **Speed**: Slower execution

### 4. API Tests
- **Purpose**: Test REST API endpoints
- **Scope**: HTTP requests/responses, authentication
- **Mocking**: Database operations
- **Speed**: Medium execution

## Running Tests

### Basic Test Execution
```bash
# Run all tests
python manage.py test

# Run with pytest
pytest

# Run specific test file
pytest tests/unit/test_models.py

# Run specific test class
pytest tests/unit/test_models.py::TestDeviceModel

# Run specific test method
pytest tests/unit/test_models.py::TestDeviceModel::test_device_creation
```

### Test Execution with Options
```bash
# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=.

# Run with coverage report
pytest --cov=. --cov-report=html

# Run tests in parallel
pytest -n auto

# Run only failed tests
pytest --lf

# Run tests matching pattern
pytest -k "test_device"

# Run tests with specific markers
pytest -m "not slow"
```

### Cross-Integration Tests
```bash
# Run cross-integration tests
cd tests/cross_integration
python run_tests.py

# Run specific cross-integration test
pytest test_simple_macos_compatibility.py -v

# Run with macOS compatibility
pytest test_simple_macos_compatibility.py test_macos_compatibility.py -v
```

## Unit Testing

### Model Testing
```python
# tests/unit/test_models.py
from django.test import TestCase
from django.contrib.auth.models import User
from gadget_communicator_pull.models import Device, BasicPlan

class TestDeviceModel(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_device_creation(self):
        """Test device creation with valid data."""
        device = Device.objects.create(
            device_id='TEST_DEVICE_001',
            label='Test Device',
            owner=self.user,
            water_level=75,
            moisture_level=45,
            water_container_capacity=2000,
            status='online'
        )
        
        self.assertEqual(device.device_id, 'TEST_DEVICE_001')
        self.assertEqual(device.label, 'Test Device')
        self.assertEqual(device.owner, self.user)
        self.assertTrue(device.is_online)
        self.assertEqual(device.water_level_ml, 1500)  # 75% of 2000ml
    
    def test_device_validation(self):
        """Test device validation rules."""
        # Test invalid water level
        with self.assertRaises(ValidationError):
            device = Device(
                device_id='TEST_DEVICE_002',
                label='Test Device',
                owner=self.user,
                water_level=150,  # Invalid: > 100%
                moisture_level=45,
                water_container_capacity=2000,
                status='online'
            )
            device.full_clean()
    
    def test_device_properties(self):
        """Test device computed properties."""
        device = Device.objects.create(
            device_id='TEST_DEVICE_003',
            label='Test Device',
            owner=self.user,
            water_level=25,  # Low water level
            moisture_level=80,  # High moisture
            water_container_capacity=2000,
            status='online'
        )
        
        self.assertTrue(device.needs_water_refill)  # < 30%
        self.assertTrue(device.needs_watering)  # moisture > 70%
```

### View Testing
```python
# tests/unit/test_views.py
from django.test import TestCase, Client
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from gadget_communicator_pull.models import Device

class TestDeviceViews(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.device = Device.objects.create(
            device_id='TEST_DEVICE_001',
            label='Test Device',
            owner=self.user,
            water_level=75,
            moisture_level=45,
            water_container_capacity=2000,
            status='online'
        )
    
    def test_list_devices(self):
        """Test device listing API."""
        url = reverse('list_devices')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['device_id'], 'TEST_DEVICE_001')
    
    def test_create_device(self):
        """Test device creation API."""
        url = reverse('create_device')
        data = {
            'device_id': 'TEST_DEVICE_002',
            'label': 'New Test Device',
            'water_level': 80,
            'moisture_level': 50,
            'water_container_capacity': 2500,
            'status': 'online'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Device.objects.count(), 2)
    
    def test_unauthenticated_access(self):
        """Test that unauthenticated users cannot access protected endpoints."""
        self.client.force_authenticate(user=None)
        
        url = reverse('list_devices')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
```

### Serializer Testing
```python
# tests/unit/test_serializers.py
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.exceptions import ValidationError
from gadget_communicator_pull.models import Device
from gadget_communicator_pull.water_serializers import DeviceSerializer

class TestDeviceSerializer(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_device_serialization(self):
        """Test device serialization."""
        device = Device.objects.create(
            device_id='TEST_DEVICE_001',
            label='Test Device',
            owner=self.user,
            water_level=75,
            moisture_level=45,
            water_container_capacity=2000,
            status='online'
        )
        
        serializer = DeviceSerializer(device)
        data = serializer.data
        
        self.assertEqual(data['device_id'], 'TEST_DEVICE_001')
        self.assertEqual(data['label'], 'Test Device')
        self.assertEqual(data['owner_username'], 'testuser')
        self.assertTrue(data['is_online'])
        self.assertEqual(data['water_level_ml'], 1500)
    
    def test_device_validation(self):
        """Test device validation."""
        # Test invalid water level
        data = {
            'device_id': 'TEST_DEVICE_001',
            'label': 'Test Device',
            'water_level': 150,  # Invalid: > 100%
            'moisture_level': 45,
            'water_container_capacity': 2000,
            'status': 'online'
        }
        
        serializer = DeviceSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('water_level', serializer.errors)
    
    def test_device_creation(self):
        """Test device creation via serializer."""
        data = {
            'device_id': 'TEST_DEVICE_002',
            'label': 'New Test Device',
            'water_level': 80,
            'moisture_level': 50,
            'water_container_capacity': 2500,
            'status': 'online'
        }
        
        serializer = DeviceSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        device = serializer.save(owner=self.user)
        self.assertEqual(device.device_id, 'TEST_DEVICE_002')
        self.assertEqual(device.owner, self.user)
```

## Integration Testing

### API Workflow Testing
```python
# tests/integration/test_api_workflow.py
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from gadget_communicator_pull.models import Device, BasicPlan, Status

class TestAPIWorkflow(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_complete_device_workflow(self):
        """Test complete device management workflow."""
        # 1. Create device
        device_data = {
            'device_id': 'TEST_DEVICE_001',
            'label': 'Test Device',
            'water_level': 75,
            'moisture_level': 45,
            'water_container_capacity': 2000,
            'status': 'online'
        }
        
        response = self.client.post('/api/v1/devices/', device_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        device_id = response.data['id']
        
        # 2. Create basic plan
        plan_data = {
            'name': 'Test Plan',
            'plan_type': 'basic',
            'water_volume': 150,
            'device': device_id
        }
        
        response = self.client.post('/api/v1/plans/', plan_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        plan_id = response.data['id']
        
        # 3. Create status
        status_data = {
            'message': 'Plan executed successfully',
            'status_type': 'success',
            'device': device_id
        }
        
        response = self.client.post('/api/v1/statuses/', status_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # 4. Verify data integrity
        self.assertEqual(Device.objects.count(), 1)
        self.assertEqual(BasicPlan.objects.count(), 1)
        self.assertEqual(Status.objects.count(), 1)
        
        # 5. Test relationships
        device = Device.objects.get(id=device_id)
        self.assertEqual(device.basic_plans.count(), 1)
        self.assertEqual(device.statuses.count(), 1)
```

### Database Operations Testing
```python
# tests/integration/test_database_operations.py
from django.test import TestCase, TransactionTestCase
from django.db import transaction
from django.contrib.auth.models import User
from gadget_communicator_pull.models import Device, BasicPlan

class TestDatabaseOperations(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_device_plan_relationship(self):
        """Test device-plan relationship integrity."""
        device = Device.objects.create(
            device_id='TEST_DEVICE_001',
            label='Test Device',
            owner=self.user,
            water_level=75,
            moisture_level=45,
            water_container_capacity=2000,
            status='online'
        )
        
        plan = BasicPlan.objects.create(
            name='Test Plan',
            plan_type='basic',
            water_volume=150,
            device=device
        )
        
        # Test forward relationship
        self.assertEqual(plan.device, device)
        
        # Test reverse relationship
        self.assertIn(plan, device.basic_plans.all())
        
        # Test cascade deletion
        device.delete()
        self.assertEqual(BasicPlan.objects.count(), 0)
    
    def test_concurrent_device_updates(self):
        """Test concurrent device updates."""
        device = Device.objects.create(
            device_id='TEST_DEVICE_001',
            label='Test Device',
            owner=self.user,
            water_level=75,
            moisture_level=45,
            water_container_capacity=2000,
            status='online'
        )
        
        # Simulate concurrent updates
        device1 = Device.objects.get(id=device.id)
        device2 = Device.objects.get(id=device.id)
        
        device1.water_level = 80
        device2.moisture_level = 50
        
        device1.save()
        device2.save()
        
        # Verify both updates were applied
        device.refresh_from_db()
        self.assertEqual(device.water_level, 80)
        self.assertEqual(device.moisture_level, 50)
```

## Cross-Integration Testing

### macOS Compatibility Testing
```python
# tests/cross_integration/test_simple_macos_compatibility.py
import pytest
from unittest.mock import Mock, patch
import sys
import os

# Add WaterPlantOperator to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..', 'WaterPlantOperator'))

class TestSimpleMacOSCompatibility:
    """Test WaterPlantOperator components on macOS."""
    
    def test_basic_imports(self):
        """Test that WaterPlantOperator modules can be imported."""
        from run.model.device import Device as OperatorDevice
        from run.model.plan import Plan
        from run.model.moisture_plan import MoisturePlan as OperatorMoisturePlan
        from run.model.time_plan import TimePlan as OperatorTimePlan
        from run.model.status import Status as OperatorStatus
        
        # All imports should succeed
        assert OperatorDevice is not None
        assert Plan is not None
        assert OperatorMoisturePlan is not None
        assert OperatorTimePlan is not None
        assert OperatorStatus is not None
    
    def test_operator_device_creation(self):
        """Test creating operator device on macOS."""
        from run.model.device import Device as OperatorDevice
        
        device = OperatorDevice(device_id='TEST_DEVICE_001')
        
        assert device is not None
        assert device.device_id == 'TEST_DEVICE_001'
    
    def test_gpio_mocking(self):
        """Test GPIO component mocking on macOS."""
        with patch('run.sensor.relay.Relay') as mock_relay:
            mock_relay_instance = Mock()
            mock_relay_instance.on.return_value = None
            mock_relay_instance.off.return_value = None
            mock_relay.return_value = mock_relay_instance
            
            # Test relay operations
            mock_relay_instance.on()
            mock_relay_instance.off()
            
            mock_relay_instance.on.assert_called_once()
            mock_relay_instance.off.assert_called_once()
    
    def test_camera_mocking(self):
        """Test camera component mocking on macOS."""
        with patch('run.sensor.camera_sensor.Camera') as mock_camera:
            mock_camera_instance = Mock()
            mock_camera_instance.take_photo.return_value = None
            mock_camera.return_value = mock_camera_instance
            
            # Test camera operations
            mock_camera_instance.take_photo("test_photo")
            
            mock_camera_instance.take_photo.assert_called_once_with("test_photo")
```

### API Integration Testing
```python
# tests/cross_integration/test_api_integration.py
import pytest
import requests_mock
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from gadget_communicator_pull.models import Device

class TestAPIIntegration(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_device_api_endpoints(self):
        """Test all device API endpoints."""
        # Create device
        device_data = {
            'device_id': 'TEST_DEVICE_001',
            'label': 'Test Device',
            'water_level': 75,
            'moisture_level': 45,
            'water_container_capacity': 2000,
            'status': 'online'
        }
        
        # POST /api/v1/devices/
        response = self.client.post('/api/v1/devices/', device_data, format='json')
        self.assertEqual(response.status_code, 201)
        device_id = response.data['id']
        
        # GET /api/v1/devices/
        response = self.client.get('/api/v1/devices/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)
        
        # GET /api/v1/devices/{id}/
        response = self.client.get(f'/api/v1/devices/{device_id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['device_id'], 'TEST_DEVICE_001')
        
        # PUT /api/v1/devices/{id}/
        update_data = {'label': 'Updated Test Device'}
        response = self.client.put(f'/api/v1/devices/{device_id}/', update_data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['label'], 'Updated Test Device')
        
        # DELETE /api/v1/devices/{id}/
        response = self.client.delete(f'/api/v1/devices/{device_id}/')
        self.assertEqual(response.status_code, 204)
        
        # Verify deletion
        response = self.client.get(f'/api/v1/devices/{device_id}/')
        self.assertEqual(response.status_code, 404)
    
    def test_expected_json_structures(self):
        """Test that API responses match expected JSON structures."""
        device = Device.objects.create(
            device_id='TEST_DEVICE_001',
            label='Test Device',
            owner=self.user,
            water_level=75,
            moisture_level=45,
            water_container_capacity=2000,
            status='online'
        )
        
        response = self.client.get(f'/api/v1/devices/{device.id}/')
        
        # Verify expected fields
        expected_fields = [
            'id', 'device_id', 'label', 'owner_username',
            'water_level', 'moisture_level', 'water_container_capacity',
            'status', 'is_online', 'water_level_ml',
            'needs_water_refill', 'needs_watering',
            'created_at', 'updated_at'
        ]
        
        for field in expected_fields:
            self.assertIn(field, response.data)
        
        # Verify data types
        self.assertIsInstance(response.data['id'], int)
        self.assertIsInstance(response.data['device_id'], str)
        self.assertIsInstance(response.data['water_level'], int)
        self.assertIsInstance(response.data['is_online'], bool)
```

## API Testing

### REST API Testing
```python
# tests/api/test_rest_api.py
import pytest
import json
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status

class TestRESTAPI(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_authentication_required(self):
        """Test that authentication is required for protected endpoints."""
        endpoints = [
            '/api/v1/devices/',
            '/api/v1/plans/',
            '/api/v1/statuses/'
        ]
        
        for endpoint in endpoints:
            response = self.client.get(endpoint)
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_token_authentication(self):
        """Test token-based authentication."""
        # Get authentication token
        response = self.client.post('/api/auth/token/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        token = response.data['access']
        
        # Use token for authenticated request
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
        response = self.client.get('/api/v1/devices/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_pagination(self):
        """Test API pagination."""
        self.client.force_authenticate(user=self.user)
        
        # Create multiple devices
        for i in range(25):
            Device.objects.create(
                device_id=f'TEST_DEVICE_{i:03d}',
                label=f'Test Device {i}',
                owner=self.user,
                water_level=75,
                moisture_level=45,
                water_container_capacity=2000,
                status='online'
            )
        
        # Test pagination
        response = self.client.get('/api/v1/devices/?page=1&page_size=10')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 10)
        self.assertEqual(response.data['count'], 25)
        self.assertIsNotNone(response.data['next'])
        self.assertIsNone(response.data['previous'])
    
    def test_filtering_and_search(self):
        """Test API filtering and search functionality."""
        self.client.force_authenticate(user=self.user)
        
        # Create test devices
        Device.objects.create(
            device_id='DEVICE_001',
            label='Living Room Plant',
            owner=self.user,
            water_level=75,
            moisture_level=45,
            water_container_capacity=2000,
            status='online'
        )
        
        Device.objects.create(
            device_id='DEVICE_002',
            label='Kitchen Plant',
            owner=self.user,
            water_level=25,
            moisture_level=80,
            water_container_capacity=2000,
            status='offline'
        )
        
        # Test status filtering
        response = self.client.get('/api/v1/devices/?status=online')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['status'], 'online')
        
        # Test search
        response = self.client.get('/api/v1/devices/?search=living')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertIn('Living', response.data['results'][0]['label'])
```

## Performance Testing

### Load Testing with Locust
```python
# tests/performance/locustfile.py
from locust import HttpUser, task, between
import random
import json

class WaterPlantAppUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        """Login and get authentication token."""
        response = self.client.post("/api/auth/token/", {
            "username": "testuser",
            "password": "testpass123"
        })
        
        if response.status_code == 200:
            self.token = response.json()["access"]
            self.client.headers.update({
                "Authorization": f"Token {self.token}"
            })
    
    @task(3)
    def list_devices(self):
        """Test device listing endpoint."""
        self.client.get("/api/v1/devices/")
    
    @task(2)
    def get_device_details(self):
        """Test device details endpoint."""
        device_id = f"TEST_DEVICE_{random.randint(1, 100):03d}"
        self.client.get(f"/api/v1/devices/{device_id}/")
    
    @task(1)
    def create_device(self):
        """Test device creation endpoint."""
        device_data = {
            "device_id": f"PERF_DEVICE_{random.randint(1000, 9999)}",
            "label": f"Performance Test Device {random.randint(1, 100)}",
            "water_level": random.randint(0, 100),
            "moisture_level": random.randint(0, 100),
            "water_container_capacity": random.randint(1000, 5000),
            "status": random.choice(["online", "offline"])
        }
        
        response = self.client.post("/api/v1/devices/", json=device_data)
        
        if response.status_code == 201:
            self.device_id = response.json()["id"]
    
    @task(1)
    def create_plan(self):
        """Test plan creation endpoint."""
        if hasattr(self, 'device_id'):
            plan_data = {
                "name": f"Performance Test Plan {random.randint(1, 100)}",
                "plan_type": random.choice(["basic", "moisture", "time_based"]),
                "water_volume": random.randint(100, 500),
                "device": self.device_id
            }
            
            self.client.post("/api/v1/plans/", json=plan_data)
    
    @task(2)
    def list_plans(self):
        """Test plan listing endpoint."""
        self.client.get("/api/v1/plans/")
    
    @task(1)
    def create_status(self):
        """Test status creation endpoint."""
        if hasattr(self, 'device_id'):
            status_data = {
                "message": f"Performance test status {random.randint(1, 100)}",
                "status_type": random.choice(["success", "error", "warning"]),
                "device": self.device_id
            }
            
            self.client.post("/api/v1/statuses/", json=status_data)
```

### Performance Test Execution
```bash
# Run performance tests
locust -f tests/performance/locustfile.py --host=http://localhost:8000

# Run with specific user count and spawn rate
locust -f tests/performance/locustfile.py --host=http://localhost:8000 --users 100 --spawn-rate 10

# Run headless mode
locust -f tests/performance/locustfile.py --host=http://localhost:8000 --users 100 --spawn-rate 10 --run-time 5m --headless
```

## Test Data Management

### Factory Boy for Test Data
```python
# tests/factories.py
import factory
from django.contrib.auth.models import User
from gadget_communicator_pull.models import Device, BasicPlan, MoisturePlan, TimePlan, Status

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
    
    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    password = factory.PostGenerationMethodCall('set_password', 'testpass123')

class DeviceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Device
    
    device_id = factory.Sequence(lambda n: f"DEVICE_{n:03d}")
    label = factory.Faker('word')
    owner = factory.SubFactory(UserFactory)
    water_level = factory.Faker('random_int', min=0, max=100)
    moisture_level = factory.Faker('random_int', min=0, max=100)
    water_container_capacity = factory.Faker('random_int', min=1000, max=5000)
    status = factory.Faker('random_element', elements=['online', 'offline'])

class BasicPlanFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = BasicPlan
    
    name = factory.Faker('word')
    plan_type = 'basic'
    water_volume = factory.Faker('random_int', min=100, max=500)
    device = factory.SubFactory(DeviceFactory)

class MoisturePlanFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MoisturePlan
    
    name = factory.Faker('word')
    plan_type = 'moisture'
    water_volume = factory.Faker('random_int', min=100, max=500)
    moisture_threshold = factory.Faker('pydecimal', left_digits=1, right_digits=2, positive=True, max_value=1.0)
    check_interval = factory.Faker('random_int', min=10, max=120)
    device = factory.SubFactory(DeviceFactory)

class StatusFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Status
    
    message = factory.Faker('sentence')
    status_type = factory.Faker('random_element', elements=['success', 'error', 'warning'])
    device = factory.SubFactory(DeviceFactory)
```

### Using Factories in Tests
```python
# tests/unit/test_with_factories.py
from django.test import TestCase
from tests.factories import UserFactory, DeviceFactory, BasicPlanFactory

class TestWithFactories(TestCase):
    def test_device_with_factory(self):
        """Test using factories for test data."""
        user = UserFactory()
        device = DeviceFactory(owner=user, water_level=75)
        plan = BasicPlanFactory(device=device, water_volume=150)
        
        self.assertEqual(device.owner, user)
        self.assertEqual(device.water_level, 75)
        self.assertEqual(plan.device, device)
        self.assertEqual(plan.water_volume, 150)
    
    def test_multiple_devices(self):
        """Test creating multiple devices with factories."""
        user = UserFactory()
        devices = DeviceFactory.create_batch(5, owner=user)
        
        self.assertEqual(len(devices), 5)
        for device in devices:
            self.assertEqual(device.owner, user)
```

## Continuous Integration

### GitHub Actions Configuration
```yaml
# .github/workflows/test.yml
name: Test Suite

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    strategy:
      matrix:
        python-version: [3.8, 3.9, "3.10"]
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-test.txt
    
    - name: Run unit tests
      run: |
        python manage.py test tests.unit
    
    - name: Run integration tests
      run: |
        python manage.py test tests.integration
    
    - name: Run cross-integration tests
      run: |
        cd tests/cross_integration
        python run_tests.py
    
    - name: Generate coverage report
      run: |
        coverage run --source='.' manage.py test
        coverage report
        coverage xml
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        flags: unittests
        name: codecov-umbrella
```

### Pre-commit Hooks
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 22.3.0
    hooks:
      - id: black
        language_version: python3
  
  - repo: https://github.com/pycqa/isort
    rev: 5.10.1
    hooks:
      - id: isort
  
  - repo: https://github.com/pycqa/flake8
    rev: 4.0.1
    hooks:
      - id: flake8
  
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v0.950
    hooks:
      - id: mypy
        additional_dependencies: [types-requests]
```

## Best Practices

### 1. Test Organization
- Group related tests in classes
- Use descriptive test names
- Follow AAA pattern (Arrange, Act, Assert)
- Keep tests independent and isolated

### 2. Test Data
- Use factories for test data creation
- Clean up test data after each test
- Use realistic test data
- Avoid hardcoded values

### 3. Mocking
- Mock external dependencies
- Use appropriate mock levels
- Verify mock interactions
- Keep mocks simple and focused

### 4. Performance
- Run tests in parallel when possible
- Use database transactions for speed
- Avoid unnecessary database operations
- Profile slow tests

### 5. Coverage
- Aim for high test coverage (>90%)
- Focus on critical business logic
- Test edge cases and error conditions
- Don't test implementation details

### 6. Documentation
- Document test purpose and scope
- Use docstrings for test methods
- Include examples in test documentation
- Keep test documentation up to date

### 7. Maintenance
- Review and update tests regularly
- Remove obsolete tests
- Refactor tests when code changes
- Monitor test execution time

This testing guide provides comprehensive information for testing WaterPlantApp at all levels, from unit tests to cross-integration tests, ensuring robust and reliable software quality.
