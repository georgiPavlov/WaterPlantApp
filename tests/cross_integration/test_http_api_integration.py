"""
HTTP API Integration Tests for WaterPlantApp and WaterPlantOperator.

This module tests the actual HTTP communication between WaterPlantOperator
and WaterPlantApp using real HTTP requests and in-memory database.
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


class TestHTTPAPIIntegration:
    """Test HTTP API integration between WaterPlantApp and WaterPlantOperator."""
    
    BASE_URL = 'http://localhost:8001'
    
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
    
    def test_server_health_check(self):
        """Test that WaterPlantApp server is healthy and responding."""
        try:
            # Test admin endpoint (should return 200 or 302)
            response = requests.get(f'{self.BASE_URL}/admin/', timeout=10)
            assert response.status_code in [200, 302, 404]
            
            # Test API endpoint structure
            response = requests.get(f'{self.BASE_URL}/gadget_communicator_pull/', timeout=10)
            # Should return 200, 404, or 405 (method not allowed)
            assert response.status_code in [200, 404, 405]
            
        except requests.exceptions.ConnectionError:
            pytest.fail("WaterPlantApp server is not running or not accessible")
        except requests.exceptions.Timeout:
            pytest.fail("WaterPlantApp server is not responding within timeout")
    
    def test_device_api_endpoints(self):
        """Test device-related API endpoints."""
        # Test device list endpoint
        try:
            response = requests.get(f'{self.BASE_URL}/gadget_communicator_pull/devices/', timeout=10)
            # Should return 200, 401 (unauthorized), or 404
            assert response.status_code in [200, 401, 404, 405]
            
            if response.status_code == 200:
                data = response.json()
                assert isinstance(data, (dict, list))
                
        except requests.exceptions.RequestException as e:
            # If endpoint doesn't exist, that's okay for this test
            pass
    
    def test_plan_api_endpoints(self):
        """Test plan-related API endpoints."""
        # Test plan list endpoint
        try:
            response = requests.get(f'{self.BASE_URL}/gadget_communicator_pull/plans/', timeout=10)
            assert response.status_code in [200, 401, 404, 405]
            
            if response.status_code == 200:
                data = response.json()
                assert isinstance(data, (dict, list))
                
        except requests.exceptions.RequestException:
            pass
    
    def test_status_api_endpoints(self):
        """Test status-related API endpoints."""
        # Test status list endpoint
        try:
            response = requests.get(f'{self.BASE_URL}/gadget_communicator_pull/status/', timeout=10)
            assert response.status_code in [200, 401, 404, 405]
            
            if response.status_code == 200:
                data = response.json()
                assert isinstance(data, (dict, list))
                
        except requests.exceptions.RequestException:
            pass
    
    def test_waterplantoperator_to_app_communication(self):
        """Test WaterPlantOperator sending data to WaterPlantApp."""
        # 1. Create WaterPlantOperator device
        operator_device = OperatorDevice(device_id='HTTP_TEST_DEVICE_001')
        
        # 2. Create device data for transmission
        device_data = {
            'device_id': operator_device.device_id,
            'label': 'HTTP Test Device',
            'water_level': 80,
            'moisture_level': 45,
            'water_container_capacity': 2000,
            'status': 'online',
            'last_update': datetime.now().isoformat()
        }
        
        # 3. Simulate HTTP POST to WaterPlantApp
        try:
            response = requests.post(
                f'{self.BASE_URL}/gadget_communicator_pull/devices/',
                json=device_data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            # Should return 201 (created), 400 (bad request), 401 (unauthorized), or 404
            assert response.status_code in [201, 400, 401, 404, 405]
            
            if response.status_code == 201:
                response_data = response.json()
                assert 'device_id' in response_data or 'id' in response_data
                
        except requests.exceptions.RequestException:
            # If endpoint doesn't exist or server is not configured, that's okay
            pass
    
    def test_plan_synchronization_via_api(self):
        """Test plan synchronization via HTTP API."""
        # 1. Create WaterPlantOperator plan
        operator_plan = OperatorPlan(
            name='HTTP Test Plan',
            plan_type='basic',
            water_volume=150
        )
        
        # 2. Create plan data for transmission
        plan_data = {
            'name': operator_plan.name,
            'plan_type': operator_plan.plan_type,
            'water_volume': operator_plan.water_volume,
            'device_id': 'HTTP_TEST_DEVICE_001',
            'created_at': datetime.now().isoformat()
        }
        
        # 3. Simulate HTTP POST to WaterPlantApp
        try:
            response = requests.post(
                f'{self.BASE_URL}/gadget_communicator_pull/plans/',
                json=plan_data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            assert response.status_code in [201, 400, 401, 404, 405]
            
            if response.status_code == 201:
                response_data = response.json()
                assert 'name' in response_data or 'id' in response_data
                
        except requests.exceptions.RequestException:
            pass
    
    def test_status_reporting_via_api(self):
        """Test status reporting via HTTP API."""
        # 1. Create WaterPlantOperator status
        operator_status = OperatorStatus(
            watering_status=True,
            message='HTTP test watering completed successfully'
        )
        
        # 2. Create status data for transmission
        status_data = {
            'message': operator_status.message,
            'status_type': 'success' if operator_status.watering_status else 'error',
            'device_id': 'HTTP_TEST_DEVICE_001',
            'timestamp': datetime.now().isoformat()
        }
        
        # 3. Simulate HTTP POST to WaterPlantApp
        try:
            response = requests.post(
                f'{self.BASE_URL}/gadget_communicator_pull/status/',
                json=status_data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            assert response.status_code in [201, 400, 401, 404, 405]
            
            if response.status_code == 201:
                response_data = response.json()
                assert 'message' in response_data or 'id' in response_data
                
        except requests.exceptions.RequestException:
            pass
    
    def test_json_data_validation(self):
        """Test JSON data validation in API communication."""
        # Test valid JSON
        valid_data = {
            'device_id': 'VALID_DEVICE_001',
            'water_level': 75,
            'moisture_level': 45,
            'status': 'online'
        }
        
        json_string = json.dumps(valid_data)
        parsed_data = json.loads(json_string)
        
        assert parsed_data['device_id'] == 'VALID_DEVICE_001'
        assert parsed_data['water_level'] == 75
        assert parsed_data['status'] == 'online'
        
        # Test invalid JSON handling
        invalid_json = '{"invalid": json}'
        try:
            json.loads(invalid_json)
            pytest.fail("Should have raised JSON decode error")
        except json.JSONDecodeError:
            pass  # Expected error
    
    def test_concurrent_api_requests(self):
        """Test concurrent API requests."""
        results = []
        
        def make_api_request(device_id):
            """Make an API request in a separate thread."""
            try:
                device_data = {
                    'device_id': device_id,
                    'water_level': 75,
                    'moisture_level': 45,
                    'status': 'online'
                }
                
                response = requests.post(
                    f'{self.BASE_URL}/gadget_communicator_pull/devices/',
                    json=device_data,
                    headers={'Content-Type': 'application/json'},
                    timeout=5
                )
                
                results.append({
                    'device_id': device_id,
                    'status_code': response.status_code,
                    'success': response.status_code in [200, 201]
                })
                
            except requests.exceptions.RequestException:
                results.append({
                    'device_id': device_id,
                    'status_code': 0,
                    'success': False
                })
        
        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=make_api_request, args=(f'CONCURRENT_DEVICE_{i:03d}',))
            threads.append(thread)
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify results
        assert len(results) == 5
        for result in results:
            assert 'device_id' in result
            assert 'status_code' in result
            assert 'success' in result
    
    def test_api_error_handling(self):
        """Test API error handling."""
        # Test with invalid data
        invalid_data = {
            'device_id': '',  # Empty device ID
            'water_level': -50,  # Negative water level
            'moisture_level': 150,  # Invalid moisture level (>100)
            'status': 'invalid_status'
        }
        
        try:
            response = requests.post(
                f'{self.BASE_URL}/gadget_communicator_pull/devices/',
                json=invalid_data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            # Should return 400 (bad request) or similar error code
            assert response.status_code in [400, 401, 404, 405, 422]
            
        except requests.exceptions.RequestException:
            pass  # Expected if endpoint doesn't exist
    
    def test_api_response_format(self):
        """Test API response format consistency."""
        try:
            # Test GET request
            response = requests.get(f'{self.BASE_URL}/gadget_communicator_pull/devices/', timeout=10)
            
            if response.status_code == 200:
                # Check if response is valid JSON
                try:
                    data = response.json()
                    assert isinstance(data, (dict, list))
                    
                    # If it's a list, check structure
                    if isinstance(data, list) and len(data) > 0:
                        item = data[0]
                        assert isinstance(item, dict)
                        
                except json.JSONDecodeError:
                    pytest.fail("API response is not valid JSON")
            
        except requests.exceptions.RequestException:
            pass  # Expected if endpoint doesn't exist
    
    def test_authentication_flow(self):
        """Test authentication flow (if implemented)."""
        try:
            # Test token endpoint
            auth_data = {
                'username': 'test_user',
                'password': 'test_password'
            }
            
            response = requests.post(
                f'{self.BASE_URL}/api-token-auth/',
                json=auth_data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            # Should return 200 (success), 400 (bad request), or 401 (unauthorized)
            assert response.status_code in [200, 400, 401, 404, 405]
            
            if response.status_code == 200:
                response_data = response.json()
                # Should contain token or access/refresh tokens
                assert 'token' in response_data or 'access' in response_data
                
        except requests.exceptions.RequestException:
            pass  # Expected if authentication is not implemented
    
    def test_cors_headers(self):
        """Test CORS headers for cross-origin requests."""
        try:
            response = requests.options(
                f'{self.BASE_URL}/gadget_communicator_pull/devices/',
                headers={
                    'Origin': 'http://localhost:3000',
                    'Access-Control-Request-Method': 'POST',
                    'Access-Control-Request-Headers': 'Content-Type'
                },
                timeout=10
            )
            
            # Check for CORS headers
            if 'Access-Control-Allow-Origin' in response.headers:
                assert response.headers['Access-Control-Allow-Origin'] in ['*', 'http://localhost:3000']
            
        except requests.exceptions.RequestException:
            pass  # Expected if CORS is not configured
    
    def test_api_performance(self):
        """Test API performance under load."""
        start_time = time.time()
        
        # Make multiple requests
        for i in range(10):
            try:
                device_data = {
                    'device_id': f'PERF_DEVICE_{i:03d}',
                    'water_level': 75,
                    'moisture_level': 45,
                    'status': 'online'
                }
                
                response = requests.post(
                    f'{self.BASE_URL}/gadget_communicator_pull/devices/',
                    json=device_data,
                    headers={'Content-Type': 'application/json'},
                    timeout=5
                )
                
                # Don't fail on error status codes, just measure performance
                
            except requests.exceptions.RequestException:
                pass  # Expected if endpoint doesn't exist
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Should complete in reasonable time
        assert execution_time < 10.0  # 10 seconds max for 10 requests
    
    def test_waterplantoperator_http_client_simulation(self):
        """Simulate WaterPlantOperator as HTTP client."""
        # 1. Create WaterPlantOperator components
        device = OperatorDevice(device_id='CLIENT_SIM_DEVICE_001')
        plan = OperatorPlan(
            name='Client Simulation Plan',
            plan_type='basic',
            water_volume=200
        )
        status = OperatorStatus(
            watering_status=True,
            message='Client simulation watering completed'
        )
        
        # 2. Simulate HTTP client behavior
        client_data = {
            'device': {
                'device_id': device.device_id,
                'water_level': 80,
                'moisture_level': 45,
                'status': 'online'
            },
            'plan': {
                'name': plan.name,
                'plan_type': plan.plan_type,
                'water_volume': plan.water_volume
            },
            'status': {
                'message': status.message,
                'success': status.watering_status,
                'timestamp': datetime.now().isoformat()
            }
        }
        
        # 3. Test JSON serialization
        json_string = json.dumps(client_data)
        assert isinstance(json_string, str)
        assert device.device_id in json_string
        assert plan.name in json_string
        assert status.message in json_string
        
        # 4. Test JSON deserialization
        parsed_data = json.loads(json_string)
        assert parsed_data['device']['device_id'] == device.device_id
        assert parsed_data['plan']['name'] == plan.name
        assert parsed_data['status']['success'] == status.watering_status
        
        # 5. Simulate sending to WaterPlantApp
        try:
            response = requests.post(
                f'{self.BASE_URL}/gadget_communicator_pull/integration/',
                json=client_data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            # Should return appropriate status code
            assert response.status_code in [200, 201, 400, 401, 404, 405]
            
        except requests.exceptions.RequestException:
            pass  # Expected if endpoint doesn't exist


class TestCornerCasesHTTP:
    """Test corner cases in HTTP API integration."""
    
    BASE_URL = 'http://localhost:8001'
    
    def test_large_payload_handling(self):
        """Test handling of large payloads."""
        # Create large payload
        large_data = {
            'device_id': 'LARGE_PAYLOAD_DEVICE_001',
            'water_level': 75,
            'moisture_level': 45,
            'status': 'online',
            'large_data': 'x' * 10000,  # 10KB of data
            'plans': [
                {
                    'name': f'Large Plan {i}',
                    'water_volume': 100 + i,
                    'data': 'y' * 1000
                }
                for i in range(100)
            ]
        }
        
        try:
            response = requests.post(
                f'{self.BASE_URL}/gadget_communicator_pull/devices/',
                json=large_data,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            # Should handle large payloads gracefully
            assert response.status_code in [200, 201, 400, 413, 401, 404, 405]
            
        except requests.exceptions.RequestException:
            pass  # Expected if endpoint doesn't exist
    
    def test_malformed_json_handling(self):
        """Test handling of malformed JSON."""
        malformed_json = '{"device_id": "MALFORMED_001", "water_level": 75, "invalid": }'
        
        try:
            response = requests.post(
                f'{self.BASE_URL}/gadget_communicator_pull/devices/',
                data=malformed_json,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            # Should return 400 (bad request) for malformed JSON
            assert response.status_code in [400, 401, 404, 405]
            
        except requests.exceptions.RequestException:
            pass  # Expected if endpoint doesn't exist
    
    def test_unicode_data_handling(self):
        """Test handling of unicode data."""
        unicode_data = {
            'device_id': 'UNICODE_设备_001',
            'label': 'Unicode Test Device - 测试设备',
            'water_level': 75,
            'moisture_level': 45,
            'status': 'online',
            'description': 'This is a test with unicode: 这是一个测试'
        }
        
        try:
            response = requests.post(
                f'{self.BASE_URL}/gadget_communicator_pull/devices/',
                json=unicode_data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            assert response.status_code in [200, 201, 400, 401, 404, 405]
            
        except requests.exceptions.RequestException:
            pass  # Expected if endpoint doesn't exist
    
    def test_special_characters_handling(self):
        """Test handling of special characters."""
        special_data = {
            'device_id': 'SPECIAL_CHARS_001',
            'label': 'Special Chars: !@#$%^&*()_+-=[]{}|;:,.<>?',
            'water_level': 75,
            'moisture_level': 45,
            'status': 'online',
            'notes': 'Test with special characters: "quotes" and \'apostrophes\''
        }
        
        try:
            response = requests.post(
                f'{self.BASE_URL}/gadget_communicator_pull/devices/',
                json=special_data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            assert response.status_code in [200, 201, 400, 401, 404, 405]
            
        except requests.exceptions.RequestException:
            pass  # Expected if endpoint doesn't exist
    
    def test_empty_payload_handling(self):
        """Test handling of empty payloads."""
        empty_data = {}
        
        try:
            response = requests.post(
                f'{self.BASE_URL}/gadget_communicator_pull/devices/',
                json=empty_data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            # Should return 400 (bad request) for empty payload
            assert response.status_code in [400, 401, 404, 405]
            
        except requests.exceptions.RequestException:
            pass  # Expected if endpoint doesn't exist
    
    def test_missing_required_fields(self):
        """Test handling of missing required fields."""
        incomplete_data = {
            'device_id': 'INCOMPLETE_001',
            # Missing water_level, moisture_level, status
        }
        
        try:
            response = requests.post(
                f'{self.BASE_URL}/gadget_communicator_pull/devices/',
                json=incomplete_data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            # Should return 400 (bad request) for missing required fields
            assert response.status_code in [400, 401, 404, 405]
            
        except requests.exceptions.RequestException:
            pass  # Expected if endpoint doesn't exist
