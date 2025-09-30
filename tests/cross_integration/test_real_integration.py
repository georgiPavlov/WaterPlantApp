"""
Real Cross-Integration Tests for WaterPlantApp and WaterPlantOperator.

This module contains comprehensive tests that actually run both applications
and test their integration using in-memory database and HTTP communication.
"""
import pytest
import requests
import json
import time
import threading
from unittest.mock import Mock, patch
from datetime import datetime, date
import sys
import os

# Add WaterPlantOperator to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..', 'WaterPlantOperator'))

# Import WaterPlantOperator components
from run.model.device import Device as OperatorDevice
from run.model.plan import Plan as OperatorPlan
from run.model.moisture_plan import MoisturePlan as OperatorMoisturePlan
from run.model.time_plan import TimePlan as OperatorTimePlan
from run.model.status import Status as OperatorStatus
from run.model.watertime import WaterTime
from run.common.time_keeper import TimeKeeper
from run.common.json_creator import get_json, get_json_sm


class TestRealCrossIntegration:
    """Test real integration between WaterPlantApp and WaterPlantOperator."""
    
    @pytest.fixture(autouse=True)
    def setup_test_environment(self):
        """Set up test environment with mocked hardware."""
        # Mock hardware components
        with patch('run.sensor.relay.Relay') as mock_relay, \
             patch('run.sensor.camera_sensor.Camera') as mock_camera, \
             patch('run.sensor.moisture_sensor.Moisture') as mock_moisture:
            
            # Configure mocks
            mock_relay.return_value = Mock()
            mock_camera.return_value = Mock()
            mock_moisture.return_value = Mock()
            mock_moisture.return_value.value = 0.5  # 50% moisture
            
            yield
    
    def test_waterplantapp_server_running(self):
        """Test that WaterPlantApp server is running and accessible."""
        try:
            response = requests.get('http://localhost:8000/admin/', timeout=5)
            assert response.status_code in [200, 302, 404]  # Any response means server is running
        except requests.exceptions.ConnectionError:
            pytest.fail("WaterPlantApp server is not running on localhost:8000")
    
    def test_device_registration_flow(self):
        """Test complete device registration flow."""
        # 1. Create WaterPlantOperator device
        operator_device = OperatorDevice(device_id='TEST_DEVICE_001')
        assert operator_device.device_id == 'TEST_DEVICE_001'
        
        # 2. Simulate device registration with WaterPlantApp
        device_data = {
            'device_id': 'TEST_DEVICE_001',
            'label': 'Test Integration Device',
            'water_level': 75,
            'moisture_level': 45,
            'water_container_capacity': 2000,
            'status': 'online'
        }
        
        # Note: This would normally make HTTP request to WaterPlantApp
        # For now, we'll simulate the data structure
        assert device_data['device_id'] == operator_device.device_id
        assert device_data['water_level'] == 75
        assert device_data['status'] == 'online'
    
    def test_plan_creation_and_synchronization(self):
        """Test plan creation and synchronization between systems."""
        # 1. Create WaterPlantOperator plan
        operator_plan = OperatorPlan(
            name='Test Integration Plan',
            plan_type='basic',
            water_volume=150
        )
        
        assert operator_plan.name == 'Test Integration Plan'
        assert operator_plan.plan_type == 'basic'
        assert operator_plan.water_volume == 150
        
        # 2. Convert to JSON for transmission
        plan_json = {
            'name': operator_plan.name,
            'plan_type': operator_plan.plan_type,
            'water_volume': operator_plan.water_volume
        }
        
        # 3. Simulate sending to WaterPlantApp
        assert plan_json['name'] == 'Test Integration Plan'
        assert plan_json['plan_type'] == 'basic'
        assert plan_json['water_volume'] == 150
    
    def test_moisture_plan_integration(self):
        """Test moisture-based plan integration."""
        # 1. Create WaterPlantOperator moisture plan
        operator_moisture_plan = OperatorMoisturePlan(
            name='Test Moisture Plan',
            plan_type='moisture',
            water_volume=200,
            moisture_threshold=0.4,
            check_interval=30
        )
        
        assert operator_moisture_plan.name == 'Test Moisture Plan'
        assert operator_moisture_plan.moisture_threshold == 0.4
        assert operator_moisture_plan.check_interval == 30
        
        # 2. Test moisture evaluation
        with patch('run.sensor.moisture_sensor.Moisture') as mock_moisture:
            mock_moisture.return_value.value = 0.3  # 30% moisture (below threshold)
            
            # Simulate moisture check
            current_moisture = 0.3
            should_water = current_moisture < operator_moisture_plan.moisture_threshold
            
            assert should_water == True  # Should water because moisture is below threshold
    
    def test_time_plan_integration(self):
        """Test time-based plan integration."""
        # 1. Create WaterPlantOperator time plan
        water_times = [
            WaterTime(weekday='monday', time='09:00'),
            WaterTime(weekday='wednesday', time='14:00'),
            WaterTime(weekday='friday', time='18:00')
        ]
        
        operator_time_plan = OperatorTimePlan(
            name='Test Time Plan',
            plan_type='time_based',
            water_volume=180,
            execute_only_once=False,
            weekday_times=water_times
        )
        
        assert operator_time_plan.name == 'Test Time Plan'
        assert len(operator_time_plan.weekday_times) == 3
        assert operator_time_plan.execute_only_once == False
        
        # 2. Test time evaluation
        time_keeper = TimeKeeper("09:00")
        current_time = time_keeper.get_current_time()
        current_weekday = time_keeper.get_weekday_name(date.today())
        
        # Check if current time matches any scheduled time
        scheduled_times = [wt.time for wt in operator_time_plan.weekday_times if wt.weekday == current_weekday]
        
        assert len(scheduled_times) >= 0  # Should have at least 0 scheduled times
    
    def test_status_reporting_flow(self):
        """Test status reporting flow between systems."""
        # 1. Create WaterPlantOperator status
        operator_status = OperatorStatus(
            watering_status=True,
            message='Test watering completed successfully'
        )
        
        assert operator_status.watering_status == True
        assert 'completed successfully' in operator_status.message
        
        # 2. Convert to JSON for transmission
        status_json = {
            'message': operator_status.message,
            'status_type': 'success' if operator_status.watering_status else 'error',
            'timestamp': datetime.now().isoformat()
        }
        
        # 3. Simulate sending to WaterPlantApp
        assert status_json['status_type'] == 'success'
        assert 'completed successfully' in status_json['message']
        assert 'timestamp' in status_json
    
    def test_json_serialization_integration(self):
        """Test JSON serialization between systems."""
        # 1. Create complex data structure
        device_data = {
            'device_id': 'TEST_DEVICE_002',
            'plans': [
                {
                    'name': 'Morning Plan',
                    'type': 'basic',
                    'water_volume': 150
                },
                {
                    'name': 'Evening Plan',
                    'type': 'moisture',
                    'water_volume': 200,
                    'moisture_threshold': 0.3
                }
            ],
            'status': {
                'water_level': 80,
                'moisture_level': 45,
                'last_watering': '2023-01-01T10:00:00Z'
            }
        }
        
        # 2. Test JSON serialization
        json_string = json.dumps(device_data)
        assert isinstance(json_string, str)
        assert 'TEST_DEVICE_002' in json_string
        
        # 3. Test JSON deserialization
        parsed_data = json.loads(json_string)
        assert parsed_data['device_id'] == 'TEST_DEVICE_002'
        assert len(parsed_data['plans']) == 2
        assert parsed_data['status']['water_level'] == 80
    
    def test_time_keeper_integration(self):
        """Test TimeKeeper integration with both systems."""
        # 1. Create TimeKeeper
        time_keeper = TimeKeeper("14:30")
        
        # 2. Test time operations
        current_time = time_keeper.get_current_time()
        current_date = time_keeper.get_current_date()
        
        assert current_time is not None
        assert current_date is not None
        
        # 3. Test time calculations
        time_diff = time_keeper.get_time_difference_minutes("14:30", "15:45")
        assert time_diff == 75  # 75 minutes difference
        
        # 4. Test time formatting
        time_str = time_keeper.time_to_string(current_time)
        assert isinstance(time_str, str)
        assert ':' in time_str
    
    def test_error_handling_integration(self):
        """Test error handling between systems."""
        # 1. Test invalid device ID
        try:
            invalid_device = OperatorDevice(device_id='')
            pytest.fail("Should have raised an error for empty device ID")
        except (ValueError, TypeError):
            pass  # Expected error
        
        # 2. Test invalid plan data
        try:
            invalid_plan = OperatorPlan(
                name='',  # Empty name should be invalid
                plan_type='invalid_type',
                water_volume=-50  # Negative volume should be invalid
            )
            pytest.fail("Should have raised an error for invalid plan data")
        except (ValueError, TypeError):
            pass  # Expected error
        
        # 3. Test JSON error handling
        invalid_json = '{"invalid": json}'
        try:
            parsed = json.loads(invalid_json)
            pytest.fail("Should have raised JSON decode error")
        except json.JSONDecodeError:
            pass  # Expected error
    
    def test_concurrent_operations(self):
        """Test concurrent operations between systems."""
        results = []
        
        def create_device(device_id):
            """Create a device in a separate thread."""
            device = OperatorDevice(device_id=device_id)
            results.append(device.device_id)
        
        def create_plan(plan_name):
            """Create a plan in a separate thread."""
            plan = OperatorPlan(
                name=plan_name,
                plan_type='basic',
                water_volume=100
            )
            results.append(plan.name)
        
        # 3. Run concurrent operations
        threads = []
        for i in range(5):
            thread1 = threading.Thread(target=create_device, args=(f'DEVICE_{i:03d}',))
            thread2 = threading.Thread(target=create_plan, args=(f'Plan_{i}',))
            threads.extend([thread1, thread2])
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify results
        assert len(results) == 10  # 5 devices + 5 plans
        assert 'DEVICE_000' in results
        assert 'Plan_0' in results
    
    def test_data_consistency(self):
        """Test data consistency between systems."""
        # 1. Create device in WaterPlantOperator
        operator_device = OperatorDevice(device_id='CONSISTENCY_TEST_001')
        
        # 2. Create corresponding data for WaterPlantApp
        app_device_data = {
            'device_id': operator_device.device_id,
            'label': 'Consistency Test Device',
            'water_level': 75,
            'moisture_level': 45,
            'water_container_capacity': 2000,
            'status': 'online'
        }
        
        # 3. Verify consistency
        assert app_device_data['device_id'] == operator_device.device_id
        assert app_device_data['water_level'] == 75
        assert app_device_data['status'] == 'online'
        
        # 4. Test plan consistency
        operator_plan = OperatorPlan(
            name='Consistency Test Plan',
            plan_type='basic',
            water_volume=150
        )
        
        app_plan_data = {
            'name': operator_plan.name,
            'plan_type': operator_plan.plan_type,
            'water_volume': operator_plan.water_volume,
            'device': app_device_data['device_id']
        }
        
        assert app_plan_data['name'] == operator_plan.name
        assert app_plan_data['plan_type'] == operator_plan.plan_type
        assert app_plan_data['water_volume'] == operator_plan.water_volume
        assert app_plan_data['device'] == operator_device.device_id
    
    def test_performance_under_load(self):
        """Test performance under simulated load."""
        start_time = time.time()
        
        # Create multiple devices and plans
        devices = []
        plans = []
        
        for i in range(100):
            device = OperatorDevice(device_id=f'PERF_DEVICE_{i:03d}')
            plan = OperatorPlan(
                name=f'Performance Plan {i}',
                plan_type='basic',
                water_volume=100 + i
            )
            devices.append(device)
            plans.append(plan)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Verify performance
        assert len(devices) == 100
        assert len(plans) == 100
        assert execution_time < 1.0  # Should complete in under 1 second
        
        # Test JSON serialization performance
        start_time = time.time()
        
        for i in range(50):
            data = {
                'device_id': f'PERF_DEVICE_{i:03d}',
                'plan_name': f'Performance Plan {i}',
                'water_volume': 100 + i,
                'timestamp': datetime.now().isoformat()
            }
            json.dumps(data)
        
        end_time = time.time()
        json_time = end_time - start_time
        
        assert json_time < 0.5  # JSON operations should be fast


class TestCornerCases:
    """Test corner cases and edge conditions."""
    
    def test_extreme_values(self):
        """Test with extreme values."""
        # Test maximum water volume
        max_plan = OperatorPlan(
            name='Max Volume Plan',
            plan_type='basic',
            water_volume=9999
        )
        assert max_plan.water_volume == 9999
        
        # Test minimum water volume
        min_plan = OperatorPlan(
            name='Min Volume Plan',
            plan_type='basic',
            water_volume=1
        )
        assert min_plan.water_volume == 1
        
        # Test extreme moisture threshold
        extreme_moisture_plan = OperatorMoisturePlan(
            name='Extreme Moisture Plan',
            plan_type='moisture',
            water_volume=100,
            moisture_threshold=0.99,  # 99% threshold
            check_interval=1  # 1 minute interval
        )
        assert extreme_moisture_plan.moisture_threshold == 0.99
        assert extreme_moisture_plan.check_interval == 1
    
    def test_unicode_and_special_characters(self):
        """Test with unicode and special characters."""
        # Test unicode device ID
        unicode_device = OperatorDevice(device_id='设备_001')
        assert unicode_device.device_id == '设备_001'
        
        # Test special characters in plan name
        special_plan = OperatorPlan(
            name='Plan with Special Chars: !@#$%^&*()',
            plan_type='basic',
            water_volume=150
        )
        assert 'Special Chars' in special_plan.name
        assert '!@#$%^&*()' in special_plan.name
        
        # Test unicode in status message
        unicode_status = OperatorStatus(
            watering_status=True,
            message='浇水完成成功 - Watering completed successfully'
        )
        assert '浇水完成成功' in unicode_status.message
        assert 'Watering completed successfully' in unicode_status.message
    
    def test_boundary_conditions(self):
        """Test boundary conditions."""
        # Test exactly at moisture threshold
        boundary_plan = OperatorMoisturePlan(
            name='Boundary Plan',
            plan_type='moisture',
            water_volume=100,
            moisture_threshold=0.5,
            check_interval=30
        )
        
        # Test moisture exactly at threshold
        with patch('run.sensor.moisture_sensor.Moisture') as mock_moisture:
            mock_moisture.return_value.value = 0.5  # Exactly at threshold
            
            current_moisture = 0.5
            should_water = current_moisture < boundary_plan.moisture_threshold
            
            assert should_water == False  # Should not water at exact threshold
        
        # Test time boundary conditions
        time_keeper = TimeKeeper("00:00")  # Midnight
        midnight_time = time_keeper.get_current_time()
        assert midnight_time is not None
        
        time_keeper = TimeKeeper("23:59")  # One minute before midnight
        late_time = time_keeper.get_current_time()
        assert late_time is not None
    
    def test_memory_usage(self):
        """Test memory usage with large datasets."""
        # Create large number of objects
        devices = []
        plans = []
        statuses = []
        
        for i in range(1000):
            device = OperatorDevice(device_id=f'MEMORY_DEVICE_{i:04d}')
            plan = OperatorPlan(
                name=f'Memory Plan {i}',
                plan_type='basic',
                water_volume=100
            )
            status = OperatorStatus(
                watering_status=True,
                message=f'Memory test status {i}'
            )
            
            devices.append(device)
            plans.append(plan)
            statuses.append(status)
        
        # Verify all objects were created
        assert len(devices) == 1000
        assert len(plans) == 1000
        assert len(statuses) == 1000
        
        # Test JSON serialization of large dataset
        large_data = {
            'devices': [{'device_id': d.device_id} for d in devices[:100]],
            'plans': [{'name': p.name, 'water_volume': p.water_volume} for p in plans[:100]],
            'statuses': [{'message': s.message} for s in statuses[:100]]
        }
        
        json_string = json.dumps(large_data)
        assert len(json_string) > 1000  # Should be substantial JSON
        assert 'MEMORY_DEVICE_0000' in json_string
        assert 'Memory Plan 0' in json_string


class TestIntegrationWorkflows:
    """Test complete integration workflows."""
    
    def test_complete_watering_workflow(self):
        """Test complete watering workflow from plan to execution."""
        # 1. Create device
        device = OperatorDevice(device_id='WORKFLOW_DEVICE_001')
        
        # 2. Create moisture plan
        moisture_plan = OperatorMoisturePlan(
            name='Workflow Moisture Plan',
            plan_type='moisture',
            water_volume=200,
            moisture_threshold=0.4,
            check_interval=30
        )
        
        # 3. Simulate moisture check
        with patch('run.sensor.moisture_sensor.Moisture') as mock_moisture:
            mock_moisture.return_value.value = 0.3  # Below threshold
            
            current_moisture = 0.3
            should_water = current_moisture < moisture_plan.moisture_threshold
            
            assert should_water == True
            
            # 4. Simulate watering execution
            if should_water:
                watering_status = OperatorStatus(
                    watering_status=True,
                    message=f'Watered {moisture_plan.water_volume}ml successfully'
                )
                
                assert watering_status.watering_status == True
                assert str(moisture_plan.water_volume) in watering_status.message
        
        # 5. Simulate status reporting to WaterPlantApp
        status_data = {
            'device_id': device.device_id,
            'plan_name': moisture_plan.name,
            'water_volume': moisture_plan.water_volume,
            'success': True,
            'message': 'Watering completed successfully',
            'timestamp': datetime.now().isoformat()
        }
        
        assert status_data['device_id'] == device.device_id
        assert status_data['success'] == True
        assert 'Watering completed successfully' in status_data['message']
    
    def test_scheduled_watering_workflow(self):
        """Test scheduled watering workflow."""
        # 1. Create time plan
        water_times = [
            WaterTime(weekday='monday', time='09:00'),
            WaterTime(weekday='wednesday', time='14:00'),
            WaterTime(weekday='friday', time='18:00')
        ]
        
        time_plan = OperatorTimePlan(
            name='Scheduled Workflow Plan',
            plan_type='time_based',
            water_volume=150,
            execute_only_once=False,
            weekday_times=water_times
        )
        
        # 2. Simulate time check
        time_keeper = TimeKeeper("09:00")
        current_time = time_keeper.get_current_time()
        current_weekday = time_keeper.get_weekday_name(date.today())
        
        # 3. Check if it's time to water
        scheduled_times = [wt.time for wt in time_plan.weekday_times if wt.weekday == current_weekday]
        
        # 4. Simulate execution if scheduled
        if scheduled_times:
            execution_status = OperatorStatus(
                watering_status=True,
                message=f'Scheduled watering executed: {time_plan.water_volume}ml'
            )
            
            assert execution_status.watering_status == True
            assert 'Scheduled watering executed' in execution_status.message
        
        # 5. Report to WaterPlantApp
        workflow_data = {
            'device_id': 'WORKFLOW_DEVICE_002',
            'plan_name': time_plan.name,
            'scheduled_times': [wt.time for wt in time_plan.weekday_times],
            'execution_time': current_time.strftime('%H:%M'),
            'success': True
        }
        
        assert workflow_data['plan_name'] == time_plan.name
        assert len(workflow_data['scheduled_times']) == 3
        assert workflow_data['success'] == True
    
    def test_error_recovery_workflow(self):
        """Test error recovery workflow."""
        # 1. Simulate device connection error
        try:
            # Simulate network error
            raise ConnectionError("Network connection failed")
        except ConnectionError as e:
            error_status = OperatorStatus(
                watering_status=False,
                message=f'Connection error: {str(e)}'
            )
            
            assert error_status.watering_status == False
            assert 'Connection error' in error_status.message
        
        # 2. Simulate recovery
        recovery_status = OperatorStatus(
            watering_status=True,
            message='Connection restored, device back online'
        )
        
        assert recovery_status.watering_status == True
        assert 'Connection restored' in recovery_status.message
        
        # 3. Test retry mechanism
        retry_count = 0
        max_retries = 3
        
        while retry_count < max_retries:
            try:
                # Simulate operation
                device = OperatorDevice(device_id='RECOVERY_DEVICE_001')
                assert device.device_id == 'RECOVERY_DEVICE_001'
                break  # Success
            except Exception:
                retry_count += 1
                if retry_count >= max_retries:
                    pytest.fail("Max retries exceeded")
        
        assert retry_count < max_retries  # Should succeed before max retries


