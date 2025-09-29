"""
Pytest configuration and fixtures for cross-integration tests.

This module provides common fixtures and configuration for testing
the integration between WaterPlantApp and WaterPlantOperator.
"""
import pytest
import json
import os
import sys
import django
from typing import Dict, Any, List, Optional
from unittest.mock import Mock, patch, MagicMock

# Configure Django settings first
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../pycharmtut'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pycharmtut.test_settings')
django.setup()

# Now import Django components
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

# Add both project paths to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..', 'WaterPlantOperator'))

# Import Django models
from gadget_communicator_pull.models import (
    Device, BasicPlan, MoisturePlan, TimePlan, WaterTime, Status, WaterChart
)

# Import WaterPlantOperator components
from run.model.device import Device as OperatorDevice
from run.model.plan import Plan
from run.model.moisture_plan import MoisturePlan as OperatorMoisturePlan
from run.model.time_plan import TimePlan as OperatorTimePlan
from run.model.status import Status as OperatorStatus
from run.operation.pump import Pump
from run.operation.server_checker import ServerChecker
from run.http_communicator.server_communicator import ServerCommunicator


@pytest.fixture
def django_user():
    """Create a Django test user."""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )


@pytest.fixture
def django_device(django_user):
    """Create a Django device."""
    return Device.objects.create(
        device_id='TEST_DEVICE_001',
        label='Test Plant Device',
        owner=django_user,
        water_level=75,
        moisture_level=45,
        water_container_capacity=2000,
        is_connected=True,
        status='online'
    )


@pytest.fixture
def django_basic_plan():
    """Create a Django basic plan."""
    return BasicPlan.objects.create(
        name='Test Basic Plan',
        plan_type='basic',
        water_volume=150
    )


@pytest.fixture
def django_moisture_plan():
    """Create a Django moisture plan."""
    return MoisturePlan.objects.create(
        name='Test Moisture Plan',
        plan_type='moisture',
        water_volume=200,
        moisture_threshold=0.4,
        check_interval=30
    )


@pytest.fixture
def django_time_plan():
    """Create a Django time plan."""
    return TimePlan.objects.create(
        name='Test Time Plan',
        plan_type='time_based',
        water_volume=180,
        execute_only_once=False
    )


@pytest.fixture
def operator_device():
    """Create a WaterPlantOperator device."""
    return OperatorDevice(
        device_id='TEST_DEVICE_001',
        water_level=75,
        moisture_level=45,
        water_container_capacity=2000
    )


@pytest.fixture
def operator_basic_plan():
    """Create a WaterPlantOperator basic plan."""
    return Plan(
        name='Test Basic Plan',
        plan_type='basic',
        water_volume=150
    )


@pytest.fixture
def operator_moisture_plan():
    """Create a WaterPlantOperator moisture plan."""
    return OperatorMoisturePlan(
        name='Test Moisture Plan',
        plan_type='moisture',
        water_volume=200,
        moisture_threshold=0.4,
        check_interval=30
    )


@pytest.fixture
def operator_time_plan():
    """Create a WaterPlantOperator time plan."""
    return OperatorTimePlan(
        name='Test Time Plan',
        plan_type='time_based',
        water_volume=180,
        execute_only_once=False
    )


@pytest.fixture
def operator_status():
    """Create a WaterPlantOperator status."""
    return OperatorStatus(
        execution_status=True,
        message='Test watering completed successfully'
    )


@pytest.fixture
def mock_pump():
    """Create a mocked pump for testing."""
    with patch('run.operation.pump.Pump') as mock_pump_class:
        mock_pump = Mock()
        mock_pump.water_plant.return_value = True
        mock_pump.water_plant_by_moisture.return_value = True
        mock_pump.water_plant_by_timer.return_value = True
        mock_pump.get_water_level_in_percent.return_value = 75
        mock_pump.get_moisture_level_in_percent.return_value = 45
        mock_pump.is_water_level_sufficient.return_value = True
        mock_pump_class.return_value = mock_pump
        yield mock_pump


@pytest.fixture
def mock_server_communicator():
    """Create a mocked server communicator for testing."""
    with patch('run.http_communicator.server_communicator.ServerCommunicator') as mock_comm_class:
        mock_comm = Mock()
        mock_comm.send_health_check.return_value = True
        mock_comm.send_result.return_value = True
        mock_comm.send_photo.return_value = True
        mock_comm.get_water_plan.return_value = {
            'name': 'Test Plan',
            'plan_type': 'basic',
            'water_volume': 150
        }
        mock_comm_class.return_value = mock_comm
        yield mock_comm


@pytest.fixture
def mock_server_checker():
    """Create a mocked server checker for testing."""
    with patch('run.operation.server_checker.ServerChecker') as mock_checker_class:
        mock_checker = Mock()
        mock_checker.plan_executor.return_value = None
        mock_checker_class.return_value = mock_checker
        yield mock_checker


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


@pytest.fixture
def mock_camera():
    """Mock camera component for macOS compatibility."""
    with patch('picamera.PiCamera') as mock_camera_class:
        mock_camera_instance = Mock()
        mock_camera_instance.capture.return_value = None
        mock_camera_class.return_value = mock_camera_instance
        yield mock_camera_instance


@pytest.fixture
def api_client():
    """Create a Django test client."""
    return Client()


@pytest.fixture
def authenticated_api_client(django_user, api_client):
    """Create an authenticated Django test client."""
    api_client.force_login(django_user)
    return api_client


@pytest.fixture
def expected_device_json():
    """Expected JSON structure for device API responses."""
    return {
        'id': 1,
        'device_id': 'TEST_DEVICE_001',
        'label': 'Test Plant Device',
        'owner_username': 'testuser',
        'water_level': 75,
        'water_level_ml': 1500,
        'moisture_level': 45,
        'water_container_capacity': 2000,
        'water_reset': False,
        'send_email': True,
        'is_connected': True,
        'is_online': True,
        'status': 'online',
        'last_seen': None,
        'location': '',
        'notes': '',
        'needs_water_refill': False,
        'needs_watering': False,
        'basic_plans': [],
        'time_plans': [],
        'moisture_plans': [],
        'recent_statuses': [],
        'water_charts': [],
        'created_at': '2023-01-01T00:00:00Z',
        'updated_at': '2023-01-01T00:00:00Z'
    }


@pytest.fixture
def expected_plan_json():
    """Expected JSON structure for plan API responses."""
    return {
        'id': 1,
        'name': 'Test Basic Plan',
        'plan_type': 'basic',
        'water_volume': 150,
        'has_been_executed': False,
        'devices': [],
        'is_executable': True,
        'created_at': '2023-01-01T00:00:00Z',
        'updated_at': '2023-01-01T00:00:00Z'
    }


@pytest.fixture
def expected_status_json():
    """Expected JSON structure for status API responses."""
    return {
        'id': 1,
        'execution_status': True,
        'message': 'Test status message',
        'status_id': 'uuid-string',
        'status_time': '2023-01-01T00:00:00Z',
        'status_type': 'success',
        'device_id': 'TEST_DEVICE_001',
        'created_at': '2023-01-01T00:00:00Z',
        'updated_at': '2023-01-01T00:00:00Z'
    }


@pytest.fixture
def mock_requests():
    """Mock requests library for API testing."""
    with patch('requests.get') as mock_get, \
         patch('requests.post') as mock_post, \
         patch('requests.put') as mock_put, \
         patch('requests.delete') as mock_delete:
        
        # Mock successful responses
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'success': True}
        mock_response.text = '{"success": true}'
        
        mock_get.return_value = mock_response
        mock_post.return_value = mock_response
        mock_put.return_value = mock_response
        mock_delete.return_value = mock_response
        
        yield {
            'get': mock_get,
            'post': mock_post,
            'put': mock_put,
            'delete': mock_delete,
            'response': mock_response
        }


class CrossIntegrationTestCase(TestCase):
    """Base test case for cross-integration tests."""
    
    def setUp(self):
        """Set up common test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.device = Device.objects.create(
            device_id='TEST_DEVICE_001',
            label='Test Plant Device',
            owner=self.user,
            water_level=75,
            moisture_level=45,
            water_container_capacity=2000,
            is_connected=True,
            status='online'
        )
        
        self.client = Client()
        self.client.force_login(self.user)
    
    def create_operator_device(self, **kwargs):
        """Create a WaterPlantOperator device."""
        defaults = {
            'device_id': 'TEST_DEVICE_001',
            'water_level': 75,
            'moisture_level': 45,
            'water_container_capacity': 2000
        }
        defaults.update(kwargs)
        return OperatorDevice(**defaults)
    
    def create_operator_plan(self, plan_type='basic', **kwargs):
        """Create a WaterPlantOperator plan."""
        if plan_type == 'basic':
            defaults = {
                'name': 'Test Basic Plan',
                'plan_type': 'basic',
                'water_volume': 150
            }
            defaults.update(kwargs)
            return Plan(**defaults)
        elif plan_type == 'moisture':
            defaults = {
                'name': 'Test Moisture Plan',
                'plan_type': 'moisture',
                'water_volume': 200,
                'moisture_threshold': 0.4,
                'check_interval': 30
            }
            defaults.update(kwargs)
            return OperatorMoisturePlan(**defaults)
        elif plan_type == 'time_based':
            defaults = {
                'name': 'Test Time Plan',
                'plan_type': 'time_based',
                'water_volume': 180,
                'execute_only_once': False
            }
            defaults.update(kwargs)
            return OperatorTimePlan(**defaults)
    
    def create_operator_status(self, **kwargs):
        """Create a WaterPlantOperator status."""
        defaults = {
            'execution_status': True,
            'message': 'Test status message'
        }
        defaults.update(kwargs)
        return OperatorStatus(**defaults)
    
    def assert_json_response(self, response, expected_status=200, expected_keys=None):
        """Assert JSON response structure."""
        self.assertEqual(response.status_code, expected_status)
        self.assertEqual(response['Content-Type'], 'application/json')
        
        if expected_keys:
            data = response.json()
            for key in expected_keys:
                self.assertIn(key, data)
    
    def assert_device_json_structure(self, data):
        """Assert device JSON structure."""
        required_keys = [
            'id', 'device_id', 'label', 'water_level', 'moisture_level',
            'water_container_capacity', 'is_connected', 'status'
        ]
        for key in required_keys:
            self.assertIn(key, data)
    
    def assert_plan_json_structure(self, data):
        """Assert plan JSON structure."""
        required_keys = [
            'id', 'name', 'plan_type', 'water_volume', 'has_been_executed'
        ]
        for key in required_keys:
            self.assertIn(key, data)
    
    def assert_status_json_structure(self, data):
        """Assert status JSON structure."""
        required_keys = [
            'id', 'execution_status', 'message', 'status_id', 'status_time'
        ]
        for key in required_keys:
            self.assertIn(key, data)
