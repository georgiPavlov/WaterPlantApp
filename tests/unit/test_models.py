"""
Unit tests for Django models.

This module contains comprehensive unit tests for all models in the
water plant automation system.
"""
import pytest
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone
from gadget_communicator_pull.models import (
    Device, BasicPlan, MoisturePlan, TimePlan, WaterTime, Status, WaterChart
)


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
        self.assertFalse(plan.has_been_executed)
        self.assertIsNotNone(plan.created_at)
        self.assertIsNotNone(plan.updated_at)
    
    def test_basic_plan_str_representation(self):
        """Test string representation of basic plan."""
        plan = BasicPlan.objects.create(
            name='Test Plan',
            water_volume=200
        )
        expected = "BasicPlan: Test Plan (200ml)"
        self.assertEqual(str(plan), expected)
    
    def test_basic_plan_repr_representation(self):
        """Test developer representation of basic plan."""
        plan = BasicPlan.objects.create(
            name='Test Plan',
            water_volume=200
        )
        expected = f"BasicPlan(id={plan.id}, name='Test Plan', volume=200ml)"
        self.assertEqual(repr(plan), expected)
    
    def test_basic_plan_is_executable_property(self):
        """Test is_executable property."""
        plan = BasicPlan.objects.create(
            name='Test Plan',
            water_volume=200
        )
        
        # Should be executable initially
        self.assertTrue(plan.is_executable)
        
        # Should not be executable after marking as executed
        plan.mark_as_executed()
        self.assertFalse(plan.is_executable)
        
        # Should not be executable with zero water volume
        plan.reset_execution_status()
        plan.water_volume = 0
        plan.save()
        self.assertFalse(plan.is_executable)
    
    def test_basic_plan_validation_water_volume_too_low(self):
        """Test validation with water volume too low."""
        plan = BasicPlan(
            name='Test Plan',
            water_volume=30  # Below minimum
        )
        
        with self.assertRaises(ValidationError) as context:
            plan.full_clean()
        
        self.assertIn('water_volume', str(context.exception))
    
    def test_basic_plan_validation_water_volume_too_high(self):
        """Test validation with water volume too high."""
        plan = BasicPlan(
            name='Test Plan',
            water_volume=2500  # Above maximum
        )
        
        with self.assertRaises(ValidationError) as context:
            plan.full_clean()
        
        self.assertIn('water_volume', str(context.exception))
    
    def test_basic_plan_validation_invalid_plan_type(self):
        """Test validation with invalid plan type."""
        plan = BasicPlan(
            name='Test Plan',
            plan_type='invalid_type'
        )
        
        with self.assertRaises(ValidationError) as context:
            plan.full_clean()
        
        self.assertIn('plan_type', str(context.exception))
    
    def test_basic_plan_mark_as_executed(self):
        """Test marking plan as executed."""
        plan = BasicPlan.objects.create(
            name='Test Plan',
            water_volume=200
        )
        
        self.assertFalse(plan.has_been_executed)
        plan.mark_as_executed()
        
        plan.refresh_from_db()
        self.assertTrue(plan.has_been_executed)
    
    def test_basic_plan_reset_execution_status(self):
        """Test resetting execution status."""
        plan = BasicPlan.objects.create(
            name='Test Plan',
            water_volume=200,
            has_been_executed=True
        )
        
        self.assertTrue(plan.has_been_executed)
        plan.reset_execution_status()
        
        plan.refresh_from_db()
        self.assertFalse(plan.has_been_executed)


class TestMoisturePlanModel(TestCase):
    """Test cases for MoisturePlan model."""
    
    def test_moisture_plan_creation(self):
        """Test moisture plan creation with valid data."""
        plan = MoisturePlan.objects.create(
            name='Test Moisture Plan',
            plan_type='moisture',
            water_volume=200,
            moisture_threshold=0.4,
            check_interval=30
        )
        
        self.assertEqual(plan.name, 'Test Moisture Plan')
        self.assertEqual(plan.plan_type, 'moisture')
        self.assertEqual(plan.water_volume, 200)
        self.assertEqual(plan.moisture_threshold, 0.4)
        self.assertEqual(plan.check_interval, 30)
        self.assertFalse(plan.is_running)
        self.assertFalse(plan.has_been_executed)
    
    def test_moisture_plan_str_representation(self):
        """Test string representation of moisture plan."""
        plan = MoisturePlan.objects.create(
            name='Test Plan',
            water_volume=200,
            moisture_threshold=0.4
        )
        expected = "MoisturePlan: Test Plan (threshold: 40.0%, 200ml)"
        self.assertEqual(str(plan), expected)
    
    def test_moisture_plan_moisture_threshold_percentage_property(self):
        """Test moisture threshold percentage property."""
        plan = MoisturePlan.objects.create(
            name='Test Plan',
            moisture_threshold=0.4
        )
        
        self.assertEqual(plan.moisture_threshold_percentage, 40.0)
    
    def test_moisture_plan_should_water_method(self):
        """Test should_water method."""
        plan = MoisturePlan.objects.create(
            name='Test Plan',
            moisture_threshold=0.4
        )
        
        # Should water when moisture is below threshold
        self.assertTrue(plan.should_water(0.3))
        
        # Should not water when moisture is above threshold
        self.assertFalse(plan.should_water(0.5))
        
        # Should not water when moisture equals threshold
        self.assertFalse(plan.should_water(0.4))
    
    def test_moisture_plan_start_stop_plan(self):
        """Test starting and stopping moisture plan."""
        plan = MoisturePlan.objects.create(
            name='Test Plan',
            moisture_threshold=0.4
        )
        
        self.assertFalse(plan.is_running)
        
        plan.start_plan()
        plan.refresh_from_db()
        self.assertTrue(plan.is_running)
        
        plan.stop_plan()
        plan.refresh_from_db()
        self.assertFalse(plan.is_running)
    
    def test_moisture_plan_validation_moisture_threshold_too_low(self):
        """Test validation with moisture threshold too low."""
        plan = MoisturePlan(
            name='Test Plan',
            moisture_threshold=0.05  # Below minimum
        )
        
        with self.assertRaises(ValidationError) as context:
            plan.full_clean()
        
        self.assertIn('moisture_threshold', str(context.exception))
    
    def test_moisture_plan_validation_moisture_threshold_too_high(self):
        """Test validation with moisture threshold too high."""
        plan = MoisturePlan(
            name='Test Plan',
            moisture_threshold=1.5  # Above maximum
        )
        
        with self.assertRaises(ValidationError) as context:
            plan.full_clean()
        
        self.assertIn('moisture_threshold', str(context.exception))
    
    def test_moisture_plan_validation_check_interval_too_low(self):
        """Test validation with check interval too low."""
        plan = MoisturePlan(
            name='Test Plan',
            check_interval=3  # Below minimum
        )
        
        with self.assertRaises(ValidationError) as context:
            plan.full_clean()
        
        self.assertIn('check_interval', str(context.exception))
    
    def test_moisture_plan_validation_check_interval_too_high(self):
        """Test validation with check interval too high."""
        plan = MoisturePlan(
            name='Test Plan',
            check_interval=2000  # Above maximum
        )
        
        with self.assertRaises(ValidationError) as context:
            plan.full_clean()
        
        self.assertIn('check_interval', str(context.exception))


class TestTimePlanModel(TestCase):
    """Test cases for TimePlan model."""
    
    def test_time_plan_creation(self):
        """Test time plan creation with valid data."""
        plan = TimePlan.objects.create(
            name='Test Time Plan',
            plan_type='time_based',
            water_volume=180,
            execute_only_once=False
        )
        
        self.assertEqual(plan.name, 'Test Time Plan')
        self.assertEqual(plan.plan_type, 'time_based')
        self.assertEqual(plan.water_volume, 180)
        self.assertFalse(plan.execute_only_once)
        self.assertFalse(plan.is_running)
        self.assertFalse(plan.has_been_executed)
    
    def test_time_plan_str_representation(self):
        """Test string representation of time plan."""
        plan = TimePlan.objects.create(
            name='Test Plan',
            water_volume=180
        )
        expected = "TimePlan: Test Plan (180ml)"
        self.assertEqual(str(plan), expected)
    
    def test_time_plan_start_stop_plan(self):
        """Test starting and stopping time plan."""
        plan = TimePlan.objects.create(
            name='Test Plan',
            water_volume=180
        )
        
        self.assertFalse(plan.is_running)
        
        plan.start_plan()
        plan.refresh_from_db()
        self.assertTrue(plan.is_running)
        
        plan.stop_plan()
        plan.refresh_from_db()
        self.assertFalse(plan.is_running)
    
    def test_time_plan_add_remove_weekday_time(self):
        """Test adding and removing weekday times."""
        plan = TimePlan.objects.create(
            name='Test Plan',
            water_volume=180
        )
        
        # Add a weekday time
        plan.add_weekday_time('Monday', '09:00')
        
        # Check that the time was added
        times = plan.get_weekday_times()
        self.assertEqual(len(times), 1)
        self.assertEqual(times[0]['weekday'], 'Monday')
        self.assertEqual(times[0]['time_water'], '09:00')
        
        # Remove the weekday time
        plan.remove_weekday_time('Monday', '09:00')
        
        # Check that the time was removed
        times = plan.get_weekday_times()
        self.assertEqual(len(times), 0)


class TestWaterTimeModel(TestCase):
    """Test cases for WaterTime model."""
    
    def test_water_time_creation(self):
        """Test water time creation with valid data."""
        time_plan = TimePlan.objects.create(
            name='Test Plan',
            water_volume=180
        )
        
        water_time = WaterTime.objects.create(
            weekday=1,  # Tuesday
            time_water='09:00',
            time_plan=time_plan
        )
        
        self.assertEqual(water_time.weekday, 1)
        self.assertEqual(water_time.time_water, '09:00')
        self.assertEqual(water_time.time_plan, time_plan)
        self.assertTrue(water_time.is_in_use)
    
    def test_water_time_str_representation(self):
        """Test string representation of water time."""
        time_plan = TimePlan.objects.create(
            name='Test Plan',
            water_volume=180
        )
        
        water_time = WaterTime.objects.create(
            weekday=1,  # Tuesday
            time_water='09:00',
            time_plan=time_plan
        )
        
        expected = "Tuesday at 09:00"
        self.assertEqual(str(water_time), expected)
    
    def test_water_time_weekday_name_property(self):
        """Test weekday name property."""
        time_plan = TimePlan.objects.create(
            name='Test Plan',
            water_volume=180
        )
        
        water_time = WaterTime.objects.create(
            weekday=1,  # Tuesday
            time_water='09:00',
            time_plan=time_plan
        )
        
        self.assertEqual(water_time.weekday_name, 'Tuesday')
    
    def test_water_time_is_valid_time_property(self):
        """Test is_valid_time property."""
        time_plan = TimePlan.objects.create(
            name='Test Plan',
            water_volume=180
        )
        
        # Valid time
        water_time = WaterTime.objects.create(
            weekday=1,
            time_water='09:00',
            time_plan=time_plan
        )
        self.assertTrue(water_time.is_valid_time)
        
        # Invalid time
        water_time.time_water = '25:00'
        self.assertFalse(water_time.is_valid_time)
    
    def test_water_time_get_time_in_minutes(self):
        """Test get_time_in_minutes method."""
        time_plan = TimePlan.objects.create(
            name='Test Plan',
            water_volume=180
        )
        
        water_time = WaterTime.objects.create(
            weekday=1,
            time_water='09:30',
            time_plan=time_plan
        )
        
        # 9 hours * 60 minutes + 30 minutes = 570 minutes
        self.assertEqual(water_time.get_time_in_minutes(), 570)
    
    def test_water_time_activate_deactivate(self):
        """Test activating and deactivating water time."""
        time_plan = TimePlan.objects.create(
            name='Test Plan',
            water_volume=180
        )
        
        water_time = WaterTime.objects.create(
            weekday=1,
            time_water='09:00',
            time_plan=time_plan,
            is_in_use=False
        )
        
        self.assertFalse(water_time.is_in_use)
        
        water_time.activate()
        water_time.refresh_from_db()
        self.assertTrue(water_time.is_in_use)
        
        water_time.deactivate()
        water_time.refresh_from_db()
        self.assertFalse(water_time.is_in_use)
    
    def test_water_time_validation_invalid_time_format(self):
        """Test validation with invalid time format."""
        time_plan = TimePlan.objects.create(
            name='Test Plan',
            water_volume=180
        )
        
        water_time = WaterTime(
            weekday=1,
            time_water='25:00',  # Invalid time
            time_plan=time_plan
        )
        
        with self.assertRaises(ValidationError) as context:
            water_time.full_clean()
        
        self.assertIn('time_water', str(context.exception))
    
    def test_water_time_validation_invalid_weekday(self):
        """Test validation with invalid weekday."""
        time_plan = TimePlan.objects.create(
            name='Test Plan',
            water_volume=180
        )
        
        water_time = WaterTime(
            weekday=10,  # Invalid weekday
            time_water='09:00',
            time_plan=time_plan
        )
        
        with self.assertRaises(ValidationError) as context:
            water_time.full_clean()
        
        self.assertIn('weekday', str(context.exception))


class TestStatusModel(TestCase):
    """Test cases for Status model."""
    
    def test_status_creation(self):
        """Test status creation with valid data."""
        status = Status.objects.create(
            execution_status=True,
            message='Test status message',
            status_type='success',
            device_id='TEST_DEVICE_001'
        )
        
        self.assertTrue(status.execution_status)
        self.assertEqual(status.message, 'Test status message')
        self.assertEqual(status.status_type, 'success')
        self.assertEqual(status.device_id, 'TEST_DEVICE_001')
        self.assertIsNotNone(status.status_id)
        self.assertIsNotNone(status.status_time)
    
    def test_status_str_representation(self):
        """Test string representation of status."""
        status = Status.objects.create(
            execution_status=True,
            message='Test status message that is quite long and should be truncated'
        )
        
        expected = "✓ Test status message that is quite long and should be..."
        self.assertEqual(str(status), expected)
    
    def test_status_is_success_property(self):
        """Test is_success property."""
        success_status = Status.objects.create(
            execution_status=True,
            message='Success message'
        )
        self.assertTrue(success_status.is_success)
        
        failure_status = Status.objects.create(
            execution_status=False,
            message='Failure message'
        )
        self.assertFalse(failure_status.is_success)
    
    def test_status_is_failure_property(self):
        """Test is_failure property."""
        success_status = Status.objects.create(
            execution_status=True,
            message='Success message'
        )
        self.assertFalse(success_status.is_failure)
        
        failure_status = Status.objects.create(
            execution_status=False,
            message='Failure message'
        )
        self.assertTrue(failure_status.is_failure)
    
    def test_status_status_icon_property(self):
        """Test status_icon property."""
        # Success status
        success_status = Status.objects.create(
            execution_status=True,
            message='Success message'
        )
        self.assertEqual(success_status.status_icon, '✓')
        
        # Warning status
        warning_status = Status.objects.create(
            execution_status=False,
            message='Warning message',
            status_type='warning'
        )
        self.assertEqual(warning_status.status_icon, '⚠')
        
        # Info status
        info_status = Status.objects.create(
            execution_status=False,
            message='Info message',
            status_type='info'
        )
        self.assertEqual(info_status.status_icon, 'ℹ')
        
        # Failure status
        failure_status = Status.objects.create(
            execution_status=False,
            message='Failure message',
            status_type='failure'
        )
        self.assertEqual(failure_status.status_icon, '✗')
    
    def test_status_factory_methods(self):
        """Test status factory methods."""
        # Test create_success
        success_status = Status.create_success('Success message', 'TEST_DEVICE_001')
        self.assertTrue(success_status.execution_status)
        self.assertEqual(success_status.message, 'Success message')
        self.assertEqual(success_status.status_type, 'success')
        self.assertEqual(success_status.device_id, 'TEST_DEVICE_001')
        
        # Test create_failure
        failure_status = Status.create_failure('Failure message', 'TEST_DEVICE_001')
        self.assertFalse(failure_status.execution_status)
        self.assertEqual(failure_status.message, 'Failure message')
        self.assertEqual(failure_status.status_type, 'failure')
        self.assertEqual(failure_status.device_id, 'TEST_DEVICE_001')
        
        # Test create_warning
        warning_status = Status.create_warning('Warning message', 'TEST_DEVICE_001')
        self.assertFalse(warning_status.execution_status)
        self.assertEqual(warning_status.message, 'Warning message')
        self.assertEqual(warning_status.status_type, 'warning')
        self.assertEqual(warning_status.device_id, 'TEST_DEVICE_001')
    
    def test_status_validation_empty_message(self):
        """Test validation with empty message."""
        status = Status(
            execution_status=True,
            message=''  # Empty message
        )
        
        with self.assertRaises(ValidationError) as context:
            status.full_clean()
        
        self.assertIn('message', str(context.exception))
    
    def test_status_validation_invalid_status_type(self):
        """Test validation with invalid status type."""
        status = Status(
            execution_status=True,
            message='Test message',
            status_type='invalid_type'
        )
        
        with self.assertRaises(ValidationError) as context:
            status.full_clean()
        
        self.assertIn('status_type', str(context.exception))


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
            label='Test Plant Device',
            owner=self.user,
            water_level=75,
            moisture_level=45,
            water_container_capacity=2000,
            is_connected=True,
            status='online'
        )
        
        self.assertEqual(device.device_id, 'TEST_DEVICE_001')
        self.assertEqual(device.label, 'Test Plant Device')
        self.assertEqual(device.owner, self.user)
        self.assertEqual(device.water_level, 75)
        self.assertEqual(device.moisture_level, 45)
        self.assertEqual(device.water_container_capacity, 2000)
        self.assertTrue(device.is_connected)
        self.assertEqual(device.status, 'online')
    
    def test_device_str_representation(self):
        """Test string representation of device."""
        device = Device.objects.create(
            device_id='TEST_DEVICE_001',
            label='Test Plant Device'
        )
        
        expected = "Test Plant Device (TEST_DEVICE_001)"
        self.assertEqual(str(device), expected)
    
    def test_device_is_online_property(self):
        """Test is_online property."""
        device = Device.objects.create(
            device_id='TEST_DEVICE_001',
            label='Test Device',
            is_connected=True,
            status='online'
        )
        self.assertTrue(device.is_online)
        
        device.status = 'offline'
        device.save()
        self.assertFalse(device.is_online)
        
        device.is_connected = False
        device.save()
        self.assertFalse(device.is_online)
    
    def test_device_water_level_ml_property(self):
        """Test water_level_ml property."""
        device = Device.objects.create(
            device_id='TEST_DEVICE_001',
            label='Test Device',
            water_level=75,
            water_container_capacity=2000
        )
        
        # 75% of 2000ml = 1500ml
        self.assertEqual(device.water_level_ml, 1500)
    
    def test_device_needs_water_refill_property(self):
        """Test needs_water_refill property."""
        device = Device.objects.create(
            device_id='TEST_DEVICE_001',
            label='Test Device',
            water_level=15  # Below 20%
        )
        self.assertTrue(device.needs_water_refill)
        
        device.water_level = 25  # Above 20%
        device.save()
        self.assertFalse(device.needs_water_refill)
    
    def test_device_needs_watering_property(self):
        """Test needs_watering property."""
        device = Device.objects.create(
            device_id='TEST_DEVICE_001',
            label='Test Device',
            moisture_level=25  # Below 30%
        )
        self.assertTrue(device.needs_watering)
        
        device.moisture_level = 35  # Above 30%
        device.save()
        self.assertFalse(device.needs_watering)
    
    def test_device_connect_disconnect(self):
        """Test device connect and disconnect methods."""
        device = Device.objects.create(
            device_id='TEST_DEVICE_001',
            label='Test Device',
            is_connected=False,
            status='offline'
        )
        
        # Test connect
        device.connect()
        device.refresh_from_db()
        self.assertTrue(device.is_connected)
        self.assertEqual(device.status, 'online')
        self.assertIsNotNone(device.last_seen)
        
        # Test disconnect
        device.disconnect()
        device.refresh_from_db()
        self.assertFalse(device.is_connected)
        self.assertEqual(device.status, 'offline')
    
    def test_device_update_water_level(self):
        """Test update_water_level method."""
        device = Device.objects.create(
            device_id='TEST_DEVICE_001',
            label='Test Device',
            water_level=50
        )
        
        # Valid update
        device.update_water_level(75)
        device.refresh_from_db()
        self.assertEqual(device.water_level, 75)
        
        # Invalid update (should not change)
        device.update_water_level(150)  # Above 100%
        device.refresh_from_db()
        self.assertEqual(device.water_level, 75)  # Should remain unchanged
    
    def test_device_update_moisture_level(self):
        """Test update_moisture_level method."""
        device = Device.objects.create(
            device_id='TEST_DEVICE_001',
            label='Test Device',
            moisture_level=30
        )
        
        # Valid update
        device.update_moisture_level(60)
        device.refresh_from_db()
        self.assertEqual(device.moisture_level, 60)
        
        # Invalid update (should not change)
        device.update_moisture_level(150)  # Above 100%
        device.refresh_from_db()
        self.assertEqual(device.moisture_level, 60)  # Should remain unchanged
    
    def test_device_reset_water_level(self):
        """Test reset_water_level method."""
        device = Device.objects.create(
            device_id='TEST_DEVICE_001',
            label='Test Device',
            water_level=25,
            water_reset=True
        )
        
        device.reset_water_level()
        device.refresh_from_db()
        self.assertEqual(device.water_level, 100)
        self.assertFalse(device.water_reset)
    
    def test_device_validation_water_level_too_high(self):
        """Test validation with water level too high."""
        device = Device(
            device_id='TEST_DEVICE_001',
            label='Test Device',
            water_level=150  # Above 100%
        )
        
        with self.assertRaises(ValidationError) as context:
            device.full_clean()
        
        self.assertIn('water_level', str(context.exception))
    
    def test_device_validation_moisture_level_too_high(self):
        """Test validation with moisture level too high."""
        device = Device(
            device_id='TEST_DEVICE_001',
            label='Test Device',
            moisture_level=150  # Above 100%
        )
        
        with self.assertRaises(ValidationError) as context:
            device.full_clean()
        
        self.assertIn('moisture_level', str(context.exception))
    
    def test_device_validation_water_container_capacity_too_low(self):
        """Test validation with water container capacity too low."""
        device = Device(
            device_id='TEST_DEVICE_001',
            label='Test Device',
            water_container_capacity=50  # Below minimum
        )
        
        with self.assertRaises(ValidationError) as context:
            device.full_clean()
        
        self.assertIn('water_container_capacity', str(context.exception))
    
    def test_device_validation_water_container_capacity_too_high(self):
        """Test validation with water container capacity too high."""
        device = Device(
            device_id='TEST_DEVICE_001',
            label='Test Device',
            water_container_capacity=15000  # Above maximum
        )
        
        with self.assertRaises(ValidationError) as context:
            device.full_clean()
        
        self.assertIn('water_container_capacity', str(context.exception))
    
    def test_device_validation_device_id_too_short(self):
        """Test validation with device ID too short."""
        device = Device(
            device_id='AB',  # Too short
            label='Test Device'
        )
        
        with self.assertRaises(ValidationError) as context:
            device.full_clean()
        
        self.assertIn('device_id', str(context.exception))


class TestWaterChartModel(TestCase):
    """Test cases for WaterChart model."""
    
    def setUp(self):
        """Set up test data."""
        self.device = Device.objects.create(
            device_id='TEST_DEVICE_001',
            label='Test Plant Device',
            water_container_capacity=2000
        )
    
    def test_water_chart_creation(self):
        """Test water chart creation with valid data."""
        water_chart = WaterChart.objects.create(
            water_level=80,
            device=self.device
        )
        
        self.assertEqual(water_chart.water_level, 80)
        self.assertEqual(water_chart.device, self.device)
        self.assertIsNotNone(water_chart.recorded_at)
    
    def test_water_chart_str_representation(self):
        """Test string representation of water chart."""
        water_chart = WaterChart.objects.create(
            water_level=80,
            device=self.device
        )
        
        expected = f"Test Plant Device: 80% at {water_chart.recorded_at}"
        self.assertEqual(str(water_chart), expected)
    
    def test_water_chart_repr_representation(self):
        """Test developer representation of water chart."""
        water_chart = WaterChart.objects.create(
            water_level=80,
            device=self.device
        )
        
        expected = f"WaterChart(id={water_chart.id}, device={self.device.device_id}, level=80%)"
        self.assertEqual(repr(water_chart), expected)
