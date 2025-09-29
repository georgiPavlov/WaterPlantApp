"""
Unit tests for WaterPlantApp views.

This module contains comprehensive unit tests for all API views
in the WaterPlantApp Django application.
"""
import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from rest_framework import status

from gadget_communicator_pull.models import (
    Device, BasicPlan, MoisturePlan, TimePlan, WaterTime, Status, WaterChart
)


class TestDeviceViews(TestCase):
    """Test cases for device-related views."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.device = Device.objects.create(
            device_id='TEST_DEVICE_001',
            label='Test Device',
            owner=self.user,
            water_level=75,
            moisture_level=45,
            water_container_capacity=2000,
            status='online'
        )
    
    def test_create_device(self):
        """Test device creation via API."""
        url = reverse('create_device')
        data = {
            'device_id': 'TEST_DEVICE_002',
            'label': 'New Test Device',
            'water_level': 80,
            'moisture_level': 50,
            'water_container_capacity': 2500,
            'status': 'online'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Device.objects.count(), 2)
        
        # Verify device was created with correct data
        device = Device.objects.get(device_id='TEST_DEVICE_002')
        self.assertEqual(device.label, 'New Test Device')
        self.assertEqual(device.owner, self.user)
    
    def test_list_devices(self):
        """Test device listing via API."""
        url = reverse('list_devices')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['device_id'], 'TEST_DEVICE_001')
    
    def test_get_device(self):
        """Test device retrieval via API."""
        url = reverse('get_device', kwargs={'device_id': self.device.device_id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['device_id'], 'TEST_DEVICE_001')
        self.assertEqual(response.data['label'], 'Test Device')
    
    def test_update_device(self):
        """Test device update via API."""
        url = reverse('update_device', kwargs={'device_id': self.device.device_id})
        data = {
            'label': 'Updated Test Device',
            'water_level': 90,
            'moisture_level': 60
        }
        
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify device was updated
        self.device.refresh_from_db()
        self.assertEqual(self.device.label, 'Updated Test Device')
        self.assertEqual(self.device.water_level, 90)
    
    def test_delete_device(self):
        """Test device deletion via API."""
        url = reverse('delete_device', kwargs={'device_id': self.device.device_id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Device.objects.count(), 0)
    
    def test_device_water_chart(self):
        """Test device water chart data via API."""
        # Create water chart data
        WaterChart.objects.create(
            device=self.device,
            water_level=80,
            timestamp='2023-01-01T10:00:00Z'
        )
        
        url = reverse('device_water_chart', kwargs={'device_id': self.device.device_id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['water_level'], 80)


class TestPlanViews(TestCase):
    """Test cases for plan-related views."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.device = Device.objects.create(
            device_id='TEST_DEVICE_001',
            label='Test Device',
            owner=self.user,
            water_level=75,
            moisture_level=45,
            water_container_capacity=2000,
            status='online'
        )
    
    def test_create_basic_plan(self):
        """Test basic plan creation via API."""
        url = reverse('create_plan')
        data = {
            'name': 'Test Basic Plan',
            'plan_type': 'basic',
            'water_volume': 150,
            'device': self.device.id
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(BasicPlan.objects.count(), 1)
        
        plan = BasicPlan.objects.first()
        self.assertEqual(plan.name, 'Test Basic Plan')
        self.assertEqual(plan.plan_type, 'basic')
        self.assertEqual(plan.water_volume, 150)
    
    def test_create_moisture_plan(self):
        """Test moisture plan creation via API."""
        url = reverse('create_plan')
        data = {
            'name': 'Test Moisture Plan',
            'plan_type': 'moisture',
            'water_volume': 200,
            'moisture_threshold': 0.4,
            'check_interval': 30,
            'device': self.device.id
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(MoisturePlan.objects.count(), 1)
        
        plan = MoisturePlan.objects.first()
        self.assertEqual(plan.name, 'Test Moisture Plan')
        self.assertEqual(plan.moisture_threshold, 0.4)
        self.assertEqual(plan.check_interval, 30)
    
    def test_create_time_plan(self):
        """Test time plan creation via API."""
        url = reverse('create_plan')
        data = {
            'name': 'Test Time Plan',
            'plan_type': 'time_based',
            'water_volume': 180,
            'execute_only_once': False,
            'device': self.device.id
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(TimePlan.objects.count(), 1)
        
        plan = TimePlan.objects.first()
        self.assertEqual(plan.name, 'Test Time Plan')
        self.assertEqual(plan.execute_only_once, False)
    
    def test_list_plans(self):
        """Test plan listing via API."""
        # Create test plans
        BasicPlan.objects.create(
            name='Test Plan 1',
            plan_type='basic',
            water_volume=150,
            device=self.device
        )
        MoisturePlan.objects.create(
            name='Test Plan 2',
            plan_type='moisture',
            water_volume=200,
            moisture_threshold=0.4,
            check_interval=30,
            device=self.device
        )
        
        url = reverse('list_plans')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_get_plans_by_device(self):
        """Test getting plans by device via API."""
        # Create test plan
        BasicPlan.objects.create(
            name='Test Plan',
            plan_type='basic',
            water_volume=150,
            device=self.device
        )
        
        url = reverse('get_plans_by_device', kwargs={'device_id': self.device.device_id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Test Plan')
    
    def test_update_plan(self):
        """Test plan update via API."""
        plan = BasicPlan.objects.create(
            name='Test Plan',
            plan_type='basic',
            water_volume=150,
            device=self.device
        )
        
        url = reverse('update_plan', kwargs={'plan_id': plan.id})
        data = {
            'name': 'Updated Test Plan',
            'water_volume': 200
        }
        
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        plan.refresh_from_db()
        self.assertEqual(plan.name, 'Updated Test Plan')
        self.assertEqual(plan.water_volume, 200)
    
    def test_delete_plan(self):
        """Test plan deletion via API."""
        plan = BasicPlan.objects.create(
            name='Test Plan',
            plan_type='basic',
            water_volume=150,
            device=self.device
        )
        
        url = reverse('delete_plan', kwargs={'plan_id': plan.id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(BasicPlan.objects.count(), 0)


class TestStatusViews(TestCase):
    """Test cases for status-related views."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.device = Device.objects.create(
            device_id='TEST_DEVICE_001',
            label='Test Device',
            owner=self.user,
            water_level=75,
            moisture_level=45,
            water_container_capacity=2000,
            status='online'
        )
    
    def test_create_status(self):
        """Test status creation via API."""
        url = reverse('create_status')
        data = {
            'message': 'Test status message',
            'status_type': 'success',
            'device': self.device.id
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Status.objects.count(), 1)
        
        status_obj = Status.objects.first()
        self.assertEqual(status_obj.message, 'Test status message')
        self.assertEqual(status_obj.status_type, 'success')
    
    def test_list_status(self):
        """Test status listing via API."""
        # Create test statuses
        Status.objects.create(
            message='Status 1',
            status_type='success',
            device=self.device
        )
        Status.objects.create(
            message='Status 2',
            status_type='error',
            device=self.device
        )
        
        url = reverse('list_status')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_get_status(self):
        """Test status retrieval via API."""
        status_obj = Status.objects.create(
            message='Test status',
            status_type='success',
            device=self.device
        )
        
        url = reverse('get_status', kwargs={'status_id': status_obj.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Test status')
    
    def test_delete_status(self):
        """Test status deletion via API."""
        status_obj = Status.objects.create(
            message='Test status',
            status_type='success',
            device=self.device
        )
        
        url = reverse('delete_status', kwargs={'status_id': status_obj.id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Status.objects.count(), 0)


class TestCameraViews(TestCase):
    """Test cases for camera-related views."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.device = Device.objects.create(
            device_id='TEST_DEVICE_001',
            label='Test Device',
            owner=self.user,
            water_level=75,
            moisture_level=45,
            water_container_capacity=2000,
            status='online'
        )
    
    @patch('gadget_communicator_pull.views.api.camera.take_photo_async.camera_operations')
    def test_take_photo_async(self, mock_camera_ops):
        """Test async photo capture via API."""
        mock_camera_ops.take_photo.return_value = True
        
        url = reverse('take_photo_async')
        data = {
            'device_id': self.device.device_id,
            'photo_name': 'test_photo'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertTrue(response.data['success'])
    
    def test_list_photos(self):
        """Test photo listing via API."""
        url = reverse('list_photos')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
    
    def test_get_photo_status(self):
        """Test photo status retrieval via API."""
        url = reverse('get_photo_status', kwargs={'photo_name': 'test_photo'})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('status', response.data)
    
    def test_download_photo(self):
        """Test photo download via API."""
        url = reverse('download_photo', kwargs={'photo_name': 'test_photo'})
        response = self.client.get(url)
        
        # Should return 404 if photo doesn't exist
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_delete_photo(self):
        """Test photo deletion via API."""
        url = reverse('delete_photo', kwargs={'photo_name': 'test_photo'})
        response = self.client.delete(url)
        
        # Should return 404 if photo doesn't exist
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class TestAuthenticationViews(TestCase):
    """Test cases for authentication-related views."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_unauthenticated_access(self):
        """Test that unauthenticated users cannot access protected endpoints."""
        url = reverse('list_devices')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_authenticated_access(self):
        """Test that authenticated users can access protected endpoints."""
        self.client.force_authenticate(user=self.user)
        
        url = reverse('list_devices')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_user_owns_device(self):
        """Test that users can only access their own devices."""
        # Create device for another user
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123'
        )
        other_device = Device.objects.create(
            device_id='OTHER_DEVICE_001',
            label='Other Device',
            owner=other_user,
            water_level=75,
            moisture_level=45,
            water_container_capacity=2000,
            status='online'
        )
        
        # Authenticate as testuser
        self.client.force_authenticate(user=self.user)
        
        # Try to access other user's device
        url = reverse('get_device', kwargs={'device_id': other_device.device_id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class TestErrorHandling(TestCase):
    """Test cases for error handling in views."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_invalid_device_id(self):
        """Test handling of invalid device ID."""
        url = reverse('get_device', kwargs={'device_id': 'INVALID_DEVICE'})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_invalid_plan_id(self):
        """Test handling of invalid plan ID."""
        url = reverse('update_plan', kwargs={'plan_id': 99999})
        data = {'name': 'Updated Plan'}
        response = self.client.put(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_invalid_status_id(self):
        """Test handling of invalid status ID."""
        url = reverse('get_status', kwargs={'status_id': 99999})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_malformed_json(self):
        """Test handling of malformed JSON data."""
        url = reverse('create_device')
        response = self.client.post(
            url, 
            'invalid json data', 
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_missing_required_fields(self):
        """Test handling of missing required fields."""
        url = reverse('create_device')
        data = {
            'label': 'Test Device'
            # Missing required fields like device_id, water_level, etc.
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
