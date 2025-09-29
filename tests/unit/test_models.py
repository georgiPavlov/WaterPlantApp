"""
Unit tests for WaterPlantApp models.

This module contains comprehensive unit tests for all model classes
in the WaterPlantApp Django application.
"""
import pytest
import uuid
from datetime import datetime, date, time
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from unittest.mock import Mock, patch

from gadget_communicator_pull.models import (
    Device, BasicPlan, MoisturePlan, TimePlan, WaterTime, Status, WaterChart
)


class TestDeviceModel(TestCase):
    """Test cases for Device model."""

    def setUp(self):
        """Set up test data."""
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
            water_container_capacity=2000
        )
        
        self.assertEqual(device.device_id, 'TEST_DEVICE_001')
        self.assertEqual(device.label, 'Test Device')
        self.assertEqual(device.owner, self.user)
        self.assertEqual(device.water_level, 75)
        self.assertEqual(device.moisture_level, 45)
        self.assertEqual(device.water_container_capacity, 2000)

    def test_device_str_representation(self):
        """Test device string representation."""
        device = Device.objects.create(
            device_id='TEST_DEVICE_001',
            label='Test Device',
            owner=self.user
        )
        
        expected = "Test Device (TEST_DEVICE_001)"
        self.assertEqual(str(device), expected)

    def test_device_is_online_property(self):
        """Test device is_online property."""
        device = Device.objects.create(
            device_id='TEST_DEVICE_001',
            label='Test Device',
            owner=self.user,
            is_connected=True,
            status='online'
        )
        
        self.assertTrue(device.is_online)
        
        device.is_connected = False
        self.assertFalse(device.is_online)

    def test_device_water_level_ml_property(self):
        """Test device water_level_ml property."""
        device = Device.objects.create(
            device_id='TEST_DEVICE_001',
            label='Test Device',
            owner=self.user,
            water_level=50,
            water_container_capacity=2000
        )
        
        expected_ml = int((50 / 100) * 2000)  # 1000ml
        self.assertEqual(device.water_level_ml, expected_ml)

    def test_device_needs_water_refill_property(self):
        """Test device needs_water_refill property."""
        device = Device.objects.create(
            device_id='TEST_DEVICE_001',
            label='Test Device',
            owner=self.user,
            water_level=15  # Below 20%
        )
        
        self.assertTrue(device.needs_water_refill)
        
        device.water_level = 25
        self.assertFalse(device.needs_water_refill)

    def test_device_needs_watering_property(self):
        """Test device needs_watering property."""
        device = Device.objects.create(
            device_id='TEST_DEVICE_001',
            label='Test Device',
            owner=self.user,
            moisture_level=25  # Below 30%
        )
        
        self.assertTrue(device.needs_watering)
        
        device.moisture_level = 35
        self.assertFalse(device.needs_watering)

    def test_device_connect_disconnect(self):
        """Test device connect and disconnect methods."""
        device = Device.objects.create(
            device_id='TEST_DEVICE_001',
            label='Test Device',
            owner=self.user
        )
        
        # Test connect
        device.connect()
        self.assertTrue(device.is_connected)
        self.assertEqual(device.status, 'online')
        
        # Test disconnect
        device.disconnect()
        self.assertFalse(device.is_connected)
        self.assertEqual(device.status, 'offline')

    def test_device_update_water_level(self):
        """Test device water level update."""
        device = Device.objects.create(
            device_id='TEST_DEVICE_001',
            label='Test Device',
            owner=self.user,
            water_level=50
        )
        
        device.update_water_level(75)
        self.assertEqual(device.water_level, 75)

    def test_device_update_moisture_level(self):
        """Test device moisture level update."""
        device = Device.objects.create(
            device_id='TEST_DEVICE_001',
            label='Test Device',
            owner=self.user,
            moisture_level=30
        )
        
        device.update_moisture_level(60)
        self.assertEqual(device.moisture_level, 60)

    def test_device_reset_water_level(self):
        """Test device water level reset."""
        device = Device.objects.create(
            device_id='TEST_DEVICE_001',
            label='Test Device',
            owner=self.user,
            water_level=25,
            water_reset=True
        )
        
        device.reset_water_level()
        self.assertEqual(device.water_level, 100)
        self.assertFalse(device.water_reset)

    def test_device_validation_water_level_too_high(self):
        """Test device validation for water level too high."""
        device = Device(
            device_id='TEST_DEVICE_001',
            label='Test Device',
            owner=self.user,
            water_level=150,  # Above 100%
            water_container_capacity=2000
        )
        
        with self.assertRaises(ValidationError):
            device.full_clean()

    def test_device_validation_moisture_level_too_high(self):
        """Test device validation for moisture level too high."""
        device = Device(
            device_id='TEST_DEVICE_001',
            label='Test Device',
            owner=self.user,
            moisture_level=150,  # Above 100%
            water_container_capacity=2000
        )
        
        with self.assertRaises(ValidationError):
            device.full_clean()

    def test_device_validation_water_container_capacity_too_low(self):
        """Test device validation for water container capacity too low."""
        device = Device(
            device_id='TEST_DEVICE_001',
            label='Test Device',
            owner=self.user,
            water_container_capacity=50  # Below 100ml
        )
        
        with self.assertRaises(ValidationError):
            device.full_clean()

    def test_device_validation_water_container_capacity_too_high(self):
        """Test device validation for water container capacity too high."""
        device = Device(
            device_id='TEST_DEVICE_001',
            label='Test Device',
            owner=self.user,
            water_container_capacity=15000  # Above 10000ml
        )
        
        with self.assertRaises(ValidationError):
            device.full_clean()

    def test_device_validation_device_id_too_short(self):
        """Test device validation for device ID too short."""
        device = Device(
            device_id='AB',  # Too short
            label='Test Device',
            owner=self.user,
            water_container_capacity=2000
        )
        
        with self.assertRaises(ValidationError):
            device.full_clean()


class TestBasicPlanModel(TestCase):
    """Test cases for BasicPlan model."""

    def test_basic_plan_creation(self):
        """Test basic plan creation with valid data."""
        plan = BasicPlan.objects.create(
            name='Test Basic Plan',
            plan_type='basic',
            water_volume=150
        )
        
        self.assertEqual(plan.name, 'Test Basic Plan')
        self.assertEqual(plan.plan_type, 'basic')
        self.assertEqual(plan.water_volume, 150)

    def test_basic_plan_str_representation(self):
        """Test basic plan string representation."""
        plan = BasicPlan.objects.create(
            name='Test Basic Plan',
            water_volume=150
        )
        
        expected = "BasicPlan: Test Basic Plan (150ml)"
        self.assertEqual(str(plan), expected)

    def test_basic_plan_is_executable_property(self):
        """Test basic plan is_executable property."""
        plan = BasicPlan.objects.create(
            name='Test Basic Plan',
            water_volume=150,
            has_been_executed=False
        )
        
        self.assertTrue(plan.is_executable)
        
        plan.has_been_executed = True
        self.assertFalse(plan.is_executable)


class TestTimePlanModel(TestCase):
    """Test cases for TimePlan model."""

    def test_time_plan_creation(self):
        """Test time plan creation with valid data."""
        plan = TimePlan.objects.create(
            name='Test Time Plan',
            plan_type='time_based',
            water_volume=200
        )
        
        self.assertEqual(plan.name, 'Test Time Plan')
        self.assertEqual(plan.plan_type, 'time_based')
        self.assertEqual(plan.water_volume, 200)

    def test_time_plan_add_remove_weekday_time(self):
        """Test time plan weekday time management."""
        plan = TimePlan.objects.create(
            name='Test Time Plan',
            water_volume=200
        )
        
        # Test adding weekday time
        water_time = WaterTime.objects.create(
            time_water='09:00',
            weekday=0  # Monday
        )
        plan.weekday_times.add(water_time)
        
        self.assertIn(water_time, plan.weekday_times.all())
        
        # Test removing weekday time
        plan.weekday_times.remove(water_time)
        self.assertNotIn(water_time, plan.weekday_times.all())


class TestStatusModel(TestCase):
    """Test cases for Status model."""

    def test_status_creation(self):
        """Test status creation with valid data."""
        status = Status.objects.create(
            message='Test status message',
            execution_status=True,
            status_type='success',
            device_id='TEST_DEVICE_001'
        )
        
        self.assertEqual(status.message, 'Test status message')
        self.assertTrue(status.execution_status)
        self.assertEqual(status.status_type, 'success')
        self.assertEqual(status.device_id, 'TEST_DEVICE_001')

    def test_status_str_representation(self):
        """Test status string representation."""
        status = Status.objects.create(
            message='Test status message',
            execution_status=True
        )
        
        expected = "✓ Test status message..."
        self.assertEqual(str(status), expected)


class TestWaterTimeModel(TestCase):
    """Test cases for WaterTime model."""

    def test_water_time_creation(self):
        """Test water time creation with valid data."""
        water_time = WaterTime.objects.create(
            time_water='09:00',
            weekday=0  # Monday
        )
        
        self.assertEqual(water_time.time_water, '09:00')
        self.assertEqual(water_time.weekday, 0)

    def test_water_time_str_representation(self):
        """Test water time string representation."""
        water_time = WaterTime.objects.create(
            time_water='09:00',
            weekday=0  # Monday
        )
        
        expected = "Monday at 09:00"
        self.assertEqual(str(water_time), expected)


class TestModelIntegration(TestCase):
    """Test cases for model integration."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_device_plan_relationships(self):
        """Test device and plan relationships."""
        device = Device.objects.create(
            device_id='TEST_DEVICE_001',
            label='Test Device',
            owner=self.user
        )
        
        basic_plan = BasicPlan.objects.create(
            name='Test Basic Plan',
            water_volume=150
        )
        
        # Test that plans can be created independently
        self.assertIsNotNone(basic_plan)
        self.assertIsNotNone(device)

    def test_status_device_relationship(self):
        """Test status and device relationship."""
        device = Device.objects.create(
            device_id='TEST_DEVICE_001',
            label='Test Device',
            owner=self.user
        )
        
        status = Status.objects.create(
            message='Device status update',
            execution_status=True,
            device_id=device.device_id
        )
        
        self.assertEqual(status.device_id, device.device_id)

    def test_model_validation_integration(self):
        """Test model validation integration."""
        # Test valid device creation
        device = Device.objects.create(
            device_id='TEST_DEVICE_001',
            label='Test Device',
            owner=self.user,
            water_level=50,
            moisture_level=30,
            water_container_capacity=2000
        )
        
        self.assertIsNotNone(device)
        
        # Test valid plan creation
        plan = BasicPlan.objects.create(
            name='Test Plan',
            water_volume=150
        )
        
        self.assertIsNotNone(plan)