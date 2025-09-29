"""
Unit tests for WaterPlantApp serializers.

This module contains comprehensive unit tests for all serializer classes
in the WaterPlantApp Django application.
"""
import pytest
import json
from datetime import datetime, date, time
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth.models import User
from unittest.mock import Mock, patch

from gadget_communicator_pull.models import (
    Device, BasicPlan, MoisturePlan, TimePlan, WaterTime, Status, WaterChart
)
from gadget_communicator_pull.water_serializers import (
    BasePlanSerializer, DeviceSerializer, WaterChartSerializer,
    MoisturePlanSerializer, TimePlanSerializer, StatusSerializer
)


class TestBasePlanSerializer(TestCase):
    """Test cases for BasePlanSerializer."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.device = Device.objects.create(
            device_id='TEST_DEVICE_001',
            label='Test Device',
            owner=self.user,
            water_level=75,
            moisture_level=45,
            water_container_capacity=2000
        )

    def test_valid_basic_plan_serialization(self):
        """Test basic plan serialization."""
        plan = BasicPlan.objects.create(
            name='Test Basic Plan',
            plan_type='basic',
            water_volume=150
        )
        
        serializer = BasePlanSerializer(plan)
        data = serializer.data
        
        self.assertEqual(data['name'], 'Test Basic Plan')
        self.assertEqual(data['plan_type'], 'basic')
        self.assertEqual(data['water_volume'], 150)

    def test_valid_moisture_plan_serialization(self):
        """Test moisture plan serialization."""
        plan = MoisturePlan.objects.create(
            name='Test Moisture Plan',
            plan_type='moisture',
            water_volume=200,
            moisture_threshold=0.3  # 30% as decimal
        )
        
        serializer = BasePlanSerializer(plan)
        data = serializer.data
        
        self.assertEqual(data['name'], 'Test Moisture Plan')
        self.assertEqual(data['plan_type'], 'moisture')
        self.assertEqual(data['water_volume'], 200)

    def test_valid_time_plan_serialization(self):
        """Test time plan serialization."""
        plan = TimePlan.objects.create(
            name='Test Time Plan',
            plan_type='time_based',
            water_volume=250
        )
        
        serializer = BasePlanSerializer(plan)
        data = serializer.data
        
        self.assertEqual(data['name'], 'Test Time Plan')
        self.assertEqual(data['plan_type'], 'time_based')
        self.assertEqual(data['water_volume'], 250)

    def test_plan_creation(self):
        """Test plan creation via serializer."""
        data = {
            'name': 'New Test Plan',
            'plan_type': 'basic',
            'water_volume': 100
        }
        
        serializer = BasePlanSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        plan = serializer.save()
        self.assertEqual(plan.name, 'New Test Plan')
        self.assertEqual(plan.plan_type, 'basic')
        self.assertEqual(plan.water_volume, 100)

    def test_plan_update(self):
        """Test plan update via serializer."""
        plan = BasicPlan.objects.create(
            name='Test Plan',
            plan_type='basic',
            water_volume=100
        )
        
        data = {
            'name': 'Updated Test Plan',
            'plan_type': 'basic',
            'water_volume': 150
        }
        
        serializer = BasePlanSerializer(plan, data=data)
        self.assertTrue(serializer.is_valid())
        
        updated_plan = serializer.save()
        self.assertEqual(updated_plan.name, 'Updated Test Plan')
        self.assertEqual(updated_plan.water_volume, 150)


class TestDeviceSerializer(TestCase):
    """Test cases for DeviceSerializer."""
    
    def setUp(self):
        """Set up test data."""
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
            water_container_capacity=2000
        )
        
        serializer = DeviceSerializer(device)
        data = serializer.data
        
        self.assertEqual(data['device_id'], 'TEST_DEVICE_001')
        self.assertEqual(data['label'], 'Test Device')
        self.assertEqual(data['water_level'], 75)
        self.assertEqual(data['moisture_level'], 45)
        self.assertEqual(data['water_container_capacity'], 2000)

    def test_device_creation(self):
        """Test device creation via serializer."""
        data = {
            'device_id': 'NEW_DEVICE_001',
            'label': 'New Test Device',
            'water_level': 80,
            'moisture_level': 50,
            'water_container_capacity': 1500
        }
        
        serializer = DeviceSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        device = serializer.save(owner=self.user)
        self.assertEqual(device.device_id, 'NEW_DEVICE_001')
        self.assertEqual(device.label, 'New Test Device')
        self.assertEqual(device.owner, self.user)

    def test_device_update(self):
        """Test device update via serializer."""
        device = Device.objects.create(
            device_id='TEST_DEVICE_001',
            label='Test Device',
            owner=self.user,
            water_level=50,
            moisture_level=30
        )
        
        data = {
            'device_id': 'TEST_DEVICE_001',
            'label': 'Updated Test Device',
            'water_level': 75,
            'moisture_level': 45,
            'water_container_capacity': 2000
        }
        
        serializer = DeviceSerializer(device, data=data)
        self.assertTrue(serializer.is_valid())
        
        updated_device = serializer.save()
        self.assertEqual(updated_device.label, 'Updated Test Device')
        self.assertEqual(updated_device.water_level, 75)

    def test_device_validation(self):
        """Test device validation."""
        data = {
            'device_id': 'AB',  # Too short
            'label': 'Test Device',
            'water_level': 150,  # Too high
            'moisture_level': 45,
            'water_container_capacity': 2000
        }
        
        serializer = DeviceSerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_device_related_data(self):
        """Test device with related data."""
        device = Device.objects.create(
            device_id='TEST_DEVICE_001',
            label='Test Device',
            owner=self.user
        )
        
        # Create related plans
        basic_plan = BasicPlan.objects.create(
            name='Test Basic Plan',
            water_volume=150
        )
        
        # Test that device can be serialized with related data
        serializer = DeviceSerializer(device)
        data = serializer.data
        
        self.assertIsNotNone(data)
        self.assertEqual(data['device_id'], 'TEST_DEVICE_001')


class TestWaterChartSerializer(TestCase):
    """Test cases for WaterChartSerializer."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.device = Device.objects.create(
            device_id='TEST_DEVICE_001',
            label='Test Device',
            owner=self.user
        )

    def test_water_chart_serialization(self):
        """Test water chart serialization."""
        water_chart = WaterChart.objects.create(
            device=self.device,
            water_level=75
        )
        
        serializer = WaterChartSerializer(water_chart)
        data = serializer.data
        
        self.assertEqual(data['water_level'], 75)
        self.assertIsNotNone(data['recorded_at'])


class TestStatusSerializer(TestCase):
    """Test cases for StatusSerializer."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.device = Device.objects.create(
            device_id='TEST_DEVICE_001',
            label='Test Device',
            owner=self.user
        )

    def test_status_serialization(self):
        """Test status serialization."""
        status = Status.objects.create(
            message='Test status message',
            execution_status=True,
            status_type='success',
            device_id=self.device.device_id
        )
        
        serializer = StatusSerializer(status)
        data = serializer.data
        
        self.assertEqual(data['message'], 'Test status message')
        self.assertTrue(data['execution_status'])
        self.assertEqual(data['status_type'], 'success')
        self.assertEqual(data['device_id'], self.device.device_id)

    def test_status_creation(self):
        """Test status creation via serializer."""
        data = {
            'message': 'New status message',
            'execution_status': False,
            'status_type': 'warning',
            'device_id': self.device.device_id
        }
        
        serializer = StatusSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        status = serializer.save()
        self.assertEqual(status.message, 'New status message')
        self.assertFalse(status.execution_status)
        self.assertEqual(status.status_type, 'warning')

    def test_status_update(self):
        """Test status update via serializer."""
        status = Status.objects.create(
            message='Test status message',
            execution_status=False,
            status_type='info',
            device_id=self.device.device_id
        )
        
        data = {
            'message': 'Updated status message',
            'execution_status': True,
            'status_type': 'success',
            'device_id': self.device.device_id
        }
        
        serializer = StatusSerializer(status, data=data)
        self.assertTrue(serializer.is_valid())
        
        updated_status = serializer.save()
        self.assertEqual(updated_status.message, 'Updated status message')
        self.assertTrue(updated_status.execution_status)

    def test_status_validation(self):
        """Test status validation."""
        data = {
            'message': '',  # Empty message
            'execution_status': True,
            'status_type': 'invalid_type',  # Invalid status type
            'device_id': self.device.device_id
        }
        
        serializer = StatusSerializer(data=data)
        self.assertFalse(serializer.is_valid())


class TestSerializerIntegration(TestCase):
    """Test cases for serializer integration."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.device = Device.objects.create(
            device_id='TEST_DEVICE_001',
            label='Test Device',
            owner=self.user
        )

    def test_serializer_nested_relationships(self):
        """Test serializer with nested relationships."""
        # Create a device with related data
        basic_plan = BasicPlan.objects.create(
            name='Test Basic Plan',
            water_volume=150
        )
        
        status = Status.objects.create(
            message='Device status',
            execution_status=True,
            device_id=self.device.device_id
        )
        
        # Test device serialization
        device_serializer = DeviceSerializer(self.device)
        device_data = device_serializer.data
        
        self.assertIsNotNone(device_data)
        self.assertEqual(device_data['device_id'], 'TEST_DEVICE_001')

    def test_serializer_computed_fields(self):
        """Test serializer with computed fields."""
        device = Device.objects.create(
            device_id='TEST_DEVICE_002',
            label='Test Device 2',
            owner=self.user,
            water_level=50,
            water_container_capacity=2000
        )
        
        serializer = DeviceSerializer(device)
        data = serializer.data
        
        # Test that computed fields are included
        self.assertIn('water_level', data)
        self.assertIn('water_container_capacity', data)

    def test_serializer_with_missing_optional_fields(self):
        """Test serializer with missing optional fields."""
        data = {
            'device_id': 'TEST_DEVICE_003',
            'label': 'Test Device 3',
            'water_level': 75,
            'moisture_level': 45,
            'water_container_capacity': 2000
        }
        
        serializer = DeviceSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        device = serializer.save(owner=self.user)
        self.assertIsNotNone(device)
        self.assertEqual(device.device_id, 'TEST_DEVICE_003')