"""
Pytest configuration and fixtures for WaterPlantApp tests.

This module provides common fixtures and configuration for all tests
in the WaterPlantApp test suite.
"""
import pytest
from django.contrib.auth.models import User
from django.test import TestCase
from gadget_communicator_pull.models import (
    Device, BasicPlan, MoisturePlan, TimePlan, WaterTime, Status, WaterChart
)


@pytest.fixture
def user():
    """Create a test user."""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )


@pytest.fixture
def device(user):
    """Create a test device."""
    return Device.objects.create(
        device_id='TEST_DEVICE_001',
        label='Test Plant Device',
        owner=user,
        water_level=75,
        moisture_level=45,
        water_container_capacity=2000,
        is_connected=True,
        status='online'
    )


@pytest.fixture
def basic_plan():
    """Create a test basic plan."""
    return BasicPlan.objects.create(
        name='Test Basic Plan',
        plan_type='basic',
        water_volume=150
    )


@pytest.fixture
def moisture_plan():
    """Create a test moisture plan."""
    return MoisturePlan.objects.create(
        name='Test Moisture Plan',
        plan_type='moisture',
        water_volume=200,
        moisture_threshold=0.4,
        check_interval=30
    )


@pytest.fixture
def time_plan():
    """Create a test time plan."""
    return TimePlan.objects.create(
        name='Test Time Plan',
        plan_type='time_based',
        water_volume=180,
        execute_only_once=False
    )


@pytest.fixture
def water_time(time_plan):
    """Create a test water time."""
    return WaterTime.objects.create(
        weekday=1,  # Tuesday
        time_water='09:00',
        time_plan=time_plan
    )


@pytest.fixture
def status(device):
    """Create a test status."""
    return Status.objects.create(
        execution_status=True,
        message='Test watering completed successfully',
        status_type='success',
        device_id=device.device_id
    )


@pytest.fixture
def water_chart(device):
    """Create a test water chart entry."""
    return WaterChart.objects.create(
        water_level=80,
        device=device
    )


@pytest.fixture
def multiple_devices(user):
    """Create multiple test devices."""
    devices = []
    for i in range(3):
        device = Device.objects.create(
            device_id=f'TEST_DEVICE_{i+1:03d}',
            label=f'Test Plant Device {i+1}',
            owner=user,
            water_level=50 + (i * 10),
            moisture_level=30 + (i * 5),
            water_container_capacity=2000,
            is_connected=i % 2 == 0,  # Alternate connection status
            status='online' if i % 2 == 0 else 'offline'
        )
        devices.append(device)
    return devices


@pytest.fixture
def multiple_plans():
    """Create multiple test plans of different types."""
    plans = []
    
    # Basic plans
    for i in range(2):
        plan = BasicPlan.objects.create(
            name=f'Basic Plan {i+1}',
            plan_type='basic',
            water_volume=100 + (i * 50)
        )
        plans.append(plan)
    
    # Moisture plans
    for i in range(2):
        plan = MoisturePlan.objects.create(
            name=f'Moisture Plan {i+1}',
            plan_type='moisture',
            water_volume=150 + (i * 50),
            moisture_threshold=0.3 + (i * 0.1),
            check_interval=20 + (i * 10)
        )
        plans.append(plan)
    
    # Time plans
    for i in range(2):
        plan = TimePlan.objects.create(
            name=f'Time Plan {i+1}',
            plan_type='time_based',
            water_volume=200 + (i * 50),
            execute_only_once=i == 0
        )
        plans.append(plan)
    
    return plans


@pytest.fixture
def device_with_plans(device, multiple_plans):
    """Create a device with associated plans."""
    # Associate plans with device
    for plan in multiple_plans[:2]:  # Basic plans
        device.device_relation_b.add(plan)
    
    for plan in multiple_plans[2:4]:  # Moisture plans
        device.device_relation_m.add(plan)
    
    for plan in multiple_plans[4:6]:  # Time plans
        device.device_relation_t.add(plan)
    
    return device


@pytest.fixture
def time_plan_with_schedules(time_plan):
    """Create a time plan with multiple scheduled times."""
    # Add multiple watering times
    WaterTime.objects.create(
        weekday=0,  # Monday
        time_water='08:00',
        time_plan=time_plan
    )
    WaterTime.objects.create(
        weekday=0,  # Monday
        time_water='18:00',
        time_plan=time_plan
    )
    WaterTime.objects.create(
        weekday=3,  # Thursday
        time_water='09:30',
        time_plan=time_plan
    )
    WaterTime.objects.create(
        weekday=5,  # Saturday
        time_water='10:00',
        time_plan=time_plan
    )
    
    return time_plan


@pytest.fixture
def device_with_history(device):
    """Create a device with water level history."""
    # Create historical water level data
    for i in range(10):
        WaterChart.objects.create(
            water_level=100 - (i * 5),  # Decreasing water level
            device=device
        )
    
    return device


@pytest.fixture
def device_with_statuses(device):
    """Create a device with multiple status entries."""
    # Create various status entries
    Status.objects.create(
        execution_status=True,
        message='Watering completed successfully',
        status_type='success',
        device_id=device.device_id
    )
    Status.objects.create(
        execution_status=False,
        message='Moisture sensor reading failed',
        status_type='warning',
        device_id=device.device_id
    )
    Status.objects.create(
        execution_status=True,
        message='Device connected successfully',
        status_type='info',
        device_id=device.device_id
    )
    Status.objects.create(
        execution_status=False,
        message='Water level critically low',
        status_type='failure',
        device_id=device.device_id
    )
    
    return device


class BaseTestCase(TestCase):
    """Base test case with common setup and utilities."""
    
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
    
    def create_basic_plan(self, **kwargs):
        """Create a basic plan with default values."""
        defaults = {
            'name': 'Test Basic Plan',
            'plan_type': 'basic',
            'water_volume': 150
        }
        defaults.update(kwargs)
        return BasicPlan.objects.create(**defaults)
    
    def create_moisture_plan(self, **kwargs):
        """Create a moisture plan with default values."""
        defaults = {
            'name': 'Test Moisture Plan',
            'plan_type': 'moisture',
            'water_volume': 200,
            'moisture_threshold': 0.4,
            'check_interval': 30
        }
        defaults.update(kwargs)
        return MoisturePlan.objects.create(**defaults)
    
    def create_time_plan(self, **kwargs):
        """Create a time plan with default values."""
        defaults = {
            'name': 'Test Time Plan',
            'plan_type': 'time_based',
            'water_volume': 180,
            'execute_only_once': False
        }
        defaults.update(kwargs)
        return TimePlan.objects.create(**defaults)
    
    def create_water_time(self, time_plan, **kwargs):
        """Create a water time with default values."""
        defaults = {
            'weekday': 1,  # Tuesday
            'time_water': '09:00',
            'time_plan': time_plan
        }
        defaults.update(kwargs)
        return WaterTime.objects.create(**defaults)
    
    def create_status(self, **kwargs):
        """Create a status with default values."""
        defaults = {
            'execution_status': True,
            'message': 'Test status message',
            'status_type': 'success',
            'device_id': self.device.device_id
        }
        defaults.update(kwargs)
        return Status.objects.create(**defaults)
    
    def create_water_chart(self, **kwargs):
        """Create a water chart entry with default values."""
        defaults = {
            'water_level': 80,
            'device': self.device
        }
        defaults.update(kwargs)
        return WaterChart.objects.create(**defaults)
