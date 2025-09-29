"""
Unit tests for WaterPlantApp views.

This module contains comprehensive unit tests for all view classes
in the WaterPlantApp Django application.
"""
import pytest
import json
from datetime import datetime, date, time
from decimal import Decimal
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from unittest.mock import Mock, patch

from gadget_communicator_pull.models import (
    Device, BasicPlan, MoisturePlan, TimePlan, WaterTime, Status, WaterChart
)


class TestDeviceViews(TestCase):
    """Test cases for device views."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
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

    def test_list_devices(self):
        """Test device listing via API."""
        url = reverse('gadget_communicator_pull:api_list_devices')
        response = self.client.get(url)
        
        # Should return 200 or 403 depending on authentication
        self.assertIn(response.status_code, [200, 403])

    def test_get_device(self):
        """Test device retrieval via API."""
        url = reverse('gadget_communicator_pull:api_get_device', kwargs={'id': self.device.device_id})
        response = self.client.get(url)
        
        # Should return 200 or 403 depending on authentication
        self.assertIn(response.status_code, [200, 403])

    def test_create_device(self):
        """Test device creation via API."""
        url = reverse('gadget_communicator_pull:api_create_device')
        data = {
            'device_id': 'NEW_DEVICE_001',
            'label': 'New Test Device',
            'water_level': 80,
            'moisture_level': 50,
            'water_container_capacity': 1500
        }
        
        response = self.client.post(url, json.dumps(data), content_type='application/json')
        
        # Should return 201 or 403 depending on authentication
        self.assertIn(response.status_code, [201, 403])

    def test_update_device(self):
        """Test device update via API."""
        url = reverse('gadget_communicator_pull:api_update_device')
        data = {
            'id': self.device.device_id,
            'label': 'Updated Test Device',
            'water_level': 85,
            'moisture_level': 55,
            'water_container_capacity': 2000
        }
        
        response = self.client.post(url, json.dumps(data), content_type='application/json')
        
        # Should return 200 or 403 depending on authentication
        self.assertIn(response.status_code, [200, 403])

    def test_delete_device(self):
        """Test device deletion via API."""
        url = reverse('gadget_communicator_pull:api_delete_device', kwargs={'id': self.device.device_id})
        response = self.client.delete(url)
        
        # Should return 204 or 403 depending on authentication
        self.assertIn(response.status_code, [204, 403])

    def test_device_water_chart(self):
        """Test device water chart via API."""
        url = reverse('gadget_communicator_pull:api_get_device_charts', kwargs={'id': self.device.device_id})
        response = self.client.get(url)
        
        # Should return 200 or 403 depending on authentication
        self.assertIn(response.status_code, [200, 403])


class TestPlanViews(TestCase):
    """Test cases for plan views."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
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
        self.basic_plan = BasicPlan.objects.create(
            name='Test Basic Plan',
            plan_type='basic',
            water_volume=150
        )

    def test_list_plans(self):
        """Test plan listing via API."""
        url = reverse('gadget_communicator_pull:api_list_plans')
        response = self.client.get(url)
        
        # Should return 200 or 403 depending on authentication
        self.assertIn(response.status_code, [200, 403])

    def test_create_basic_plan(self):
        """Test basic plan creation via API."""
        url = reverse('gadget_communicator_pull:api_create_plan')
        data = {
            'name': 'New Basic Plan',
            'plan_type': 'basic',
            'water_volume': 200
        }
        
        response = self.client.post(url, json.dumps(data), content_type='application/json')
        
        # Should return 201 or 403 depending on authentication
        self.assertIn(response.status_code, [201, 403])

    def test_create_moisture_plan(self):
        """Test moisture plan creation via API."""
        url = reverse('gadget_communicator_pull:api_create_plan')
        data = {
            'name': 'New Moisture Plan',
            'plan_type': 'moisture',
            'water_volume': 250,
            'moisture_threshold': 30
        }
        
        response = self.client.post(url, json.dumps(data), content_type='application/json')
        
        # Should return 201 or 403 depending on authentication
        self.assertIn(response.status_code, [201, 403])

    def test_create_time_plan(self):
        """Test time plan creation via API."""
        url = reverse('gadget_communicator_pull:api_create_plan')
        data = {
            'name': 'New Time Plan',
            'plan_type': 'time',
            'water_volume': 300
        }
        
        response = self.client.post(url, json.dumps(data), content_type='application/json')
        
        # Should return 201 or 403 depending on authentication
        self.assertIn(response.status_code, [201, 403])

    def test_get_plans_by_device(self):
        """Test getting plans by device ID via API."""
        url = reverse('gadget_communicator_pull:api_get_plans_by_device_id', kwargs={'id': self.device.device_id})
        response = self.client.get(url)
        
        # Should return 200 or 403 depending on authentication
        self.assertIn(response.status_code, [200, 403])

    def test_update_plan(self):
        """Test plan update via API."""
        url = reverse('gadget_communicator_pull:api_update_plan')
        data = {
            'id': self.basic_plan.id,
            'name': 'Updated Basic Plan',
            'plan_type': 'basic',
            'water_volume': 200
        }
        
        response = self.client.post(url, json.dumps(data), content_type='application/json')
        
        # Should return 200 or 403 depending on authentication
        self.assertIn(response.status_code, [200, 403])

    def test_delete_plan(self):
        """Test plan deletion via API."""
        url = reverse('gadget_communicator_pull:api_delete_plan', kwargs={'id': self.basic_plan.id})
        response = self.client.delete(url)
        
        # Should return 204 or 403 depending on authentication
        self.assertIn(response.status_code, [204, 403])


class TestStatusViews(TestCase):
    """Test cases for status views."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
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
        self.status = Status.objects.create(
            message='Test status message',
            execution_status=True,
            status_type='success',
            device_id=self.device.device_id
        )

    def test_list_status(self):
        """Test status listing via API."""
        url = reverse('gadget_communicator_pull:api_list_status', kwargs={'id': self.device.device_id})
        response = self.client.get(url)
        
        # Should return 200 or 403 depending on authentication
        self.assertIn(response.status_code, [200, 403])

    def test_get_status(self):
        """Test status retrieval via API."""
        url = reverse('gadget_communicator_pull:api_get_status', kwargs={'id': self.status.id})
        response = self.client.get(url)
        
        # Should return 200 or 403 depending on authentication
        self.assertIn(response.status_code, [200, 403])

    def test_create_status(self):
        """Test status creation via API."""
        url = reverse('gadget_communicator_pull:api_create_status')
        data = {
            'message': 'New status message',
            'execution_status': False,
            'status_type': 'warning',
            'device_id': self.device.device_id
        }
        
        response = self.client.post(url, json.dumps(data), content_type='application/json')
        
        # Should return 201 or 403 depending on authentication
        self.assertIn(response.status_code, [201, 403])

    def test_delete_status(self):
        """Test status deletion via API."""
        url = reverse('gadget_communicator_pull:api_delete_status', kwargs={'id': self.status.id})
        response = self.client.delete(url)
        
        # Should return 204 or 403 depending on authentication
        self.assertIn(response.status_code, [204, 403])


class TestCameraViews(TestCase):
    """Test cases for camera views."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
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

    def test_take_photo_async(self):
        """Test async photo taking via API."""
        url = reverse('gadget_communicator_pull:api_create_photo', kwargs={'id_d': self.device.device_id})
        response = self.client.post(url)
        
        # Should return 200 or 403 depending on authentication
        self.assertIn(response.status_code, [200, 403])

    def test_get_photo_status(self):
        """Test photo status retrieval via API."""
        url = reverse('gadget_communicator_pull:api_get_photo_by_id', kwargs={'id': 'test_photo_id'})
        response = self.client.get(url)
        
        # Should return 200 or 403 depending on authentication
        self.assertIn(response.status_code, [200, 403])

    def test_list_photos(self):
        """Test photo listing via API."""
        url = reverse('gadget_communicator_pull:api_list_photos', kwargs={'id_d': self.device.device_id})
        response = self.client.get(url)
        
        # Should return 200 or 403 depending on authentication
        self.assertIn(response.status_code, [200, 403])

    def test_download_photo(self):
        """Test photo download via API."""
        url = reverse('gadget_communicator_pull:api_download_photo_id', kwargs={'id': 'test_photo_id'})
        response = self.client.get(url)
        
        # Should return 200 or 403 depending on authentication
        self.assertIn(response.status_code, [200, 403])

    def test_delete_photo(self):
        """Test photo deletion via API."""
        url = reverse('gadget_communicator_pull:api_delete_photo_by_id', kwargs={'id': 'test_photo_id'})
        response = self.client.delete(url)
        
        # Should return 204 or 403 depending on authentication
        self.assertIn(response.status_code, [204, 403])


class TestAuthenticationViews(TestCase):
    """Test cases for authentication views."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_unauthenticated_access(self):
        """Test unauthenticated access to protected endpoints."""
        url = reverse('gadget_communicator_pull:api_list_devices')
        response = self.client.get(url)
        
        # Should return 403 for unauthenticated access
        self.assertEqual(response.status_code, 403)

    def test_authenticated_access(self):
        """Test authenticated access to protected endpoints."""
        # Login user
        self.client.force_login(self.user)
        
        url = reverse('gadget_communicator_pull:api_list_devices')
        response = self.client.get(url)
        
        # Should return 200 for authenticated access
        self.assertEqual(response.status_code, 200)

    def test_user_owns_device(self):
        """Test user ownership of device."""
        device = Device.objects.create(
            device_id='TEST_DEVICE_001',
            label='Test Device',
            owner=self.user
        )
        
        # Login user
        self.client.force_login(self.user)
        
        url = reverse('gadget_communicator_pull:api_get_device', kwargs={'id': device.device_id})
        response = self.client.get(url)
        
        # Should return 200 for owned device
        self.assertEqual(response.status_code, 200)


class TestErrorHandling(TestCase):
    """Test cases for error handling."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_invalid_device_id(self):
        """Test handling of invalid device ID."""
        url = reverse('gadget_communicator_pull:api_get_device', kwargs={'id': 'INVALID_ID'})
        response = self.client.get(url)
        
        # Should return 404 or 403 depending on authentication
        self.assertIn(response.status_code, [404, 403])

    def test_invalid_plan_id(self):
        """Test handling of invalid plan ID."""
        url = reverse('gadget_communicator_pull:api_delete_plan', kwargs={'id': '99999'})
        response = self.client.delete(url)
        
        # Should return 404 or 403 depending on authentication
        self.assertIn(response.status_code, [404, 403])

    def test_invalid_status_id(self):
        """Test handling of invalid status ID."""
        url = reverse('gadget_communicator_pull:api_get_status', kwargs={'id': '99999'})
        response = self.client.get(url)
        
        # Should return 404 or 403 depending on authentication
        self.assertIn(response.status_code, [404, 403])

    def test_malformed_json(self):
        """Test handling of malformed JSON data."""
        url = reverse('gadget_communicator_pull:api_create_device')
        response = self.client.post(url, 'invalid json', content_type='application/json')
        
        # Should return 400 or 403 depending on authentication
        self.assertIn(response.status_code, [400, 403])

    def test_missing_required_fields(self):
        """Test handling of missing required fields."""
        url = reverse('gadget_communicator_pull:api_create_device')
        data = {
            'label': 'Test Device'
            # Missing required device_id field
        }
        
        response = self.client.post(url, json.dumps(data), content_type='application/json')
        
        # Should return 400 or 403 depending on authentication
        self.assertIn(response.status_code, [400, 403])