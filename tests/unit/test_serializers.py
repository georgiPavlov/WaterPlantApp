"""
Simple unit tests for WaterPlantApp serializers that match the actual serializer structure.
"""
import pytest
from django.test import TestCase
from django.contrib.auth.models import User

from gadget_communicator_pull.models import (
    Device, BasicPlan, MoisturePlan, TimePlan, WaterTime, Status, WaterChart
)
from gadget_communicator_pull.water_serializers import (
    BasePlanSerializer, DeviceSerializer, WaterChartSerializer
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
        self.assertFalse(data['has_been_executed'])

    def test_valid_moisture_plan_serialization(self):
        """Test moisture plan serialization."""
        plan = MoisturePlan.objects.create(
            name='Test Moisture Plan',
            plan_type='moisture',
            water_volume=200,
            moisture_threshold=0.3
        )
        
        serializer = BasePlanSerializer(plan)
        data = serializer.data
        
        self.assertEqual(data['name'], 'Test Moisture Plan')
        self.assertEqual(data['plan_type'], 'moisture')
        self.assertEqual(data['water_volume'], 200)
        self.assertFalse(data['has_been_executed'])

    def test_valid_time_plan_serialization(self):
        """Test time plan serialization."""
        plan = TimePlan.objects.create(
            name='Test Time Plan',
            plan_type='time_based',
            water_volume=180
        )
        
        serializer = BasePlanSerializer(plan)
        data = serializer.data
        
        self.assertEqual(data['name'], 'Test Time Plan')
        self.assertEqual(data['plan_type'], 'time_based')
        self.assertEqual(data['water_volume'], 180)
        self.assertFalse(data['has_been_executed'])

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
            name='Original Plan',
            plan_type='basic',
            water_volume=100
        )
        
        data = {
            'name': 'Updated Plan',
            'plan_type': 'basic',
            'water_volume': 150
        }
        
        serializer = BasePlanSerializer(plan, data=data)
        self.assertTrue(serializer.is_valid())
        
        updated_plan = serializer.save()
        self.assertEqual(updated_plan.name, 'Updated Plan')
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
        self.assertFalse(data['water_reset'])
        self.assertFalse(data['send_email'])
        self.assertFalse(data['is_connected'])

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
        
        device = serializer.save()
        self.assertEqual(device.device_id, 'NEW_DEVICE_001')
        self.assertEqual(device.label, 'New Test Device')
        self.assertEqual(device.water_level, 80)

    def test_device_update(self):
        """Test device update via serializer."""
        device = Device.objects.create(
            device_id='TEST_DEVICE_001',
            label='Original Device',
            water_level=50
        )
        
        data = {
            'device_id': 'TEST_DEVICE_001',
            'label': 'Updated Device',
            'water_level': 90,
            'moisture_level': 60,
            'water_container_capacity': 2000
        }
        
        serializer = DeviceSerializer(device, data=data)
        self.assertTrue(serializer.is_valid())
        
        updated_device = serializer.save()
        self.assertEqual(updated_device.label, 'Updated Device')
        self.assertEqual(updated_device.water_level, 90)

    def test_device_validation(self):
        """Test device validation."""
        # Test with missing required fields
        data = {
            'device_id': 'TEST_DEVICE_001'
            # Missing label, water_level, etc.
        }
        
        serializer = DeviceSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('label', serializer.errors)

    def test_device_related_data(self):
        """Test device with related data."""
        device = Device.objects.create(
            device_id='TEST_DEVICE_001',
            label='Test Device',
            water_level=75
        )
        
        # Create a basic plan and associate it with the device
        plan = BasicPlan.objects.create(
            name='Test Plan',
            plan_type='basic',
            water_volume=100
        )
        device.device_relation_b.add(plan)
        
        serializer = DeviceSerializer(device)
        data = serializer.data
        
        # The serializer should still work even with related data
        self.assertEqual(data['device_id'], 'TEST_DEVICE_001')
        self.assertEqual(data['label'], 'Test Device')


class TestWaterChartSerializer(TestCase):
    """Test cases for WaterChartSerializer."""

    def test_water_chart_serialization(self):
        """Test water chart serialization."""
        device = Device.objects.create(
            device_id='TEST_DEVICE_001',
            label='Test Device'
        )
        
        water_chart = WaterChart.objects.create(
            water_chart=85,
            device_relation=device
        )
        
        serializer = WaterChartSerializer(water_chart)
        data = serializer.data
        
        self.assertEqual(data['water_chart'], 85)

    def test_water_chart_creation(self):
        """Test water chart creation via serializer."""
        device = Device.objects.create(
            device_id='TEST_DEVICE_001',
            label='Test Device'
        )
        
        data = {
            'water_chart': 90
        }
        
        serializer = WaterChartSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        water_chart = serializer.save(device_relation=device)
        self.assertEqual(water_chart.water_chart, 90)
        self.assertEqual(water_chart.device_relation, device)


class TestSerializerIntegration(TestCase):
    """Test serializer integration."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_serializer_computed_fields(self):
        """Test serializer computed fields."""
        device = Device.objects.create(
            device_id='TEST_DEVICE_001',
            label='Test Device',
            water_level=50,
            water_container_capacity=2000
        )
        
        serializer = DeviceSerializer(device)
        data = serializer.data
        
        # Test that basic fields are serialized correctly
        self.assertEqual(data['water_level'], 50)
        self.assertEqual(data['water_container_capacity'], 2000)

    def test_serializer_nested_relationships(self):
        """Test serializer nested relationships."""
        device = Device.objects.create(
            device_id='TEST_DEVICE_001',
            label='Test Device'
        )
        
        plan = BasicPlan.objects.create(
            name='Test Plan',
            plan_type='basic',
            water_volume=100
        )
        
        # Test that we can serialize both objects independently
        device_serializer = DeviceSerializer(device)
        plan_serializer = BasePlanSerializer(plan)
        
        device_data = device_serializer.data
        plan_data = plan_serializer.data
        
        self.assertEqual(device_data['device_id'], 'TEST_DEVICE_001')
        self.assertEqual(plan_data['name'], 'Test Plan')

    def test_serializer_with_missing_optional_fields(self):
        """Test serializer with missing optional fields."""
        # Test device with minimal data
        data = {
            'device_id': 'MINIMAL_DEVICE',
            'label': 'Minimal Device'
        }
        
        serializer = DeviceSerializer(data=data)
        # Should be valid even with missing optional fields
        self.assertTrue(serializer.is_valid())
        
        device = serializer.save()
        self.assertEqual(device.device_id, 'MINIMAL_DEVICE')
        self.assertEqual(device.label, 'Minimal Device')
        # Default values should be used
        self.assertEqual(device.water_level, 100)  # Default from model
        self.assertEqual(device.moisture_level, 0)  # Default from model
