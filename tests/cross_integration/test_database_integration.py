"""
Database Integration Tests for WaterPlantApp and WaterPlantOperator.

This module tests the database integration between WaterPlantApp (Django)
and WaterPlantOperator using in-memory database and data synchronization.
"""
import pytest
import os
import sys
import django
from datetime import datetime, date
from unittest.mock import Mock, patch

# Add WaterPlantOperator to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..', 'WaterPlantOperator'))

# Configure Django settings for testing
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pycharmtut.test_settings')
django.setup()

# Import Django models
from gadget_communicator_pull.models import (
    Device as AppDevice,
    BasicPlan as AppBasicPlan,
    MoisturePlan as AppMoisturePlan,
    TimePlan as AppTimePlan,
    WaterTime as AppWaterTime,
    Status as AppStatus,
    WaterChart as AppWaterChart
)

# Import WaterPlantOperator components
from run.model.device import Device as OperatorDevice
from run.model.plan import Plan as OperatorPlan
from run.model.moisture_plan import MoisturePlan as OperatorMoisturePlan
from run.model.time_plan import TimePlan as OperatorTimePlan
from run.model.status import Status as OperatorStatus
from run.model.watertime import WaterTime as OperatorWaterTime


class TestDatabaseIntegration:
    """Test database integration between WaterPlantApp and WaterPlantOperator."""
    
    @pytest.fixture(autouse=True)
    def setup_test_environment(self):
        """Set up test environment with mocked hardware."""
        with patch('run.sensor.relay.Relay') as mock_relay, \
             patch('run.sensor.camera_sensor.Camera') as mock_camera, \
             patch('run.sensor.moisture_sensor.Moisture') as mock_moisture:
            
            mock_relay.return_value = Mock()
            mock_camera.return_value = Mock()
            mock_moisture.return_value = Mock()
            mock_moisture.return_value.value = 0.5
            
            yield
    
    @pytest.mark.django_db
    @pytest.mark.django_db
    def test_device_synchronization(self):
        """Test device synchronization between systems."""
        # 1. Create WaterPlantOperator device
        operator_device = OperatorDevice(device_id='DB_SYNC_DEVICE_001')
        
        # 2. Create corresponding WaterPlantApp device
        app_device = AppDevice.objects.create(
            device_id=operator_device.device_id,
            label='Database Sync Test Device',
            water_level=75,
            moisture_level=45,
            water_container_capacity=2000,
            status='online'
        )
        
        # 3. Verify synchronization
        assert app_device.device_id == operator_device.device_id
        assert app_device.water_level == 75
        assert app_device.moisture_level == 45
        assert app_device.status == 'online'
        
        # 4. Test data consistency
        assert app_device.device_id == 'DB_SYNC_DEVICE_001'
        assert app_device.label == 'Database Sync Test Device'
        assert app_device.water_container_capacity == 2000
    
    @pytest.mark.django_db
    def test_basic_plan_synchronization(self):
        """Test basic plan synchronization between systems."""
        # 1. Create WaterPlantOperator plan
        operator_plan = OperatorPlan(
            name='Database Sync Basic Plan',
            plan_type='basic',
            water_volume=150
        )
        
        # 2. Create corresponding WaterPlantApp plan
        app_plan = AppBasicPlan.objects.create(
            name=operator_plan.name,
            plan_type=operator_plan.plan_type,
            water_volume=operator_plan.water_volume
        )
        
        # 3. Verify synchronization
        assert app_plan.name == operator_plan.name
        assert app_plan.plan_type == operator_plan.plan_type
        assert app_plan.water_volume == operator_plan.water_volume
        
        # 4. Test plan properties
        assert app_plan.is_executable == True
        assert app_plan.plan_type == 'basic'
    
    @pytest.mark.django_db
    def test_moisture_plan_synchronization(self):
        """Test moisture plan synchronization between systems."""
        # 1. Create WaterPlantOperator moisture plan
        operator_moisture_plan = OperatorMoisturePlan(
            name='Database Sync Moisture Plan',
            plan_type='moisture',
            water_volume=200,
            moisture_threshold=0.4,
            check_interval=30
        )
        
        # 2. Create corresponding WaterPlantApp moisture plan
        app_moisture_plan = AppMoisturePlan.objects.create(
            name=operator_moisture_plan.name,
            plan_type=operator_moisture_plan.plan_type,
            water_volume=operator_moisture_plan.water_volume,
            moisture_threshold=operator_moisture_plan.moisture_threshold,
            check_interval=operator_moisture_plan.check_interval
        )
        
        # 3. Verify synchronization
        assert app_moisture_plan.name == operator_moisture_plan.name
        assert app_moisture_plan.moisture_threshold == operator_moisture_plan.moisture_threshold
        assert app_moisture_plan.check_interval == operator_moisture_plan.check_interval
        
        # 4. Test moisture plan properties
        assert app_moisture_plan.moisture_threshold_percentage == 40.0  # 0.4 * 100
        assert app_moisture_plan.is_executable == True
    
    @pytest.mark.django_db
    def test_time_plan_synchronization(self):
        """Test time plan synchronization between systems."""
        # 1. Create WaterPlantOperator time plan
        operator_water_times = [
            OperatorWaterTime(weekday='monday', time_water='09:00'),
            OperatorWaterTime(weekday='wednesday', time_water='14:00'),
            OperatorWaterTime(weekday='friday', time_water='18:00')
        ]
        
        operator_time_plan = OperatorTimePlan(
            name='Database Sync Time Plan',
            plan_type='time_based',
            water_volume=180,
            execute_only_once=False,
            weekday_times=operator_water_times
        )
        
        # 2. Create corresponding WaterPlantApp time plan
        app_time_plan = AppTimePlan.objects.create(
            name=operator_time_plan.name,
            plan_type=operator_time_plan.plan_type,
            water_volume=operator_time_plan.water_volume,
            execute_only_once=operator_time_plan.execute_only_once
        )
        
        # 3. Create corresponding WaterTime objects
        for operator_water_time in operator_water_times:
            AppWaterTime.objects.create(
                time_plan=app_time_plan,
                weekday=operator_water_time.weekday,
                time=operator_water_time.time
            )
        
        # 4. Verify synchronization
        assert app_time_plan.name == operator_time_plan.name
        assert app_time_plan.water_volume == operator_time_plan.water_volume
        assert app_time_plan.execute_only_once == operator_time_plan.execute_only_once
        
        # 5. Verify water times
        app_water_times = app_time_plan.get_weekday_times()
        assert len(app_water_times) == 3
        
        weekday_times = [wt.weekday for wt in app_water_times]
        assert 'monday' in weekday_times
        assert 'wednesday' in weekday_times
        assert 'friday' in weekday_times
    
    @pytest.mark.django_db
    def test_status_synchronization(self):
        """Test status synchronization between systems."""
        # 1. Create WaterPlantOperator status
        operator_status = OperatorStatus(
            watering_status=True,
            message='Database sync watering completed successfully'
        )
        
        # 2. Create corresponding WaterPlantApp status
        app_status = AppStatus.objects.create(
            message=operator_status.message,
            execution_status=operator_status.watering_status
        )
        
        # 3. Verify synchronization
        assert app_status.message == operator_status.message
        assert app_status.execution_status == operator_status.watering_status
        assert app_status.is_success == True
        assert app_status.is_failure == False
    
    @pytest.mark.django_db
    def test_water_chart_integration(self):
        """Test water chart integration."""
        # 1. Create device
        device = AppDevice.objects.create(
            device_id='WATER_CHART_DEVICE_001',
            label='Water Chart Test Device',
            water_level=80,
            moisture_level=45,
            water_container_capacity=2000,
            status='online'
        )
        
        # 2. Create water chart entry
        water_chart = AppWaterChart.objects.create(
            device=device,
            water_level=80,
        )
        
        # 3. Verify water chart properties
        assert water_chart.device == device
        assert water_chart.water_level == 80
        assert water_chart.water_level_ml == 1600  # 80% of 2000ml
    
    @pytest.mark.django_db
    def test_data_consistency_across_systems(self):
        """Test data consistency across both systems."""
        # 1. Create WaterPlantOperator components
        operator_device = OperatorDevice(device_id='CONSISTENCY_DEVICE_001')
        operator_plan = OperatorPlan(
            name='Consistency Test Plan',
            plan_type='basic',
            water_volume=150
        )
        operator_status = OperatorStatus(
            watering_status=True,
            message='Consistency test completed'
        )
        
        # 2. Create corresponding WaterPlantApp components
        app_device = AppDevice.objects.create(
            device_id=operator_device.device_id,
            label='Consistency Test Device',
            water_level=75,
            moisture_level=45,
            water_container_capacity=2000,
            status='online'
        )
        
        app_plan = AppBasicPlan.objects.create(
            name=operator_plan.name,
            plan_type=operator_plan.plan_type,
            water_volume=operator_plan.water_volume
        )
        
        app_status = AppStatus.objects.create(
            device=app_device,
            message=operator_status.message,
            execution_status=operator_status.watering_status
        )
        
        # 3. Verify cross-system consistency
        assert app_device.device_id == operator_device.device_id
        assert app_plan.name == operator_plan.name
        assert app_plan.water_volume == operator_plan.water_volume
        assert app_status.message == operator_status.message
        assert app_status.execution_status == operator_status.watering_status
    
    @pytest.mark.django_db
    def test_database_transactions(self):
        """Test database transactions and rollback."""
        # 1. Test successful transaction
        try:
            with django.db.transaction.atomic():
                device = AppDevice.objects.create(
                    device_id='TRANSACTION_DEVICE_001',
                    label='Transaction Test Device',
                    water_level=75,
                    moisture_level=45,
                    water_container_capacity=2000,
                    status='online'
                )
                
                plan = AppBasicPlan.objects.create(
                    name='Transaction Test Plan',
                    plan_type='basic',
                    water_volume=150
                )
                
                status = AppStatus.objects.create(
                    message='Transaction test completed',
                    status_type='success'
                )
                
                # Verify objects were created
                assert device.device_id == 'TRANSACTION_DEVICE_001'
                assert plan.name == 'Transaction Test Plan'
                assert status.message == 'Transaction test completed'
                
        except Exception as e:
            pytest.fail(f"Transaction failed: {e}")
        
        # 2. Test rollback on error
        try:
            with django.db.transaction.atomic():
                AppDevice.objects.create(
                    device_id='ROLLBACK_DEVICE_001',
                    label='Rollback Test Device',
                    water_level=75,
                    moisture_level=45,
                    water_container_capacity=2000,
                    status='online'
                )
                
                # Intentionally cause an error
                raise Exception("Simulated error for rollback test")
                
        except Exception:
            pass  # Expected error
        
        # Verify rollback worked
        with pytest.raises(AppDevice.DoesNotExist):
            AppDevice.objects.get(device_id='ROLLBACK_DEVICE_001')
    
    @pytest.mark.django_db
    def test_database_performance(self):
        """Test database performance with multiple operations."""
        start_time = datetime.now()
        
        # Create multiple devices and plans
        devices = []
        plans = []
        statuses = []
        
        for i in range(100):
            device = AppDevice.objects.create(
                device_id=f'PERF_DEVICE_{i:03d}',
                label=f'Performance Test Device {i}',
                water_level=75,
                moisture_level=45,
                water_container_capacity=2000,
                status='online'
            )
            
            plan = AppBasicPlan.objects.create(
                name=f'Performance Test Plan {i}',
                plan_type='basic',
                water_volume=100 + i
            )
            
            status = AppStatus.objects.create(
                message=f'Performance test status {i}',
                status_type='success'
            )
            
            devices.append(device)
            plans.append(plan)
            statuses.append(status)
        
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        # Verify performance
        assert len(devices) == 100
        assert len(plans) == 100
        assert len(statuses) == 100
        assert execution_time < 5.0  # Should complete in under 5 seconds
        
        # Test query performance
        start_time = datetime.now()
        
        # Query all devices
        all_devices = AppDevice.objects.all()
        assert all_devices.count() >= 100
        
        # Query devices by status
        online_devices = AppDevice.objects.filter(status='online')
        assert online_devices.count() >= 100
        
        # Query plans by type
        basic_plans = AppBasicPlan.objects.filter(plan_type='basic')
        assert basic_plans.count() >= 100
        
        end_time = datetime.now()
        query_time = (end_time - start_time).total_seconds()
        
        assert query_time < 1.0  # Queries should be fast
    
    @pytest.mark.django_db
    def test_database_constraints(self):
        """Test database constraints and validation."""
        # 1. Test unique constraint on device_id
        import uuid
        unique_device_id = f'UNIQUE_DEVICE_{uuid.uuid4().hex[:8]}'
        AppDevice.objects.create(
            device_id=unique_device_id,
            label='Unique Test Device',
            water_level=75,
            moisture_level=45,
            water_container_capacity=2000,
            status='online'
        )
        
        # Try to create another device with same device_id
        with pytest.raises(django.db.IntegrityError):
            AppDevice.objects.create(
                device_id=unique_device_id,  # Same device_id
                label='Duplicate Device',
                water_level=75,
                moisture_level=45,
                water_container_capacity=2000,
                status='online'
            )
        
        # 2. Test validation constraints
        with pytest.raises(django.core.exceptions.ValidationError):
            device = AppDevice(
                device_id='VALIDATION_DEVICE_001',
                label='Validation Test Device',
                water_level=150,  # Invalid: > 100
                moisture_level=45,
                water_container_capacity=2000,
                status='online'
            )
            device.full_clean()
    
    @pytest.mark.django_db
    def test_database_relationships(self):
        """Test database relationships between models."""
        # 1. Create device
        device = AppDevice.objects.create(
            device_id='RELATIONSHIP_DEVICE_001',
            label='Relationship Test Device',
            water_level=75,
            moisture_level=45,
            water_container_capacity=2000,
            status='online'
        )
        
        # 2. Create plans associated with device
        basic_plan = AppBasicPlan.objects.create(
            device=device,
            name='Device Basic Plan',
            plan_type='basic',
            water_volume=150
        )
        
        moisture_plan = AppMoisturePlan.objects.create(
            device=device,
            name='Device Moisture Plan',
            plan_type='moisture',
            water_volume=200,
            moisture_threshold=0.4,
            check_interval=30
        )
        
        # 3. Create status associated with device
        status = AppStatus.objects.create(
            device=device,
            message='Device relationship test',
            execution_status=True
        )
        
        # 4. Create water chart entries
        water_chart1 = AppWaterChart.objects.create(
            device=device,
            water_level=75,
        )
        
        water_chart2 = AppWaterChart.objects.create(
            device=device,
            water_level=80,
        )
        
        # 5. Test relationships
        assert water_chart1.device == device
        assert water_chart2.device == device
        
        # Test device methods
        device_plans = device.basic_plans.all()
        assert device_plans.count() == 1
        assert device_plans.first().name == 'Device Basic Plan'
        
        device_moisture_plans = device.moisture_plans.all()
        assert device_moisture_plans.count() == 1
        assert device_moisture_plans.first().name == 'Device Moisture Plan'
        
        device_statuses = device.statuses.all()
        assert device_statuses.count() == 1
        assert device_statuses.first().message == 'Device relationship test'
    
    @pytest.mark.django_db
    def test_database_migrations(self):
        """Test database migrations and schema changes."""
        # 1. Test that all models can be created
        device = AppDevice.objects.create(
            device_id='MIGRATION_DEVICE_001',
            label='Migration Test Device',
            water_level=75,
            moisture_level=45,
            water_container_capacity=2000,
            status='online'
        )
        
        basic_plan = AppBasicPlan.objects.create(
            name='Migration Basic Plan',
            plan_type='basic',
            water_volume=150
        )
        
        moisture_plan = AppMoisturePlan.objects.create(
            name='Migration Moisture Plan',
            plan_type='moisture',
            water_volume=200,
            moisture_threshold=0.4,
            check_interval=30
        )
        
        time_plan = AppTimePlan.objects.create(
            name='Migration Time Plan',
            plan_type='time_based',
            water_volume=180,
            execute_only_once=False
        )
        
        status = AppStatus.objects.create(
            message='Migration test completed',
            status_type='success'
        )
        
        water_chart = AppWaterChart.objects.create(
            device=device,
            water_level=75,
        )
        
        # 2. Verify all objects were created successfully
        assert device.device_id == 'MIGRATION_DEVICE_001'
        assert basic_plan.name == 'Migration Basic Plan'
        assert moisture_plan.name == 'Migration Moisture Plan'
        assert time_plan.name == 'Migration Time Plan'
        assert status.message == 'Migration test completed'
        assert water_chart.device == device
    
    @pytest.mark.django_db
    def test_database_cleanup(self):
        """Test database cleanup and data integrity."""
        # 1. Create test data
        device = AppDevice.objects.create(
            device_id='CLEANUP_DEVICE_001',
            label='Cleanup Test Device',
            water_level=75,
            moisture_level=45,
            water_container_capacity=2000,
            status='online'
        )
        
        plan = AppBasicPlan.objects.create(
            name='Cleanup Test Plan',
            plan_type='basic',
            water_volume=150
        )
        
        status = AppStatus.objects.create(
            message='Cleanup test',
            status_type='success'
        )
        
        water_chart = AppWaterChart.objects.create(
            device=device,
            water_level=75,
        )
        
        # 2. Verify data exists
        assert AppDevice.objects.filter(device_id='CLEANUP_DEVICE_001').exists()
        assert AppBasicPlan.objects.filter(name='Cleanup Test Plan').exists()
        assert AppStatus.objects.filter(message='Cleanup test').exists()
        assert AppWaterChart.objects.filter(device=device).exists()
        
        # 3. Clean up data
        water_chart.delete()
        status.delete()
        plan.delete()
        device.delete()
        
        # 4. Verify cleanup
        assert not AppDevice.objects.filter(device_id='CLEANUP_DEVICE_001').exists()
        assert not AppBasicPlan.objects.filter(name='Cleanup Test Plan').exists()
        assert not AppStatus.objects.filter(message='Cleanup test').exists()
        assert not AppWaterChart.objects.filter(device=device).exists()
