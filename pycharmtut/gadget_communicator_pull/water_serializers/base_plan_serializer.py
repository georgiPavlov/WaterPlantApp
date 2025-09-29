"""
Base Plan Serializer for water plant automation system.

This module defines the BasePlanSerializer which provides common serialization
functionality for all watering plan types.
"""
from typing import Dict, Any, List
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from gadget_communicator_pull.models.basic_plan_module import BasicPlan
from gadget_communicator_pull.water_serializers.device_serializer import DeviceSerializer


class BasePlanSerializer(serializers.ModelSerializer):
    """
    Base serializer for watering plans.
    
    Provides common serialization functionality for all plan types,
    including device relationships and validation.
    
    Attributes:
        devices: Associated devices (read-only)
        is_executable: Whether the plan can be executed (read-only)
        created_at: When the plan was created (read-only)
        updated_at: When the plan was last updated (read-only)
    """
    
    devices = DeviceSerializer(many=True, read_only=True, source='devices_b')
    is_executable = serializers.BooleanField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    class Meta:
        """Meta options for BasePlanSerializer."""
        model = BasicPlan
        fields = [
            'id',
            'name', 
            'plan_type', 
            'water_volume', 
            'has_been_executed',
            'devices',
            'is_executable',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_name(self, value: str) -> str:
        """
        Validate plan name.
        
        Args:
            value: Plan name to validate
            
        Returns:
            str: Validated plan name
            
        Raises:
            ValidationError: If validation fails
        """
        if not value or len(value.strip()) < 3:
            raise ValidationError("Plan name must be at least 3 characters long")
        
        if len(value) > 100:
            raise ValidationError("Plan name cannot exceed 100 characters")
        
        return value.strip()

    def validate_water_volume(self, value: int) -> int:
        """
        Validate water volume.
        
        Args:
            value: Water volume to validate
            
        Returns:
            int: Validated water volume
            
        Raises:
            ValidationError: If validation fails
        """
        if value < 50:
            raise ValidationError("Water volume must be at least 50ml")
        
        if value > 2000:
            raise ValidationError("Water volume cannot exceed 2000ml")
        
        return value

    def validate_plan_type(self, value: str) -> str:
        """
        Validate plan type.
        
        Args:
            value: Plan type to validate
            
        Returns:
            str: Validated plan type
            
        Raises:
            ValidationError: If validation fails
        """
        valid_types = ['basic', 'moisture', 'time_based']
        if value not in valid_types:
            raise ValidationError(f"Plan type must be one of: {', '.join(valid_types)}")
        
        return value

    def create(self, validated_data: Dict[str, Any]) -> BasicPlan:
        """
        Create a new plan instance.
        
        Args:
            validated_data: Validated plan data
            
        Returns:
            BasicPlan: Created plan instance
        """
        # Ensure plan_type is set correctly
        validated_data['plan_type'] = 'basic'
        
        return super().create(validated_data)

    def update(self, instance: BasicPlan, validated_data: Dict[str, Any]) -> BasicPlan:
        """
        Update an existing plan instance.
        
        Args:
            instance: Plan instance to update
            validated_data: Validated plan data
            
        Returns:
            BasicPlan: Updated plan instance
        """
        # Ensure plan_type remains consistent
        validated_data['plan_type'] = 'basic'
        
        return super().update(instance, validated_data)

    def to_representation(self, instance: BasicPlan) -> Dict[str, Any]:
        """
        Convert model instance to dictionary representation.
        
        Args:
            instance: Plan instance to serialize
            
        Returns:
            Dict[str, Any]: Serialized plan data
        """
        data = super().to_representation(instance)
        
        # Add computed fields
        data['is_executable'] = instance.is_executable
        data['water_volume_ml'] = instance.water_volume
        
        return data













