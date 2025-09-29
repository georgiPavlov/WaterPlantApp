"""
Unit tests for WaterPlantApp serializers.

This module contains comprehensive unit tests for all serializers
in the WaterPlantApp Django application.
"""
import pytest
import json
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.exceptions import ValidationError

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
            water_container_capacity=2000,
            status='online'
        )
    
    def test_valid_basic_plan_serialization(self):
        """Test serialization of valid basic plan."""
        plan = BasicPlan.objects.create(
            name='Test Plan',
            plan_type='basic',
            water_volume=150,
            device=self.device
        )
        
        serializer = BasePlanSerializer(plan)
        data = serializer.data
        
        self.assertEqual(data['name'], 'Test Plan')
        self.assertEqual(data['plan_type'], 'basic')
        self.assertEqual(data['water_volume'], 150)
        self.assertEqual(data['device'], self.device.id)
        self.assertTrue(data['is_executable'])
    
    def test_valid_moisture_plan_serialization(self):
        """Test serialization of valid moisture plan."""
        plan = MoisturePlan.objects.create(
            name='Test Moisture Plan',
            plan_type='moisture',
            water_volume=200,
            moisture_threshold=0.4,
            check_interval=30,
            device=self.device
        )
        
        serializer = MoisturePlanSerializer(plan)
        data = serializer.data
        
        self.assertEqual(data['name'], 'Test Moisture Plan')
        self.assertEqual(data['plan_type'], 'moisture')
        self.assertEqual(data['water_volume'], 200)
        self.assertEqual(data['moisture_threshold'], Decimal('0.4'))
        self.assertEqual(data['check_interval'], 30)
        self.assertEqual(data['moisture_threshold_percentage'], 40.0)
    
    def test_valid_time_plan_serialization(self):
        """Test serialization of valid time plan."""
        plan = TimePlan.objects.create(
            name='Test Time Plan',
            plan_type='time_based',
            water_volume=180,
            execute_only_once=False,
            device=self.device
        )
        
        # Add water times
        WaterTime.objects.create(
            time_plan=plan,
            weekday='monday',
            time='09:00:00',
            is_active=True
        )
        WaterTime.objects.create(
            time_plan=plan,
            weekday='wednesday',
            time='14:00:00',
            is_active=True
        )
        
        serializer = TimePlanSerializer(plan)
        data = serializer.data
        
        self.assertEqual(data['name'], 'Test Time Plan')
        self.assertEqual(data['plan_type'], 'time_based')
        self.assertEqual(data['water_volume'], 180)
        self.assertEqual(data['execute_only_once'], False)
        self.assertEqual(len(data['water_times']), 2)
    
    def test_plan_validation(self):
        """Test plan validation."""
        # Test invalid plan type
        data = {
            'name': 'Test Plan',
            'plan_type': 'invalid_type',
            'water_volume': 150,
            'device': self.device.id
        }
        
        serializer = BasePlanSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('plan_type', serializer.errors)
        
        # Test negative water volume
        data = {
            'name': 'Test Plan',
            'plan_type': 'basic',
            'water_volume': -50,
            'device': self.device.id
        }
        
        serializer = BasePlanSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('water_volume', serializer.errors)
        
        # Test empty name
        data = {
            'name': '',
            'plan_type': 'basic',
            'water_volume': 150,
            'device': self.device.id
        }
        
        serializer = BasePlanSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('name', serializer.errors)
    
    def test_plan_creation(self):
        """Test plan creation via serializer."""
        data = {
            'name': 'New Test Plan',
            'plan_type': 'basic',
            'water_volume': 150,
            'device': self.device.id
        }
        
        serializer = BasePlanSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        plan = serializer.save()
        self.assertEqual(plan.name, 'New Test Plan')
        self.assertEqual(plan.plan_type, 'basic')
        self.assertEqual(plan.water_volume, 150)
        self.assertEqual(plan.device, self.device)
    
    def test_plan_update(self):
        """Test plan update via serializer."""
        plan = BasicPlan.objects.create(
            name='Test Plan',
            plan_type='basic',
            water_volume=150,
            device=self.device
        )
        
        data = {
            'name': 'Updated Test Plan',
            'plan_type': 'basic',
            'water_volume': 200,
            'device': self.device.id
        }
        
        serializer = BasePlanSerializer(plan, data=data)
        self.assertTrue(serializer.is_valid())
        
        updated_plan = serializer.save()
        self.assertEqual(updated_plan.name, 'Updated Test Plan')
        self.assertEqual(updated_plan.water_volume, 200)


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
            water_container_capacity=2000,
            status='online'
        )
        
        serializer = DeviceSerializer(device)
        data = serializer.data
        
        self.assertEqual(data['device_id'], 'TEST_DEVICE_001')
        self.assertEqual(data['label'], 'Test Device')
        self.assertEqual(data['owner_username'], 'testuser')
        self.assertEqual(data['water_level'], 75)
        self.assertEqual(data['moisture_level'], 45)
        self.assertEqual(data['water_container_capacity'], 2000)
        self.assertEqual(data['status'], 'online')
        self.assertTrue(data['is_online'])
        self.assertEqual(data['water_level_ml'], 1500)  # 75% of 2000ml
        self.assertFalse(data['needs_water_refill'])
        self.assertFalse(data['needs_watering'])
    
    def test_device_validation(self):
        """Test device validation."""
        # Test invalid device ID format
        data = {
            'device_id': 'invalid-id-format',
            'label': 'Test Device',
            'water_level': 75,
            'moisture_level': 45,
            'water_container_capacity': 2000,
            'status': 'online'
        }
        
        serializer = DeviceSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('device_id', serializer.errors)
        
        # Test negative water level
        data = {
            'device_id': 'TEST_DEVICE_001',
            'label': 'Test Device',
            'water_level': -10,
            'moisture_level': 45,
            'water_container_capacity': 2000,
            'status': 'online'
        }
        
        serializer = DeviceSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('water_level', serializer.errors)
        
        # Test water level over 100%
        data = {
            'device_id': 'TEST_DEVICE_001',
            'label': 'Test Device',
            'water_level': 150,
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
        self.assertEqual(device.label, 'New Test Device')
        self.assertEqual(device.owner, self.user)
        self.assertEqual(device.water_level, 80)
    
    def test_device_update(self):
        """Test device update via serializer."""
        device = Device.objects.create(
            device_id='TEST_DEVICE_001',
            label='Test Device',
            owner=self.user,
            water_level=75,
            moisture_level=45,
            water_container_capacity=2000,
            status='online'
        )
        
        data = {
            'device_id': 'TEST_DEVICE_001',
            'label': 'Updated Test Device',
            'water_level': 90,
            'moisture_level': 60,
            'water_container_capacity': 2000,
            'status': 'online'
        }
        
        serializer = DeviceSerializer(device, data=data)
        self.assertTrue(serializer.is_valid())
        
        updated_device = serializer.save()
        self.assertEqual(updated_device.label, 'Updated Test Device')
        self.assertEqual(updated_device.water_level, 90)
        self.assertEqual(updated_device.moisture_level, 60)
    
    def test_device_related_data(self):
        """Test device serializer includes related data."""
        device = Device.objects.create(
            device_id='TEST_DEVICE_001',
            label='Test Device',
            owner=self.user,
            water_level=75,
            moisture_level=45,
            water_container_capacity=2000,
            status='online'
        )
        
        # Create related plans
        BasicPlan.objects.create(
            name='Basic Plan',
            plan_type='basic',
            water_volume=150,
            device=device
        )
        MoisturePlan.objects.create(
            name='Moisture Plan',
            plan_type='moisture',
            water_volume=200,
            moisture_threshold=0.4,
            check_interval=30,
            device=device
        )
        
        # Create status
        Status.objects.create(
            message='Test status',
            status_type='success',
            device=device
        )
        
        serializer = DeviceSerializer(device)
        data = serializer.data
        
        self.assertEqual(len(data['basic_plans']), 1)
        self.assertEqual(len(data['moisture_plans']), 1)
        self.assertEqual(len(data['time_plans']), 0)
        self.assertEqual(len(data['recent_statuses']), 1)


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
            owner=self.user,
            water_level=75,
            moisture_level=45,
            water_container_capacity=2000,
            status='online'
        )
    
    def test_water_chart_serialization(self):
        """Test water chart serialization."""
        chart = WaterChart.objects.create(
            device=self.device,
            water_level=80,
            timestamp='2023-01-01T10:00:00Z'
        )
        
        serializer = WaterChartSerializer(chart)
        data = serializer.data
        
        self.assertEqual(data['water_level'], 80)
        self.assertEqual(data['timestamp'], '2023-01-01T10:00:00Z')
        self.assertEqual(data['water_level_ml'], 1600)  # 80% of 2000ml
    
    def test_water_chart_validation(self):
        """Test water chart validation."""
        # Test negative water level
        data = {
            'water_level': -10,
            'timestamp': '2023-01-01T10:00:00Z'
        }
        
        serializer = WaterChartSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('water_level', serializer.errors)
        
        # Test water level over 100%
        data = {
            'water_level': 150,
            'timestamp': '2023-01-01T10:00:00Z'
        }
        
        serializer = WaterChartSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('water_level', serializer.errors)
    
    def test_water_chart_creation(self):
        """Test water chart creation via serializer."""
        data = {
            'water_level': 85,
            'timestamp': '2023-01-01T11:00:00Z'
        }
        
        serializer = WaterChartSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        chart = serializer.save(device=self.device)
        self.assertEqual(chart.water_level, 85)
        self.assertEqual(chart.device, self.device)


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
            owner=self.user,
            water_level=75,
            moisture_level=45,
            water_container_capacity=2000,
            status='online'
        )
    
    def test_status_serialization(self):
        """Test status serialization."""
        status = Status.objects.create(
            message='Test status message',
            status_type='success',
            device=self.device
        )
        
        serializer = StatusSerializer(status)
        data = serializer.data
        
        self.assertEqual(data['message'], 'Test status message')
        self.assertEqual(data['status_type'], 'success')
        self.assertEqual(data['device'], self.device.id)
        self.assertTrue(data['is_success'])
        self.assertFalse(data['is_failure'])
        self.assertEqual(data['status_icon'], '✅')
    
    def test_status_validation(self):
        """Test status validation."""
        # Test empty message
        data = {
            'message': '',
            'status_type': 'success',
            'device': self.device.id
        }
        
        serializer = StatusSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('message', serializer.errors)
        
        # Test invalid status type
        data = {
            'message': 'Test message',
            'status_type': 'invalid_type',
            'device': self.device.id
        }
        
        serializer = StatusSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('status_type', serializer.errors)
    
    def test_status_creation(self):
        """Test status creation via serializer."""
        data = {
            'message': 'New test status',
            'status_type': 'error',
            'device': self.device.id
        }
        
        serializer = StatusSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        status = serializer.save()
        self.assertEqual(status.message, 'New test status')
        self.assertEqual(status.status_type, 'error')
        self.assertEqual(status.device, self.device)
    
    def test_status_update(self):
        """Test status update via serializer."""
        status = Status.objects.create(
            message='Test status',
            status_type='success',
            device=self.device
        )
        
        data = {
            'message': 'Updated test status',
            'status_type': 'warning',
            'device': self.device.id
        }
        
        serializer = StatusSerializer(status, data=data)
        self.assertTrue(serializer.is_valid())
        
        updated_status = serializer.save()
        self.assertEqual(updated_status.message, 'Updated test status')
        self.assertEqual(updated_status.status_type, 'warning')


class TestSerializerIntegration(TestCase):
    """Test cases for serializer integration and edge cases."""
    
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
            water_container_capacity=2000,
            status='online'
        )
    
    def test_serializer_with_missing_optional_fields(self):
        """Test serializers handle missing optional fields gracefully."""
        # Test device with minimal data
        data = {
            'device_id': 'TEST_DEVICE_002',
            'label': 'Minimal Device',
            'water_level': 50,
            'moisture_level': 30,
            'water_container_capacity': 1000,
            'status': 'online'
        }
        
        serializer = DeviceSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        device = serializer.save(owner=self.user)
        self.assertEqual(device.device_id, 'TEST_DEVICE_002')
    
    def test_serializer_with_extra_fields(self):
        """Test serializers ignore extra fields."""
        data = {
            'name': 'Test Plan',
            'plan_type': 'basic',
            'water_volume': 150,
            'device': self.device.id,
            'extra_field': 'should_be_ignored'
        }
        
        serializer = BasePlanSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        plan = serializer.save()
        self.assertEqual(plan.name, 'Test Plan')
        # Extra field should not be saved
        self.assertFalse(hasattr(plan, 'extra_field'))
    
    def test_serializer_nested_relationships(self):
        """Test serializers handle nested relationships correctly."""
        # Create time plan with water times
        time_plan = TimePlan.objects.create(
            name='Test Time Plan',
            plan_type='time_based',
            water_volume=180,
            execute_only_once=False,
            device=self.device
        )
        
        # Add multiple water times
        WaterTime.objects.create(
            time_plan=time_plan,
            weekday='monday',
            time='09:00:00',
            is_active=True
        )
        WaterTime.objects.create(
            time_plan=time_plan,
            weekday='wednesday',
            time='14:00:00',
            is_active=True
        )
        WaterTime.objects.create(
            time_plan=time_plan,
            weekday='friday',
            time='18:00:00',
            is_active=False
        )
        
        serializer = TimePlanSerializer(time_plan)
        data = serializer.data
        
        self.assertEqual(len(data['water_times']), 3)
        # Check that active times are included
        active_times = [wt for wt in data['water_times'] if wt['is_active']]
        self.assertEqual(len(active_times), 2)
    
    def test_serializer_computed_fields(self):
        """Test serializers compute fields correctly."""
        # Test device with specific water level
        device = Device.objects.create(
            device_id='TEST_DEVICE_003',
            label='Test Device',
            owner=self.user,
            water_level=25,  # 25%
            moisture_level=80,  # 80%
            water_container_capacity=4000,  # 4000ml
            status='online'
        )
        
        serializer = DeviceSerializer(device)
        data = serializer.data
        
        # Test computed fields
        self.assertEqual(data['water_level_ml'], 1000)  # 25% of 4000ml
        self.assertTrue(data['needs_water_refill'])  # < 30%
        self.assertTrue(data['needs_watering'])  # moisture > 70%
        
        # Test status with different types
        status = Status.objects.create(
            message='Test error',
            status_type='error',
            device=device
        )
        
        status_serializer = StatusSerializer(status)
        status_data = status_serializer.data
        
        self.assertFalse(status_data['is_success'])
        self.assertTrue(status_data['is_failure'])
        self.assertEqual(status_data['status_icon'], '❌')
