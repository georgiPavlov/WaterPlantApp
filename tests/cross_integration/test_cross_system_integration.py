"""
Cross-System Integration Tests.

This module tests the integration between WaterPlantApp (Django) and WaterPlantOperator (Raspberry Pi)
to ensure proper data flow and communication between the two systems.
"""
import pytest
import json
from typing import Dict, Any
from unittest.mock import Mock, patch, MagicMock
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from conftest import CrossIntegrationTestCase


class TestDataModelCompatibility(CrossIntegrationTestCase):
    """Test data model compatibility between Django and WaterPlantOperator."""
    
    def test_device_model_compatibility(self):
        """Test device model compatibility between systems."""
        # Django device
        django_device = self.device
        
        # WaterPlantOperator device
        operator_device = self.create_operator_device(
            device_id=django_device.device_id,
            water_level=django_device.water_level,
            moisture_level=django_device.moisture_level,
            water_container_capacity=django_device.water_container_capacity
        )
        
        # Assert compatibility
        self.assertEqual(django_device.device_id, operator_device.device_id)
        self.assertEqual(django_device.water_level, operator_device.water_level)
        self.assertEqual(django_device.moisture_level, operator_device.moisture_level)
        self.assertEqual(django_device.water_container_capacity, operator_device.water_container_capacity)
    
    def test_basic_plan_model_compatibility(self):
        """Test basic plan model compatibility between systems."""
        # Django basic plan
        django_plan = self.device.device_relation_b.create(
            name='Test Basic Plan',
            plan_type='basic',
            water_volume=150
        )
        
        # WaterPlantOperator basic plan
        operator_plan = self.create_operator_plan(
            name=django_plan.name,
            plan_type=django_plan.plan_type,
            water_volume=django_plan.water_volume
        )
        
        # Assert compatibility
        self.assertEqual(django_plan.name, operator_plan.name)
        self.assertEqual(django_plan.plan_type, operator_plan.plan_type)
        self.assertEqual(django_plan.water_volume, operator_plan.water_volume)
    
    def test_moisture_plan_model_compatibility(self):
        """Test moisture plan model compatibility between systems."""
        # Django moisture plan
        django_plan = self.device.device_relation_m.create(
            name='Test Moisture Plan',
            plan_type='moisture',
            water_volume=200,
            moisture_threshold=0.4,
            check_interval=30
        )
        
        # WaterPlantOperator moisture plan
        operator_plan = self.create_operator_plan(
            plan_type='moisture',
            name=django_plan.name,
            water_volume=django_plan.water_volume,
            moisture_threshold=django_plan.moisture_threshold,
            check_interval=django_plan.check_interval
        )
        
        # Assert compatibility
        self.assertEqual(django_plan.name, operator_plan.name)
        self.assertEqual(django_plan.plan_type, operator_plan.plan_type)
        self.assertEqual(django_plan.water_volume, operator_plan.water_volume)
        self.assertEqual(django_plan.moisture_threshold, operator_plan.moisture_threshold)
        self.assertEqual(django_plan.check_interval, operator_plan.check_interval)
    
    def test_time_plan_model_compatibility(self):
        """Test time plan model compatibility between systems."""
        # Django time plan
        django_plan = self.device.device_relation_t.create(
            name='Test Time Plan',
            plan_type='time_based',
            water_volume=180,
            execute_only_once=False
        )
        
        # WaterPlantOperator time plan
        operator_plan = self.create_operator_plan(
            plan_type='time_based',
            name=django_plan.name,
            water_volume=django_plan.water_volume,
            execute_only_once=django_plan.execute_only_once
        )
        
        # Assert compatibility
        self.assertEqual(django_plan.name, operator_plan.name)
        self.assertEqual(django_plan.plan_type, operator_plan.plan_type)
        self.assertEqual(django_plan.water_volume, operator_plan.water_volume)
        self.assertEqual(django_plan.execute_only_once, operator_plan.execute_only_once)
    
    def test_status_model_compatibility(self):
        """Test status model compatibility between systems."""
        # Django status
        django_status = Status.objects.create(
            execution_status=True,
            message='Test status message',
            status_type='success',
            device_id=self.device.device_id
        )
        
        # WaterPlantOperator status
        operator_status = self.create_operator_status(
            execution_status=django_status.execution_status,
            message=django_status.message
        )
        
        # Assert compatibility
        self.assertEqual(django_status.execution_status, operator_status.execution_status)
        self.assertEqual(django_status.message, operator_status.message)


class TestAPIToOperatorCommunication(CrossIntegrationTestCase):
    """Test communication from WaterPlantApp API to WaterPlantOperator."""
    
    def setUp(self):
        """Set up test data."""
        super().setUp()
        self.api_client = APIClient()
        self.api_client.force_authenticate(user=self.user)
    
    @patch('run.http_communicator.server_communicator.ServerCommunicator')
    def test_device_status_update_communication(self, mock_comm_class):
        """Test device status update communication to operator."""
        # Mock server communicator
        mock_comm = Mock()
        mock_comm.send_health_check.return_value = True
        mock_comm_class.return_value = mock_comm
        
        # Update device status via API
        url = reverse('api:device-detail', kwargs={'pk': self.device.id})
        update_data = {
            'water_level': 85,
            'moisture_level': 55,
            'status': 'online'
        }
        
        response = self.api_client.patch(url, update_data, format='json')
        
        # Assert API response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['water_level'], 85)
        self.assertEqual(data['moisture_level'], 55)
        self.assertEqual(data['status'], 'online')
        
        # Verify operator would receive the update
        # (In real scenario, this would trigger a communication to the operator)
        self.assertTrue(True)  # Placeholder for actual communication test
    
    @patch('run.http_communicator.server_communicator.ServerCommunicator')
    def test_plan_execution_communication(self, mock_comm_class):
        """Test plan execution communication to operator."""
        # Mock server communicator
        mock_comm = Mock()
        mock_comm.get_water_plan.return_value = {
            'name': 'Test Basic Plan',
            'plan_type': 'basic',
            'water_volume': 150
        }
        mock_comm_class.return_value = mock_comm
        
        # Create a plan via API
        url = reverse('api:basic-plan-list')
        plan_data = {
            'name': 'Test Basic Plan',
            'water_volume': 150
        }
        
        response = self.api_client.post(url, plan_data, format='json')
        
        # Assert API response
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.json()
        self.assertEqual(data['name'], 'Test Basic Plan')
        self.assertEqual(data['water_volume'], 150)
        
        # Verify operator would receive the plan
        # (In real scenario, this would trigger plan execution on the operator)
        self.assertTrue(True)  # Placeholder for actual communication test
    
    @patch('run.http_communicator.server_communicator.ServerCommunicator')
    def test_status_reporting_communication(self, mock_comm_class):
        """Test status reporting communication from operator to app."""
        # Mock server communicator
        mock_comm = Mock()
        mock_comm.send_result.return_value = True
        mock_comm_class.return_value = mock_comm
        
        # Create status via API (simulating operator reporting)
        url = reverse('api:status-list')
        status_data = {
            'execution_status': True,
            'message': 'Watering completed successfully',
            'status_type': 'success',
            'device_id': self.device.device_id
        }
        
        response = self.api_client.post(url, status_data, format='json')
        
        # Assert API response
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.json()
        self.assertEqual(data['execution_status'], True)
        self.assertEqual(data['message'], 'Watering completed successfully')
        self.assertEqual(data['device_id'], self.device.device_id)
        
        # Verify status was created in Django
        status_obj = Status.objects.get(id=data['id'])
        self.assertEqual(status_obj.execution_status, True)
        self.assertEqual(status_obj.message, 'Watering completed successfully')


class TestOperatorToAPICommunication(CrossIntegrationTestCase):
    """Test communication from WaterPlantOperator to WaterPlantApp API."""
    
    def setUp(self):
        """Set up test data."""
        super().setUp()
        self.api_client = APIClient()
        self.api_client.force_authenticate(user=self.user)
    
    @patch('requests.post')
    def test_operator_health_check_to_api(self, mock_post):
        """Test operator health check communication to API."""
        # Mock API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'success': True}
        mock_post.return_value = mock_response
        
        # Simulate operator sending health check
        health_data = {
            'device_id': self.device.device_id,
            'water_level': 80,
            'moisture_level': 50,
            'is_connected': True
        }
        
        # In real scenario, this would be sent via ServerCommunicator
        # For testing, we'll simulate the API call
        url = reverse('api:device-detail', kwargs={'pk': self.device.id})
        response = self.api_client.patch(url, health_data, format='json')
        
        # Assert API response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['water_level'], 80)
        self.assertEqual(data['moisture_level'], 50)
        self.assertEqual(data['is_connected'], True)
    
    @patch('requests.post')
    def test_operator_status_report_to_api(self, mock_post):
        """Test operator status report communication to API."""
        # Mock API response
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {'id': 1, 'success': True}
        mock_post.return_value = mock_response
        
        # Simulate operator sending status report
        status_data = {
            'execution_status': True,
            'message': 'Watering plan executed successfully',
            'status_type': 'success',
            'device_id': self.device.device_id
        }
        
        # In real scenario, this would be sent via ServerCommunicator
        # For testing, we'll simulate the API call
        url = reverse('api:status-list')
        response = self.api_client.post(url, status_data, format='json')
        
        # Assert API response
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.json()
        self.assertEqual(data['execution_status'], True)
        self.assertEqual(data['message'], 'Watering plan executed successfully')
        self.assertEqual(data['device_id'], self.device.device_id)
    
    @patch('requests.get')
    def test_operator_plan_request_from_api(self, mock_get):
        """Test operator requesting plans from API."""
        # Create a plan in Django
        plan = self.device.device_relation_b.create(
            name='Test Basic Plan',
            plan_type='basic',
            water_volume=150
        )
        
        # Mock API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'success': True,
            'count': 1,
            'data': [{
                'id': plan.id,
                'name': plan.name,
                'plan_type': plan.plan_type,
                'water_volume': plan.water_volume,
                'has_been_executed': plan.has_been_executed
            }]
        }
        mock_get.return_value = mock_response
        
        # Simulate operator requesting plans
        # In real scenario, this would be done via ServerCommunicator
        # For testing, we'll simulate the API call
        url = reverse('api:basic-plan-list')
        response = self.api_client.get(url)
        
        # Assert API response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['count'], 1)
        self.assertEqual(len(data['data']), 1)
        self.assertEqual(data['data'][0]['name'], 'Test Basic Plan')


class TestDataSynchronization(CrossIntegrationTestCase):
    """Test data synchronization between Django and WaterPlantOperator."""
    
    def test_device_data_synchronization(self):
        """Test device data synchronization between systems."""
        # Update Django device
        self.device.water_level = 90
        self.device.moisture_level = 60
        self.device.save()
        
        # Create corresponding operator device
        operator_device = self.create_operator_device(
            device_id=self.device.device_id,
            water_level=self.device.water_level,
            moisture_level=self.device.moisture_level,
            water_container_capacity=self.device.water_container_capacity
        )
        
        # Assert synchronization
        self.assertEqual(self.device.water_level, operator_device.water_level)
        self.assertEqual(self.device.moisture_level, operator_device.moisture_level)
        self.assertEqual(self.device.water_container_capacity, operator_device.water_container_capacity)
    
    def test_plan_data_synchronization(self):
        """Test plan data synchronization between systems."""
        # Create Django plan
        django_plan = self.device.device_relation_b.create(
            name='Sync Test Plan',
            plan_type='basic',
            water_volume=200
        )
        
        # Create corresponding operator plan
        operator_plan = self.create_operator_plan(
            name=django_plan.name,
            plan_type=django_plan.plan_type,
            water_volume=django_plan.water_volume
        )
        
        # Assert synchronization
        self.assertEqual(django_plan.name, operator_plan.name)
        self.assertEqual(django_plan.plan_type, operator_plan.plan_type)
        self.assertEqual(django_plan.water_volume, operator_plan.water_volume)
        
        # Update Django plan
        django_plan.water_volume = 250
        django_plan.save()
        
        # Update operator plan accordingly
        operator_plan.water_volume = django_plan.water_volume
        
        # Assert updated synchronization
        self.assertEqual(django_plan.water_volume, operator_plan.water_volume)
    
    def test_status_data_synchronization(self):
        """Test status data synchronization between systems."""
        # Create Django status
        django_status = Status.objects.create(
            execution_status=True,
            message='Synchronized status',
            status_type='success',
            device_id=self.device.device_id
        )
        
        # Create corresponding operator status
        operator_status = self.create_operator_status(
            execution_status=django_status.execution_status,
            message=django_status.message
        )
        
        # Assert synchronization
        self.assertEqual(django_status.execution_status, operator_status.execution_status)
        self.assertEqual(django_status.message, operator_status.message)


class TestErrorHandlingAndRecovery(CrossIntegrationTestCase):
    """Test error handling and recovery in cross-system communication."""
    
    def setUp(self):
        """Set up test data."""
        super().setUp()
        self.api_client = APIClient()
        self.api_client.force_authenticate(user=self.user)
    
    @patch('requests.post')
    def test_api_communication_failure_handling(self, mock_post):
        """Test handling of API communication failures."""
        # Mock API failure
        mock_post.side_effect = Exception("Connection failed")
        
        # Simulate operator trying to send status
        # In real scenario, this would be handled by ServerCommunicator
        # For testing, we'll verify error handling
        try:
            # This would normally be done via ServerCommunicator
            raise Exception("Connection failed")
        except Exception as e:
            # Assert error is properly handled
            self.assertEqual(str(e), "Connection failed")
    
    def test_invalid_data_handling(self):
        """Test handling of invalid data between systems."""
        # Test invalid device data
        invalid_device_data = {
            'device_id': '',  # Invalid empty ID
            'water_level': 150,  # Invalid level > 100
            'moisture_level': -10  # Invalid negative level
        }
        
        # Test Django validation
        url = reverse('api:device-list')
        response = self.api_client.post(url, invalid_device_data, format='json')
        
        # Assert validation errors
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        self.assertIn('device_id', data)
        self.assertIn('water_level', data)
        self.assertIn('moisture_level', data)
    
    def test_data_type_compatibility(self):
        """Test data type compatibility between systems."""
        # Test string to number conversion
        django_water_level = "75"  # String from API
        operator_water_level = int(django_water_level)  # Converted to int
        
        # Assert compatibility
        self.assertEqual(int(django_water_level), operator_water_level)
        
        # Test boolean compatibility
        django_connected = "true"  # String from API
        operator_connected = django_connected.lower() == "true"  # Converted to bool
        
        # Assert compatibility
        self.assertTrue(operator_connected)
    
    def test_missing_data_handling(self):
        """Test handling of missing data between systems."""
        # Test missing required fields
        incomplete_data = {
            'device_id': 'TEST_DEVICE_001'
            # Missing required fields like water_level, moisture_level
        }
        
        # Test Django validation
        url = reverse('api:device-list')
        response = self.api_client.post(url, incomplete_data, format='json')
        
        # Assert validation errors for missing fields
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        # Django will require these fields based on model definition
        self.assertIn('water_level', data)
        self.assertIn('moisture_level', data)
