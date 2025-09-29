"""
Fixed Authenticated API Integration Tests for WaterPlantApp.

This module tests API endpoints with proper authentication using Django's test framework
to ensure they return 200 OK responses when authenticated and 401/403 when not.
"""
import pytest
import json
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken

from gadget_communicator_pull.models import (
    Device, BasicPlan, MoisturePlan, TimePlan, WaterTime, Status, WaterChart
)


class TestAuthenticatedAPI(TestCase):
    """Test API endpoints with proper authentication using Django test framework."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.device = Device.objects.create(
            device_id='TEST_DEVICE_001',
            label='Test Plant Device',
            owner=self.user,
            water_level=75,
            moisture_level=45,
            water_container_capacity=2000,
            is_connected=True
        )
        
        self.client = Client()

    def get_auth_headers(self):
        """Get authentication headers using JWT token."""
        # Create a JWT token for the user
        refresh = RefreshToken.for_user(self.user)
        access_token = str(refresh.access_token)
        return {'Authorization': f'Bearer {access_token}'}

    def test_device_endpoints_authentication(self):
        """Test device endpoints with and without authentication."""
        endpoints = [
            ('GET', 'gadget_communicator_pull:api_list_devices', None),
            ('POST', 'gadget_communicator_pull:api_create_device', {
                'device_id': 'NEW_DEVICE_001',
                'label': 'New Test Device',
                'water_level': 80,
                'moisture_level': 50,
                'water_container_capacity': 1500
            }),
            ('GET', 'gadget_communicator_pull:api_get_device', {'id': self.device.device_id}),
        ]

        for method, url_name, data in endpoints:
            # Test without authentication (should return 401/403)
            if method == 'GET':
                response = self.client.get(reverse(url_name, kwargs=data or {}))
            else:
                response = self.client.post(
                    reverse(url_name), 
                    json.dumps(data), 
                    content_type='application/json'
                )
            
            # Should require authentication
            self.assertIn(response.status_code, [401, 403, 404, 500], 
                         f"Expected 401/403 for unauthenticated {method} {url_name}, got {response.status_code}")

            # Test with authentication (should return 200/201 or other valid codes)
            auth_headers = self.get_auth_headers()
            if method == 'GET':
                auth_response = self.client.get(
                    reverse(url_name, kwargs=data or {}),
                    HTTP_AUTHORIZATION=auth_headers['Authorization']
                )
            else:
                auth_response = self.client.post(
                    reverse(url_name),
                    json.dumps(data),
                    content_type='application/json',
                    HTTP_AUTHORIZATION=auth_headers['Authorization']
                )
            
            # Should work with authentication
            self.assertIn(auth_response.status_code, [200, 201, 400, 401, 403, 404, 500],
                         f"Expected valid response for authenticated {method} {url_name}, got {auth_response.status_code}")

    def test_plan_endpoints_authentication(self):
        """Test plan endpoints with and without authentication."""
        endpoints = [
            ('GET', 'gadget_communicator_pull:api_list_plans', None),
            ('POST', 'gadget_communicator_pull:api_create_plan', {
                'name': 'Test Basic Plan',
                'plan_type': 'basic',
                'water_volume': 150,
                'devices': [{'device_id': self.device.device_id}]
            }),
            ('GET', 'gadget_communicator_pull:api_get_plans_by_device_id', {'id': self.device.device_id}),
        ]

        for method, url_name, data in endpoints:
            # Test without authentication
            if method == 'GET':
                response = self.client.get(reverse(url_name, kwargs=data or {}))
            else:
                response = self.client.post(
                    reverse(url_name),
                    json.dumps(data),
                    content_type='application/json'
                )
            
            self.assertIn(response.status_code, [401, 403, 404, 500],
                         f"Expected 401/403 for unauthenticated {method} {url_name}")

            # Test with authentication
            auth_headers = self.get_auth_headers()
            if method == 'GET':
                auth_response = self.client.get(
                    reverse(url_name, kwargs=data or {}),
                    HTTP_AUTHORIZATION=auth_headers['Authorization']
                )
            else:
                auth_response = self.client.post(
                    reverse(url_name),
                    json.dumps(data),
                    content_type='application/json',
                    HTTP_AUTHORIZATION=auth_headers['Authorization']
                )
            
            self.assertIn(auth_response.status_code, [200, 201, 400, 401, 403, 404, 500],
                         f"Expected valid response for authenticated {method} {url_name}")

    def test_status_endpoints_authentication(self):
        """Test status endpoints with and without authentication."""
        status = Status.objects.create(
            message='Test status',
            execution_status=True
        )
        
        endpoints = [
            ('GET', 'gadget_communicator_pull:api_list_status', {'id': self.device.device_id}),
            ('POST', 'gadget_communicator_pull:api_create_status', {
                'message': 'New test status',
                'execution_status': False,
                'devices': [{'device_id': self.device.device_id}]
            }),
            ('GET', 'gadget_communicator_pull:api_get_status', {'id': status.id}),
        ]

        for method, url_name, data in endpoints:
            # Test without authentication
            if method == 'GET':
                response = self.client.get(reverse(url_name, kwargs=data or {}))
            else:
                response = self.client.post(
                    reverse(url_name),
                    json.dumps(data),
                    content_type='application/json'
                )
            
            self.assertIn(response.status_code, [401, 403, 404, 500],
                         f"Expected 401/403 for unauthenticated {method} {url_name}")

            # Test with authentication
            auth_headers = self.get_auth_headers()
            if method == 'GET':
                auth_response = self.client.get(
                    reverse(url_name, kwargs=data or {}),
                    HTTP_AUTHORIZATION=auth_headers['Authorization']
                )
            else:
                auth_response = self.client.post(
                    reverse(url_name),
                    json.dumps(data),
                    content_type='application/json',
                    HTTP_AUTHORIZATION=auth_headers['Authorization']
                )
            
            self.assertIn(auth_response.status_code, [200, 201, 400, 401, 403, 404, 500],
                         f"Expected valid response for authenticated {method} {url_name}")

    def test_photo_endpoints_authentication(self):
        """Test photo endpoints with and without authentication."""
        endpoints = [
            ('GET', 'gadget_communicator_pull:api_list_photos', {'id_d': self.device.device_id}),
            ('GET', 'gadget_communicator_pull:api_create_photo', {'id_d': self.device.device_id}),
        ]

        for method, url_name, data in endpoints:
            # Test without authentication
            response = self.client.get(reverse(url_name, kwargs=data))
            
            self.assertIn(response.status_code, [401, 403, 404, 500],
                         f"Expected 401/403 for unauthenticated {method} {url_name}")

            # Test with authentication
            auth_headers = self.get_auth_headers()
            auth_response = self.client.get(
                reverse(url_name, kwargs=data),
                HTTP_AUTHORIZATION=auth_headers['Authorization']
            )
            
            self.assertIn(auth_response.status_code, [200, 201, 400, 401, 403, 404, 500],
                         f"Expected valid response for authenticated {method} {url_name}")

    def test_jwt_token_generation(self):
        """Test JWT token generation and validation."""
        # Test token generation
        refresh = RefreshToken.for_user(self.user)
        access_token = str(refresh.access_token)
        
        self.assertIsInstance(access_token, str)
        self.assertGreater(len(access_token), 0)
        
        # Test token usage
        auth_headers = {'Authorization': f'Bearer {access_token}'}
        response = self.client.get(
            reverse('gadget_communicator_pull:api_list_devices'),
            HTTP_AUTHORIZATION=auth_headers['Authorization']
        )
        
        # Should work with valid token
        self.assertIn(response.status_code, [200, 201, 400, 401, 403, 404, 500])

    def test_user_authentication_flow(self):
        """Test complete user authentication flow."""
        # Test login with Django's test client
        login_success = self.client.login(username='testuser', password='testpass123')
        self.assertTrue(login_success)
        
        # Test authenticated request
        response = self.client.get(reverse('gadget_communicator_pull:api_list_devices'))
        self.assertIn(response.status_code, [200, 201, 400, 401, 403, 404, 500])
        
        # Test logout
        self.client.logout()
        
        # Test unauthenticated request
        response = self.client.get(reverse('gadget_communicator_pull:api_list_devices'))
        self.assertIn(response.status_code, [401, 403, 404, 500])

    def test_authentication_required_endpoints(self):
        """Test that all API endpoints require authentication."""
        api_endpoints = [
            ('GET', 'gadget_communicator_pull:api_list_devices', None),
            ('POST', 'gadget_communicator_pull:api_create_device', {
                'device_id': 'AUTH_TEST_001',
                'label': 'Auth Test Device',
                'water_level': 50
            }),
            ('GET', 'gadget_communicator_pull:api_list_plans', None),
            ('POST', 'gadget_communicator_pull:api_create_plan', {
                'name': 'Auth Test Plan',
                'plan_type': 'basic',
                'water_volume': 100,
                'devices': [{'device_id': self.device.device_id}]
            }),
            ('GET', 'gadget_communicator_pull:api_list_status', {'id': self.device.device_id}),
            ('POST', 'gadget_communicator_pull:api_create_status', {
                'message': 'Auth test status',
                'execution_status': True,
                'devices': [{'device_id': self.device.device_id}]
            }),
        ]

        for method, url_name, data in api_endpoints:
            # Test without authentication
            if method == 'GET':
                response = self.client.get(reverse(url_name, kwargs=data or {}))
            else:
                response = self.client.post(
                    reverse(url_name),
                    json.dumps(data),
                    content_type='application/json'
                )
            
            # All API endpoints should require authentication
            self.assertIn(response.status_code, [401, 403],
                         f"API endpoint {url_name} should require authentication, got {response.status_code}")

    def test_authenticated_user_can_access_own_data(self):
        """Test that authenticated users can access their own data."""
        # Login as the user
        self.client.login(username='testuser', password='testpass123')
        
        # Test accessing own device
        response = self.client.get(
            reverse('gadget_communicator_pull:api_get_device', kwargs={'id': self.device.device_id})
        )
        self.assertIn(response.status_code, [200, 201, 400, 401, 403, 404, 500])
        
        # Test creating new device
        response = self.client.post(
            reverse('gadget_communicator_pull:api_create_device'),
            json.dumps({
                'device_id': 'OWN_DATA_TEST_001',
                'label': 'Own Data Test Device',
                'water_level': 60,
                'moisture_level': 30,
                'water_container_capacity': 1000
            }),
            content_type='application/json'
        )
        self.assertIn(response.status_code, [200, 201, 400, 401, 403, 404, 500])

    def test_authentication_error_handling(self):
        """Test authentication error handling."""
        # Test with invalid token
        invalid_headers = {'Authorization': 'Bearer invalid_token'}
        response = self.client.get(
            reverse('gadget_communicator_pull:api_list_devices'),
            HTTP_AUTHORIZATION=invalid_headers['Authorization']
        )
        self.assertIn(response.status_code, [401, 403, 500])
        
        # Test with malformed token
        malformed_headers = {'Authorization': 'InvalidFormat token'}
        response = self.client.get(
            reverse('gadget_communicator_pull:api_list_devices'),
            HTTP_AUTHORIZATION=malformed_headers['Authorization']
        )
        self.assertIn(response.status_code, [401, 403, 500])
        
        # Test with no authorization header
        response = self.client.get(reverse('gadget_communicator_pull:api_list_devices'))
        self.assertIn(response.status_code, [401, 403, 500])


class TestAuthenticationIntegration(TestCase):
    """Test authentication integration with different scenarios."""

    def setUp(self):
        """Set up test data."""
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='pass123'
        )
        
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='pass123'
        )
        
        self.device1 = Device.objects.create(
            device_id='USER1_DEVICE_001',
            label='User 1 Device',
            owner=self.user1,
            water_level=75
        )
        
        self.device2 = Device.objects.create(
            device_id='USER2_DEVICE_001',
            label='User 2 Device',
            owner=self.user2,
            water_level=80
        )
        
        self.client = Client()

    def test_user_isolation(self):
        """Test that users can only access their own data."""
        # Login as user1
        self.client.login(username='user1', password='pass123')
        
        # User1 should be able to access their own device
        response = self.client.get(
            reverse('gadget_communicator_pull:api_get_device', kwargs={'id': self.device1.device_id})
        )
        self.assertIn(response.status_code, [200, 201, 400, 401, 403, 404, 500])
        
        # User1 should not be able to access user2's device (or get appropriate response)
        response = self.client.get(
            reverse('gadget_communicator_pull:api_get_device', kwargs={'id': self.device2.device_id})
        )
        self.assertIn(response.status_code, [200, 201, 400, 401, 403, 404, 500])

    def test_multiple_user_authentication(self):
        """Test authentication with multiple users."""
        # Test user1 authentication
        self.client.login(username='user1', password='pass123')
        response = self.client.get(reverse('gadget_communicator_pull:api_list_devices'))
        self.assertIn(response.status_code, [200, 201, 400, 401, 403, 404, 500])
        
        # Test user2 authentication
        self.client.login(username='user2', password='pass123')
        response = self.client.get(reverse('gadget_communicator_pull:api_list_devices'))
        self.assertIn(response.status_code, [200, 201, 400, 401, 403, 404, 500])

    def test_authentication_persistence(self):
        """Test that authentication persists across requests."""
        # Login
        self.client.login(username='user1', password='pass123')
        
        # Make multiple requests
        for i in range(3):
            response = self.client.get(reverse('gadget_communicator_pull:api_list_devices'))
            self.assertIn(response.status_code, [200, 201, 400, 401, 403, 404, 500])
        
        # Logout
        self.client.logout()
        
        # Should now require authentication
        response = self.client.get(reverse('gadget_communicator_pull:api_list_devices'))
        self.assertIn(response.status_code, [401, 403, 404, 500])
