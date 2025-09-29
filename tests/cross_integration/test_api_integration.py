"""
API Integration Tests for WaterPlantApp.

This module tests the API endpoints of WaterPlantApp with expected JSON outcomes,
ensuring proper data structure and response formats.
"""
import pytest
import json
from typing import Dict, Any
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from cross_integration_tests.conftest import CrossIntegrationTestCase


class TestDeviceAPI(CrossIntegrationTestCase):
    """Test device API endpoints with expected JSON outcomes."""
    
    def setUp(self):
        """Set up test data."""
        super().setUp()
        self.api_client = APIClient()
        self.api_client.force_authenticate(user=self.user)
    
    def test_list_devices_api_json_structure(self):
        """Test list devices API returns expected JSON structure."""
        url = reverse('api:device-list')
        response = self.api_client.get(url)
        
        # Assert response structure
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # Expected top-level structure
        expected_keys = ['success', 'count', 'data']
        for key in expected_keys:
            self.assertIn(key, data)
        
        # Assert success response
        self.assertTrue(data['success'])
        self.assertEqual(data['count'], 1)
        self.assertIsInstance(data['data'], list)
        
        # Assert device data structure
        if data['data']:
            device_data = data['data'][0]
            self.assert_device_json_structure(device_data)
            
            # Assert specific values
            self.assertEqual(device_data['device_id'], 'TEST_DEVICE_001')
            self.assertEqual(device_data['label'], 'Test Plant Device')
            self.assertEqual(device_data['water_level'], 75)
            self.assertEqual(device_data['moisture_level'], 45)
            self.assertEqual(device_data['is_connected'], True)
            self.assertEqual(device_data['status'], 'online')
    
    def test_get_device_api_json_structure(self):
        """Test get device API returns expected JSON structure."""
        url = reverse('api:device-detail', kwargs={'pk': self.device.id})
        response = self.api_client.get(url)
        
        # Assert response structure
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # Assert device data structure
        self.assert_device_json_structure(data)
        
        # Assert computed fields
        self.assertIn('water_level_ml', data)
        self.assertIn('is_online', data)
        self.assertIn('needs_water_refill', data)
        self.assertIn('needs_watering', data)
        
        # Assert relationship data
        self.assertIn('basic_plans', data)
        self.assertIn('time_plans', data)
        self.assertIn('moisture_plans', data)
        self.assertIn('recent_statuses', data)
        self.assertIn('water_charts', data)
        
        # Assert data types
        self.assertIsInstance(data['basic_plans'], list)
        self.assertIsInstance(data['time_plans'], list)
        self.assertIsInstance(data['moisture_plans'], list)
        self.assertIsInstance(data['recent_statuses'], list)
        self.assertIsInstance(data['water_charts'], list)
    
    def test_create_device_api_json_structure(self):
        """Test create device API returns expected JSON structure."""
        url = reverse('api:device-list')
        device_data = {
            'device_id': 'TEST_DEVICE_002',
            'label': 'Test Device 2',
            'water_level': 80,
            'moisture_level': 50,
            'water_container_capacity': 1500,
            'is_connected': False,
            'status': 'offline'
        }
        
        response = self.api_client.post(url, device_data, format='json')
        
        # Assert response structure
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.json()
        
        # Assert device data structure
        self.assert_device_json_structure(data)
        
        # Assert created device values
        self.assertEqual(data['device_id'], 'TEST_DEVICE_002')
        self.assertEqual(data['label'], 'Test Device 2')
        self.assertEqual(data['water_level'], 80)
        self.assertEqual(data['moisture_level'], 50)
        self.assertEqual(data['water_container_capacity'], 1500)
        self.assertEqual(data['is_connected'], False)
        self.assertEqual(data['status'], 'offline')
    
    def test_update_device_api_json_structure(self):
        """Test update device API returns expected JSON structure."""
        url = reverse('api:device-detail', kwargs={'pk': self.device.id})
        update_data = {
            'water_level': 90,
            'moisture_level': 60,
            'status': 'maintenance'
        }
        
        response = self.api_client.patch(url, update_data, format='json')
        
        # Assert response structure
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # Assert device data structure
        self.assert_device_json_structure(data)
        
        # Assert updated values
        self.assertEqual(data['water_level'], 90)
        self.assertEqual(data['moisture_level'], 60)
        self.assertEqual(data['status'], 'maintenance')
    
    def test_device_api_error_responses(self):
        """Test device API error responses have expected JSON structure."""
        # Test invalid device ID
        url = reverse('api:device-detail', kwargs={'pk': 99999})
        response = self.api_client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.json()
        
        # Assert error response structure
        self.assertIn('detail', data)
        
        # Test invalid data
        url = reverse('api:device-list')
        invalid_data = {
            'device_id': '',  # Invalid empty ID
            'water_level': 150  # Invalid level > 100
        }
        
        response = self.api_client.post(url, invalid_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        
        # Assert validation error structure
        self.assertIn('device_id', data)
        self.assertIn('water_level', data)


class TestPlanAPI(CrossIntegrationTestCase):
    """Test plan API endpoints with expected JSON outcomes."""
    
    def setUp(self):
        """Set up test data."""
        super().setUp()
        self.api_client = APIClient()
        self.api_client.force_authenticate(user=self.user)
        
        # Create test plans
        self.basic_plan = self.device.device_relation_b.create(
            name='Test Basic Plan',
            plan_type='basic',
            water_volume=150
        )
        
        self.moisture_plan = self.device.device_relation_m.create(
            name='Test Moisture Plan',
            plan_type='moisture',
            water_volume=200,
            moisture_threshold=0.4,
            check_interval=30
        )
        
        self.time_plan = self.device.device_relation_t.create(
            name='Test Time Plan',
            plan_type='time_based',
            water_volume=180,
            execute_only_once=False
        )
    
    def test_list_basic_plans_api_json_structure(self):
        """Test list basic plans API returns expected JSON structure."""
        url = reverse('api:basic-plan-list')
        response = self.api_client.get(url)
        
        # Assert response structure
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # Expected structure for list response
        expected_keys = ['success', 'count', 'data']
        for key in expected_keys:
            self.assertIn(key, data)
        
        # Assert plan data structure
        if data['data']:
            plan_data = data['data'][0]
            self.assert_plan_json_structure(plan_data)
            
            # Assert specific values
            self.assertEqual(plan_data['name'], 'Test Basic Plan')
            self.assertEqual(plan_data['plan_type'], 'basic')
            self.assertEqual(plan_data['water_volume'], 150)
            self.assertEqual(plan_data['has_been_executed'], False)
    
    def test_list_moisture_plans_api_json_structure(self):
        """Test list moisture plans API returns expected JSON structure."""
        url = reverse('api:moisture-plan-list')
        response = self.api_client.get(url)
        
        # Assert response structure
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # Assert plan data structure
        if data['data']:
            plan_data = data['data'][0]
            self.assert_plan_json_structure(plan_data)
            
            # Assert moisture-specific fields
            self.assertIn('moisture_threshold', plan_data)
            self.assertIn('check_interval', plan_data)
            self.assertIn('is_running', plan_data)
            
            # Assert specific values
            self.assertEqual(plan_data['name'], 'Test Moisture Plan')
            self.assertEqual(plan_data['plan_type'], 'moisture')
            self.assertEqual(plan_data['moisture_threshold'], 0.4)
            self.assertEqual(plan_data['check_interval'], 30)
    
    def test_list_time_plans_api_json_structure(self):
        """Test list time plans API returns expected JSON structure."""
        url = reverse('api:time-plan-list')
        response = self.api_client.get(url)
        
        # Assert response structure
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # Assert plan data structure
        if data['data']:
            plan_data = data['data'][0]
            self.assert_plan_json_structure(plan_data)
            
            # Assert time-specific fields
            self.assertIn('execute_only_once', plan_data)
            self.assertIn('is_running', plan_data)
            
            # Assert specific values
            self.assertEqual(plan_data['name'], 'Test Time Plan')
            self.assertEqual(plan_data['plan_type'], 'time_based')
            self.assertEqual(plan_data['execute_only_once'], False)
    
    def test_create_basic_plan_api_json_structure(self):
        """Test create basic plan API returns expected JSON structure."""
        url = reverse('api:basic-plan-list')
        plan_data = {
            'name': 'New Basic Plan',
            'water_volume': 200
        }
        
        response = self.api_client.post(url, plan_data, format='json')
        
        # Assert response structure
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.json()
        
        # Assert plan data structure
        self.assert_plan_json_structure(data)
        
        # Assert created plan values
        self.assertEqual(data['name'], 'New Basic Plan')
        self.assertEqual(data['plan_type'], 'basic')
        self.assertEqual(data['water_volume'], 200)
        self.assertEqual(data['has_been_executed'], False)
    
    def test_create_moisture_plan_api_json_structure(self):
        """Test create moisture plan API returns expected JSON structure."""
        url = reverse('api:moisture-plan-list')
        plan_data = {
            'name': 'New Moisture Plan',
            'water_volume': 250,
            'moisture_threshold': 0.3,
            'check_interval': 45
        }
        
        response = self.api_client.post(url, plan_data, format='json')
        
        # Assert response structure
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.json()
        
        # Assert plan data structure
        self.assert_plan_json_structure(data)
        
        # Assert moisture-specific fields
        self.assertIn('moisture_threshold', data)
        self.assertIn('check_interval', data)
        self.assertIn('is_running', data)
        
        # Assert created plan values
        self.assertEqual(data['name'], 'New Moisture Plan')
        self.assertEqual(data['plan_type'], 'moisture')
        self.assertEqual(data['moisture_threshold'], 0.3)
        self.assertEqual(data['check_interval'], 45)
    
    def test_plan_api_validation_errors(self):
        """Test plan API validation errors have expected JSON structure."""
        url = reverse('api:basic-plan-list')
        invalid_data = {
            'name': '',  # Invalid empty name
            'water_volume': 3000  # Invalid volume > 2000
        }
        
        response = self.api_client.post(url, invalid_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        
        # Assert validation error structure
        self.assertIn('name', data)
        self.assertIn('water_volume', data)


class TestStatusAPI(CrossIntegrationTestCase):
    """Test status API endpoints with expected JSON outcomes."""
    
    def setUp(self):
        """Set up test data."""
        super().setUp()
        self.api_client = APIClient()
        self.api_client.force_authenticate(user=self.user)
        
        # Create test status
        self.status = Status.objects.create(
            execution_status=True,
            message='Test status message',
            status_type='success',
            device_id=self.device.device_id
        )
    
    def test_list_status_api_json_structure(self):
        """Test list status API returns expected JSON structure."""
        url = reverse('api:status-list')
        response = self.api_client.get(url)
        
        # Assert response structure
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # Expected structure for list response
        expected_keys = ['success', 'count', 'data']
        for key in expected_keys:
            self.assertIn(key, data)
        
        # Assert status data structure
        if data['data']:
            status_data = data['data'][0]
            self.assert_status_json_structure(status_data)
            
            # Assert specific values
            self.assertEqual(status_data['execution_status'], True)
            self.assertEqual(status_data['message'], 'Test status message')
            self.assertEqual(status_data['status_type'], 'success')
            self.assertEqual(status_data['device_id'], 'TEST_DEVICE_001')
    
    def test_get_status_api_json_structure(self):
        """Test get status API returns expected JSON structure."""
        url = reverse('api:status-detail', kwargs={'pk': self.status.id})
        response = self.api_client.get(url)
        
        # Assert response structure
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # Assert status data structure
        self.assert_status_json_structure(data)
        
        # Assert computed fields
        self.assertIn('is_success', data)
        self.assertIn('is_failure', data)
        self.assertIn('status_icon', data)
        
        # Assert specific values
        self.assertEqual(data['execution_status'], True)
        self.assertEqual(data['message'], 'Test status message')
        self.assertEqual(data['status_type'], 'success')
        self.assertEqual(data['device_id'], 'TEST_DEVICE_001')
    
    def test_create_status_api_json_structure(self):
        """Test create status API returns expected JSON structure."""
        url = reverse('api:status-list')
        status_data = {
            'execution_status': False,
            'message': 'New status message',
            'status_type': 'warning',
            'device_id': 'TEST_DEVICE_001'
        }
        
        response = self.api_client.post(url, status_data, format='json')
        
        # Assert response structure
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.json()
        
        # Assert status data structure
        self.assert_status_json_structure(data)
        
        # Assert created status values
        self.assertEqual(data['execution_status'], False)
        self.assertEqual(data['message'], 'New status message')
        self.assertEqual(data['status_type'], 'warning')
        self.assertEqual(data['device_id'], 'TEST_DEVICE_001')
    
    def test_status_api_validation_errors(self):
        """Test status API validation errors have expected JSON structure."""
        url = reverse('api:status-list')
        invalid_data = {
            'execution_status': True,
            'message': '',  # Invalid empty message
            'status_type': 'invalid_type'  # Invalid status type
        }
        
        response = self.api_client.post(url, invalid_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        
        # Assert validation error structure
        self.assertIn('message', data)
        self.assertIn('status_type', data)


class TestAPIFilteringAndSearch(CrossIntegrationTestCase):
    """Test API filtering and search functionality with expected JSON outcomes."""
    
    def setUp(self):
        """Set up test data."""
        super().setUp()
        self.api_client = APIClient()
        self.api_client.force_authenticate(user=self.user)
        
        # Create additional test devices
        self.device2 = Device.objects.create(
            device_id='TEST_DEVICE_002',
            label='Test Device 2',
            owner=self.user,
            water_level=50,
            moisture_level=30,
            water_container_capacity=1500,
            is_connected=False,
            status='offline'
        )
        
        self.device3 = Device.objects.create(
            device_id='TEST_DEVICE_003',
            label='Test Device 3',
            owner=self.user,
            water_level=90,
            moisture_level=70,
            water_container_capacity=3000,
            is_connected=True,
            status='online'
        )
    
    def test_device_filtering_by_status(self):
        """Test device filtering by status returns expected JSON structure."""
        url = reverse('api:device-list')
        response = self.api_client.get(url, {'status': 'online'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # Assert response structure
        self.assertIn('success', data)
        self.assertIn('count', data)
        self.assertIn('data', data)
        
        # Assert filtered results
        self.assertEqual(data['count'], 2)  # Two online devices
        for device in data['data']:
            self.assertEqual(device['status'], 'online')
    
    def test_device_filtering_by_water_level(self):
        """Test device filtering by water level returns expected JSON structure."""
        url = reverse('api:device-list')
        response = self.api_client.get(url, {'water_level__gte': 80})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # Assert filtered results
        self.assertEqual(data['count'], 2)  # Two devices with water level >= 80
        for device in data['data']:
            self.assertGreaterEqual(device['water_level'], 80)
    
    def test_device_search_by_label(self):
        """Test device search by label returns expected JSON structure."""
        url = reverse('api:device-list')
        response = self.api_client.get(url, {'search': 'Test Device 2'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # Assert search results
        self.assertEqual(data['count'], 1)
        self.assertEqual(data['data'][0]['label'], 'Test Device 2')
    
    def test_device_ordering(self):
        """Test device ordering returns expected JSON structure."""
        url = reverse('api:device-list')
        response = self.api_client.get(url, {'ordering': 'water_level'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # Assert ordered results
        water_levels = [device['water_level'] for device in data['data']]
        self.assertEqual(water_levels, sorted(water_levels))
    
    def test_device_combined_filters(self):
        """Test device combined filters return expected JSON structure."""
        url = reverse('api:device-list')
        response = self.api_client.get(url, {
            'status': 'online',
            'water_level__gte': 70,
            'ordering': '-water_level'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # Assert combined filter results
        self.assertEqual(data['count'], 2)  # Two online devices with water level >= 70
        for device in data['data']:
            self.assertEqual(device['status'], 'online')
            self.assertGreaterEqual(device['water_level'], 70)
        
        # Assert ordering (descending water level)
        water_levels = [device['water_level'] for device in data['data']]
        self.assertEqual(water_levels, sorted(water_levels, reverse=True))
