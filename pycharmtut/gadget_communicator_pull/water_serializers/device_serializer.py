"""
Device Serializer for water plant automation system.

This module defines serializers for Device and WaterChart models,
providing comprehensive serialization with validation and computed fields.
"""
from typing import Dict, Any, List, Optional
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from gadget_communicator_pull.models.device_module import Device, WaterChart


class WaterChartSerializer(serializers.ModelSerializer):
    """
    Serializer for WaterChart model.
    
    Provides serialization for water level history data with validation
    and computed fields.
    
    Attributes:
        device_label: Human-readable device name (read-only)
        water_level_ml: Water level in milliliters (read-only)
        recorded_at: When the data was recorded (read-only)
    """
    
    device_label = serializers.CharField(source='device.label', read_only=True)
    water_level_ml = serializers.SerializerMethodField()
    recorded_at = serializers.DateTimeField(read_only=True)

    class Meta:
        """Meta options for WaterChartSerializer."""
        model = WaterChart
        fields = [
            'id',
            'water_level',
            'water_level_ml',
            'device_label',
            'recorded_at'
        ]
        read_only_fields = ['id', 'recorded_at']

    def get_water_level_ml(self, obj: WaterChart) -> int:
        """
        Get water level in milliliters.
        
        Args:
            obj: WaterChart instance
            
        Returns:
            int: Water level in milliliters
        """
        return int((obj.water_level / 100) * obj.device.water_container_capacity)

    def validate_water_level(self, value: int) -> int:
        """
        Validate water level.
        
        Args:
            value: Water level to validate
            
        Returns:
            int: Validated water level
            
        Raises:
            ValidationError: If validation fails
        """
        if value < 0:
            raise ValidationError("Water level cannot be negative")
        
        if value > 100:
            raise ValidationError("Water level cannot exceed 100%")
        
        return value


class DeviceSerializer(serializers.ModelSerializer):
    """
    Serializer for Device model.
    
    Provides comprehensive serialization for water plant automation devices
    with validation, computed fields, and relationship handling.
    
    Attributes:
        owner_username: Username of the device owner (read-only)
        is_online: Whether the device is online (read-only)
        water_level_ml: Current water level in milliliters (read-only)
        needs_water_refill: Whether the device needs water refill (read-only)
        needs_watering: Whether the plant needs watering (read-only)
        basic_plans: Associated basic plans (read-only)
        time_plans: Associated time plans (read-only)
        moisture_plans: Associated moisture plans (read-only)
        recent_statuses: Recent status entries (read-only)
        water_charts: Water level history (read-only)
    """
    
    owner_username = serializers.CharField(source='owner.username', read_only=True)
    is_online = serializers.BooleanField(read_only=True)
    water_level_ml = serializers.SerializerMethodField()
    needs_water_refill = serializers.BooleanField(read_only=True)
    needs_watering = serializers.BooleanField(read_only=True)
    
    # Related data (read-only)
    basic_plans = serializers.SerializerMethodField()
    time_plans = serializers.SerializerMethodField()
    moisture_plans = serializers.SerializerMethodField()
    recent_statuses = serializers.SerializerMethodField()
    water_charts = WaterChartSerializer(many=True, read_only=True)

    class Meta:
        """Meta options for DeviceSerializer."""
        model = Device
        fields = [
            'id',
            'device_id',
            'label',
            'owner_username',
            'water_level',
            'water_level_ml',
            'moisture_level',
            'water_container_capacity',
            'water_reset',
            'send_email',
            'is_connected',
            'is_online',
            'status',
            'last_seen',
            'location',
            'notes',
            'needs_water_refill',
            'needs_watering',
            'basic_plans',
            'time_plans',
            'moisture_plans',
            'recent_statuses',
            'water_charts',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id', 'is_online', 'water_level_ml', 'needs_water_refill',
            'needs_watering', 'basic_plans', 'time_plans', 'moisture_plans',
            'recent_statuses', 'water_charts', 'created_at', 'updated_at'
        ]

    def get_water_level_ml(self, obj: Device) -> int:
        """
        Get current water level in milliliters.
        
        Args:
            obj: Device instance
            
        Returns:
            int: Water level in milliliters
        """
        return obj.water_level_ml

    def get_basic_plans(self, obj: Device) -> List[Dict[str, Any]]:
        """
        Get associated basic plans.
        
        Args:
            obj: Device instance
            
        Returns:
            List[Dict[str, Any]]: Basic plans data
        """
        return [
            {
                'id': plan.id,
                'name': plan.name,
                'water_volume': plan.water_volume,
                'has_been_executed': plan.has_been_executed
            }
            for plan in obj.get_basic_plans()
        ]

    def get_time_plans(self, obj: Device) -> List[Dict[str, Any]]:
        """
        Get associated time plans.
        
        Args:
            obj: Device instance
            
        Returns:
            List[Dict[str, Any]]: Time plans data
        """
        return [
            {
                'id': plan.id,
                'name': plan.name,
                'water_volume': plan.water_volume,
                'execute_only_once': plan.execute_only_once,
                'is_running': plan.is_running,
                'has_been_executed': plan.has_been_executed
            }
            for plan in obj.get_time_plans()
        ]

    def get_moisture_plans(self, obj: Device) -> List[Dict[str, Any]]:
        """
        Get associated moisture plans.
        
        Args:
            obj: Device instance
            
        Returns:
            List[Dict[str, Any]]: Moisture plans data
        """
        return [
            {
                'id': plan.id,
                'name': plan.name,
                'water_volume': plan.water_volume,
                'moisture_threshold': plan.moisture_threshold,
                'check_interval': plan.check_interval,
                'is_running': plan.is_running,
                'has_been_executed': plan.has_been_executed
            }
            for plan in obj.get_moisture_plans()
        ]

    def get_recent_statuses(self, obj: Device) -> List[Dict[str, Any]]:
        """
        Get recent status entries.
        
        Args:
            obj: Device instance
            
        Returns:
            List[Dict[str, Any]]: Recent statuses data
        """
        return [
            {
                'id': status.id,
                'execution_status': status.execution_status,
                'message': status.message,
                'status_type': status.status_type,
                'status_time': status.status_time
            }
            for status in obj.get_recent_statuses()
        ]

    def validate_device_id(self, value: str) -> str:
        """
        Validate device ID.
        
        Args:
            value: Device ID to validate
            
        Returns:
            str: Validated device ID
            
        Raises:
            ValidationError: If validation fails
        """
        if not value or len(value.strip()) < 3:
            raise ValidationError("Device ID must be at least 3 characters long")
        
        if len(value) > 100:
            raise ValidationError("Device ID cannot exceed 100 characters")
        
        return value.strip()

    def validate_label(self, value: str) -> str:
        """
        Validate device label.
        
        Args:
            value: Device label to validate
            
        Returns:
            str: Validated device label
            
        Raises:
            ValidationError: If validation fails
        """
        if not value or len(value.strip()) < 3:
            raise ValidationError("Device label must be at least 3 characters long")
        
        if len(value) > 100:
            raise ValidationError("Device label cannot exceed 100 characters")
        
        return value.strip()

    def validate_water_level(self, value: int) -> int:
        """
        Validate water level.
        
        Args:
            value: Water level to validate
            
        Returns:
            int: Validated water level
            
        Raises:
            ValidationError: If validation fails
        """
        if value < 0:
            raise ValidationError("Water level cannot be negative")
        
        if value > 100:
            raise ValidationError("Water level cannot exceed 100%")
        
        return value

    def validate_moisture_level(self, value: int) -> int:
        """
        Validate moisture level.
        
        Args:
            value: Moisture level to validate
            
        Returns:
            int: Validated moisture level
            
        Raises:
            ValidationError: If validation fails
        """
        if value < 0:
            raise ValidationError("Moisture level cannot be negative")
        
        if value > 100:
            raise ValidationError("Moisture level cannot exceed 100%")
        
        return value

    def validate_water_container_capacity(self, value: int) -> int:
        """
        Validate water container capacity.
        
        Args:
            value: Water container capacity to validate
            
        Returns:
            int: Validated water container capacity
            
        Raises:
            ValidationError: If validation fails
        """
        if value < 100:
            raise ValidationError("Water container capacity must be at least 100ml")
        
        if value > 10000:
            raise ValidationError("Water container capacity cannot exceed 10000ml")
        
        return value

    def validate_status(self, value: str) -> str:
        """
        Validate device status.
        
        Args:
            value: Device status to validate
            
        Returns:
            str: Validated device status
            
        Raises:
            ValidationError: If validation fails
        """
        valid_statuses = ['online', 'offline', 'maintenance', 'error']
        if value not in valid_statuses:
            raise ValidationError(f"Status must be one of: {', '.join(valid_statuses)}")
        
        return value

    def create(self, validated_data: Dict[str, Any]) -> Device:
        """
        Create a new device instance.
        
        Args:
            validated_data: Validated device data
            
        Returns:
            Device: Created device instance
        """
        return super().create(validated_data)

    def update(self, instance: Device, validated_data: Dict[str, Any]) -> Device:
        """
        Update an existing device instance.
        
        Args:
            instance: Device instance to update
            validated_data: Validated device data
            
        Returns:
            Device: Updated device instance
        """
        return super().update(instance, validated_data)

    def to_representation(self, instance: Device) -> Dict[str, Any]:
        """
        Convert model instance to dictionary representation.
        
        Args:
            instance: Device instance to serialize
            
        Returns:
            Dict[str, Any]: Serialized device data
        """
        data = super().to_representation(instance)
        
        # Add computed fields
        data['is_online'] = instance.is_online
        data['needs_water_refill'] = instance.needs_water_refill
        data['needs_watering'] = instance.needs_watering
        
        return data
