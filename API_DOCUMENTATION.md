# WaterPlantApp API Documentation

## Overview
WaterPlantApp provides a REST API for managing water plant automation systems. The API enables WaterPlantOperator devices to communicate with the central server.

## Quick Start
1. **Setup**: Run `./setup.sh` to install dependencies
2. **Start**: Run `./start.sh` to start the server
3. **Test**: Run `./test.sh` to verify everything works

## Table of Contents
1. [Authentication](#authentication)
2. [Base URL and Endpoints](#base-url-and-endpoints)
3. [Device Management API](#device-management-api)
4. [Plan Management API](#plan-management-api)
5. [Status Management API](#status-management-api)
6. [Camera API](#camera-api)
7. [Health Check API](#health-check-api)
8. [Error Handling](#error-handling)
9. [Examples](#examples)

## Authentication

### Authentication Methods
WaterPlantApp supports multiple authentication methods:

1. **Session Authentication** (for web interface)
2. **Token Authentication** (for API access)
3. **Basic Authentication** (for device communication)

### Token Authentication
```bash
# Get authentication token
curl -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "your_username", "password": "your_password"}'

# Use token in requests
curl -H "Authorization: Token your_token_here" \
  http://localhost:8000/api/devices/
```

### Device Authentication
WaterPlantOperator devices use device-specific authentication:
```bash
# Device authentication
curl -X POST http://localhost:8000/api/device-auth/ \
  -H "Content-Type: application/json" \
  -d '{"device_id": "DEVICE_001", "device_key": "device_secret_key"}'
```

## Base URL and Endpoints

### Base URL
- **Development**: `http://localhost:8000`
- **Production**: `https://your-domain.com`

### API Versioning
All API endpoints are versioned:
- **Current Version**: `/api/v1/`
- **Example**: `http://localhost:8000/api/v1/devices/`

## Device Management API

### List Devices
Get a list of all devices for the authenticated user.

**Endpoint**: `GET /api/v1/devices/`

**Parameters**:
- `page` (optional): Page number for pagination
- `page_size` (optional): Number of items per page (default: 20)
- `search` (optional): Search term for device name or ID
- `status` (optional): Filter by device status (`online`, `offline`)
- `ordering` (optional): Sort by field (`device_id`, `label`, `created_at`)

**Response**:
```json
{
  "count": 5,
  "next": "http://localhost:8000/api/v1/devices/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "device_id": "DEVICE_001",
      "label": "Living Room Plant",
      "owner_username": "user1",
      "water_level": 75,
      "moisture_level": 45,
      "water_container_capacity": 2000,
      "status": "online",
      "is_online": true,
      "water_level_ml": 1500,
      "needs_water_refill": false,
      "needs_watering": false,
      "created_at": "2023-01-01T10:00:00Z",
      "updated_at": "2023-01-01T12:00:00Z"
    }
  ]
}
```

### Get Device Details
Get detailed information about a specific device.

**Endpoint**: `GET /api/v1/devices/{device_id}/`

**Response**:
```json
{
  "id": 1,
  "device_id": "DEVICE_001",
  "label": "Living Room Plant",
  "owner_username": "user1",
  "water_level": 75,
  "moisture_level": 45,
  "water_container_capacity": 2000,
  "status": "online",
  "is_online": true,
  "water_level_ml": 1500,
  "needs_water_refill": false,
  "needs_watering": false,
  "basic_plans": [
    {
      "id": 1,
      "name": "Morning Watering",
      "plan_type": "basic",
      "water_volume": 150,
      "is_executable": true
    }
  ],
  "moisture_plans": [],
  "time_plans": [],
  "recent_statuses": [
    {
      "id": 1,
      "message": "Watering completed successfully",
      "status_type": "success",
      "created_at": "2023-01-01T12:00:00Z"
    }
  ],
  "created_at": "2023-01-01T10:00:00Z",
  "updated_at": "2023-01-01T12:00:00Z"
}
```

### Create Device
Create a new device.

**Endpoint**: `POST /api/v1/devices/`

**Request Body**:
```json
{
  "device_id": "DEVICE_002",
  "label": "Kitchen Plant",
  "water_level": 80,
  "moisture_level": 50,
  "water_container_capacity": 2500,
  "status": "online"
}
```

**Response**: `201 Created`
```json
{
  "id": 2,
  "device_id": "DEVICE_002",
  "label": "Kitchen Plant",
  "owner_username": "user1",
  "water_level": 80,
  "moisture_level": 50,
  "water_container_capacity": 2500,
  "status": "online",
  "is_online": true,
  "water_level_ml": 2000,
  "needs_water_refill": false,
  "needs_watering": false,
  "created_at": "2023-01-01T13:00:00Z",
  "updated_at": "2023-01-01T13:00:00Z"
}
```

### Update Device
Update an existing device.

**Endpoint**: `PUT /api/v1/devices/{device_id}/`

**Request Body**:
```json
{
  "label": "Updated Kitchen Plant",
  "water_level": 90,
  "moisture_level": 60
}
```

**Response**: `200 OK`
```json
{
  "id": 2,
  "device_id": "DEVICE_002",
  "label": "Updated Kitchen Plant",
  "owner_username": "user1",
  "water_level": 90,
  "moisture_level": 60,
  "water_container_capacity": 2500,
  "status": "online",
  "is_online": true,
  "water_level_ml": 2250,
  "needs_water_refill": false,
  "needs_watering": false,
  "updated_at": "2023-01-01T14:00:00Z"
}
```

### Delete Device
Delete a device.

**Endpoint**: `DELETE /api/v1/devices/{device_id}/`

**Response**: `204 No Content`

### Device Water Chart
Get water level history for a device.

**Endpoint**: `GET /api/v1/devices/{device_id}/water-chart/`

**Parameters**:
- `days` (optional): Number of days to retrieve (default: 7)
- `start_date` (optional): Start date (ISO format)
- `end_date` (optional): End date (ISO format)

**Response**:
```json
[
  {
    "id": 1,
    "water_level": 75,
    "water_level_ml": 1500,
    "timestamp": "2023-01-01T10:00:00Z"
  },
  {
    "id": 2,
    "water_level": 80,
    "water_level_ml": 1600,
    "timestamp": "2023-01-01T11:00:00Z"
  }
]
```

## Plan Management API

### List Plans
Get all plans for a user.

**Endpoint**: `GET /api/v1/plans/`

**Parameters**:
- `device_id` (optional): Filter by device ID
- `plan_type` (optional): Filter by plan type (`basic`, `moisture`, `time_based`)
- `page` (optional): Page number for pagination
- `page_size` (optional): Number of items per page

**Response**:
```json
{
  "count": 3,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Morning Watering",
      "plan_type": "basic",
      "water_volume": 150,
      "device": 1,
      "is_executable": true,
      "created_at": "2023-01-01T10:00:00Z"
    },
    {
      "id": 2,
      "name": "Moisture-based Watering",
      "plan_type": "moisture",
      "water_volume": 200,
      "moisture_threshold": 0.4,
      "check_interval": 30,
      "moisture_threshold_percentage": 40.0,
      "device": 1,
      "is_executable": true,
      "created_at": "2023-01-01T10:00:00Z"
    }
  ]
}
```

### Get Plans by Device
Get all plans for a specific device.

**Endpoint**: `GET /api/v1/devices/{device_id}/plans/`

**Response**:
```json
[
  {
    "id": 1,
    "name": "Morning Watering",
    "plan_type": "basic",
    "water_volume": 150,
    "is_executable": true
  },
  {
    "id": 2,
    "name": "Moisture-based Watering",
    "plan_type": "moisture",
    "water_volume": 200,
    "moisture_threshold": 0.4,
    "check_interval": 30,
    "moisture_threshold_percentage": 40.0,
    "is_executable": true
  }
]
```

### Create Basic Plan
Create a new basic watering plan.

**Endpoint**: `POST /api/v1/plans/`

**Request Body**:
```json
{
  "name": "Evening Watering",
  "plan_type": "basic",
  "water_volume": 180,
  "device": 1
}
```

**Response**: `201 Created`
```json
{
  "id": 3,
  "name": "Evening Watering",
  "plan_type": "basic",
  "water_volume": 180,
  "device": 1,
  "is_executable": true,
  "created_at": "2023-01-01T15:00:00Z"
}
```

### Create Moisture Plan
Create a new moisture-based watering plan.

**Endpoint**: `POST /api/v1/plans/`

**Request Body**:
```json
{
  "name": "Smart Moisture Watering",
  "plan_type": "moisture",
  "water_volume": 200,
  "moisture_threshold": 0.3,
  "check_interval": 60,
  "device": 1
}
```

**Response**: `201 Created`
```json
{
  "id": 4,
  "name": "Smart Moisture Watering",
  "plan_type": "moisture",
  "water_volume": 200,
  "moisture_threshold": 0.3,
  "check_interval": 60,
  "moisture_threshold_percentage": 30.0,
  "device": 1,
  "is_executable": true,
  "created_at": "2023-01-01T15:00:00Z"
}
```

### Create Time Plan
Create a new time-based watering plan.

**Endpoint**: `POST /api/v1/plans/`

**Request Body**:
```json
{
  "name": "Scheduled Watering",
  "plan_type": "time_based",
  "water_volume": 150,
  "execute_only_once": false,
  "device": 1,
  "water_times": [
    {
      "weekday": "monday",
      "time": "09:00:00",
      "is_active": true
    },
    {
      "weekday": "wednesday",
      "time": "14:00:00",
      "is_active": true
    },
    {
      "weekday": "friday",
      "time": "18:00:00",
      "is_active": true
    }
  ]
}
```

**Response**: `201 Created`
```json
{
  "id": 5,
  "name": "Scheduled Watering",
  "plan_type": "time_based",
  "water_volume": 150,
  "execute_only_once": false,
  "device": 1,
  "water_times": [
    {
      "id": 1,
      "weekday": "monday",
      "time": "09:00:00",
      "is_active": true,
      "weekday_name": "Monday"
    },
    {
      "id": 2,
      "weekday": "wednesday",
      "time": "14:00:00",
      "is_active": true,
      "weekday_name": "Wednesday"
    },
    {
      "id": 3,
      "weekday": "friday",
      "time": "18:00:00",
      "is_active": true,
      "weekday_name": "Friday"
    }
  ],
  "is_executable": true,
  "created_at": "2023-01-01T15:00:00Z"
}
```

### Update Plan
Update an existing plan.

**Endpoint**: `PUT /api/v1/plans/{plan_id}/`

**Request Body**:
```json
{
  "name": "Updated Morning Watering",
  "water_volume": 200
}
```

**Response**: `200 OK`
```json
{
  "id": 1,
  "name": "Updated Morning Watering",
  "plan_type": "basic",
  "water_volume": 200,
  "device": 1,
  "is_executable": true,
  "updated_at": "2023-01-01T16:00:00Z"
}
```

### Delete Plan
Delete a plan.

**Endpoint**: `DELETE /api/v1/plans/{plan_id}/`

**Response**: `204 No Content`

## Status Management API

### List Statuses
Get all status messages for a user.

**Endpoint**: `GET /api/v1/statuses/`

**Parameters**:
- `device_id` (optional): Filter by device ID
- `status_type` (optional): Filter by status type (`success`, `error`, `warning`)
- `page` (optional): Page number for pagination
- `page_size` (optional): Number of items per page

**Response**:
```json
{
  "count": 10,
  "next": "http://localhost:8000/api/v1/statuses/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "message": "Watering completed successfully",
      "status_type": "success",
      "device": 1,
      "is_success": true,
      "is_failure": false,
      "status_icon": "✅",
      "created_at": "2023-01-01T12:00:00Z"
    },
    {
      "id": 2,
      "message": "Low water level detected",
      "status_type": "warning",
      "device": 1,
      "is_success": false,
      "is_failure": false,
      "status_icon": "⚠️",
      "created_at": "2023-01-01T11:30:00Z"
    }
  ]
}
```

### Get Status Details
Get detailed information about a specific status.

**Endpoint**: `GET /api/v1/statuses/{status_id}/`

**Response**:
```json
{
  "id": 1,
  "message": "Watering completed successfully",
  "status_type": "success",
  "device": {
    "id": 1,
    "device_id": "DEVICE_001",
    "label": "Living Room Plant"
  },
  "is_success": true,
  "is_failure": false,
  "status_icon": "✅",
  "created_at": "2023-01-01T12:00:00Z"
}
```

### Create Status
Create a new status message.

**Endpoint**: `POST /api/v1/statuses/`

**Request Body**:
```json
{
  "message": "Device connected successfully",
  "status_type": "success",
  "device": 1
}
```

**Response**: `201 Created`
```json
{
  "id": 3,
  "message": "Device connected successfully",
  "status_type": "success",
  "device": 1,
  "is_success": true,
  "is_failure": false,
  "status_icon": "✅",
  "created_at": "2023-01-01T16:00:00Z"
}
```

### Delete Status
Delete a status message.

**Endpoint**: `DELETE /api/v1/statuses/{status_id}/`

**Response**: `204 No Content`

## Camera API

### Take Photo (Async)
Trigger photo capture on a device.

**Endpoint**: `POST /api/v1/camera/take-photo/`

**Request Body**:
```json
{
  "device_id": "DEVICE_001",
  "photo_name": "plant_photo_001"
}
```

**Response**: `202 Accepted`
```json
{
  "success": true,
  "message": "Photo capture initiated",
  "photo_name": "plant_photo_001",
  "status": "processing"
}
```

### List Photos
Get a list of available photos.

**Endpoint**: `GET /api/v1/camera/photos/`

**Parameters**:
- `device_id` (optional): Filter by device ID
- `page` (optional): Page number for pagination

**Response**:
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "photo_name": "plant_photo_001",
      "device_id": "DEVICE_001",
      "file_path": "/media/photos/plant_photo_001.jpg",
      "file_size": 1024000,
      "created_at": "2023-01-01T12:00:00Z"
    }
  ]
}
```

### Get Photo Status
Check the status of a photo capture.

**Endpoint**: `GET /api/v1/camera/photos/{photo_name}/status/`

**Response**:
```json
{
  "photo_name": "plant_photo_001",
  "status": "completed",
  "file_path": "/media/photos/plant_photo_001.jpg",
  "file_size": 1024000,
  "created_at": "2023-01-01T12:00:00Z"
}
```

### Download Photo
Download a photo file.

**Endpoint**: `GET /api/v1/camera/photos/{photo_name}/download/`

**Response**: `200 OK` (Binary file content)
- Content-Type: `image/jpeg`
- Content-Disposition: `attachment; filename="plant_photo_001.jpg"`

### Delete Photo
Delete a photo.

**Endpoint**: `DELETE /api/v1/camera/photos/{photo_name}/`

**Response**: `204 No Content`

## Health Check API

### System Health
Check the overall system health.

**Endpoint**: `GET /api/v1/health/`

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2023-01-01T16:00:00Z",
  "version": "1.0.0",
  "database": "connected",
  "redis": "connected",
  "services": {
    "api": "healthy",
    "database": "healthy",
    "cache": "healthy"
  }
}
```

### Device Health
Check the health of a specific device.

**Endpoint**: `GET /api/v1/devices/{device_id}/health/`

**Response**:
```json
{
  "device_id": "DEVICE_001",
  "status": "online",
  "last_seen": "2023-01-01T15:58:00Z",
  "water_level": 75,
  "moisture_level": 45,
  "battery_level": 85,
  "signal_strength": -45,
  "uptime": "2 days, 5 hours"
}
```

## Error Handling

### Error Response Format
All API errors follow a consistent format:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "field_name": ["This field is required."],
      "water_level": ["Ensure this value is between 0 and 100."]
    }
  },
  "timestamp": "2023-01-01T16:00:00Z",
  "request_id": "req_123456789"
}
```

### HTTP Status Codes
- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `202 Accepted`: Request accepted for processing
- `204 No Content`: Request successful, no content returned
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Access denied
- `404 Not Found`: Resource not found
- `405 Method Not Allowed`: HTTP method not allowed
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

### Common Error Codes
- `VALIDATION_ERROR`: Input validation failed
- `AUTHENTICATION_ERROR`: Authentication failed
- `PERMISSION_ERROR`: Insufficient permissions
- `NOT_FOUND`: Resource not found
- `RATE_LIMIT_EXCEEDED`: Too many requests
- `DEVICE_OFFLINE`: Device is not online
- `PLAN_EXECUTION_ERROR`: Plan execution failed


## Examples

### Complete Device Setup Workflow
```bash
# 1. Create device
curl -X POST http://localhost:8000/api/v1/devices/ \
  -H "Authorization: Token your_token" \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "DEVICE_001",
    "label": "Living Room Plant",
    "water_level": 75,
    "moisture_level": 45,
    "water_container_capacity": 2000,
    "status": "online"
  }'

# 2. Create basic plan
curl -X POST http://localhost:8000/api/v1/plans/ \
  -H "Authorization: Token your_token" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Morning Watering",
    "plan_type": "basic",
    "water_volume": 150,
    "device": 1
  }'

# 3. Create moisture plan
curl -X POST http://localhost:8000/api/v1/plans/ \
  -H "Authorization: Token your_token" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Smart Watering",
    "plan_type": "moisture",
    "water_volume": 200,
    "moisture_threshold": 0.4,
    "check_interval": 30,
    "device": 1
  }'

# 4. Check device status
curl -H "Authorization: Token your_token" \
  http://localhost:8000/api/v1/devices/DEVICE_001/
```

### WaterPlantOperator Integration Example
```python
import requests
import json

class WaterPlantOperatorClient:
    def __init__(self, base_url, device_id, device_key):
        self.base_url = base_url
        self.device_id = device_id
        self.device_key = device_key
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'X-Device-ID': device_id,
            'X-Device-Key': device_key
        })
    
    def send_health_check(self):
        """Send health check to server."""
        response = self.session.post(f"{self.base_url}/api/v1/health/device/")
        return response.json()
    
    def get_water_plan(self):
        """Get watering plan from server."""
        response = self.session.get(f"{self.base_url}/api/v1/devices/{self.device_id}/plans/")
        return response.json()
    
    def send_result(self, plan_id, success, message):
        """Send plan execution result to server."""
        data = {
            'plan_id': plan_id,
            'success': success,
            'message': message
        }
        response = self.session.post(f"{self.base_url}/api/v1/statuses/", json=data)
        return response.json()
    
    def update_device_status(self, water_level, moisture_level):
        """Update device status on server."""
        data = {
            'water_level': water_level,
            'moisture_level': moisture_level
        }
        response = self.session.put(f"{self.base_url}/api/v1/devices/{self.device_id}/", json=data)
        return response.json()

# Usage example
client = WaterPlantOperatorClient(
    base_url="http://localhost:8000",
    device_id="DEVICE_001",
    device_key="device_secret_key"
)

# Send health check
health = client.send_health_check()
print(f"Health check: {health}")

# Get watering plan
plans = client.get_water_plan()
print(f"Available plans: {plans}")

# Update device status
status = client.update_device_status(water_level=80, moisture_level=50)
print(f"Device status updated: {status}")
```

## Setup and Testing

### Automated Setup
```bash
# Complete setup with one command
./setup.sh

# Start the server
./start.sh

# Run all tests
./test.sh
```

### Manual Testing
```bash
# Test API endpoints
curl -H "Authorization: Token your_token" http://localhost:8000/api/v1/devices/

# Test health check
curl http://localhost:8000/api/v1/health/
```

This API documentation provides essential information about endpoints, authentication, and integration for WaterPlantApp.
