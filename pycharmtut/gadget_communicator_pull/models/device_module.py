"""
Device model for water plant automation system.

This module defines the Device model which represents water plant automation
devices and their associated data, plans, and status information.
"""
from typing import Optional, List
from django.db import models
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class Device(models.Model):
    """
    Device model for water plant automation devices.
    
    Represents a water plant automation device with its configuration,
    current status, and associated watering plans.
    
    Attributes:
        owner: User who owns this device
        device_id: Unique identifier for the device
        label: Human-readable name for the device
        water_level: Current water level percentage (0-100)
        moisture_level: Current moisture level percentage (0-100)
        water_container_capacity: Maximum water capacity in milliliters
        water_reset: Whether water level needs to be reset
        send_email: Whether to send email notifications
        is_connected: Whether the device is currently connected
        created_at: When this device was created
        updated_at: When this device was last updated
    """
    
    # Device status choices
    STATUS_CHOICES = [
        ('online', _('Online')),
        ('offline', _('Offline')),
        ('maintenance', _('Maintenance')),
        ('error', _('Error')),
    ]
    
    owner = models.ForeignKey(
        'auth.User',
        related_name='devices',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text=_("User who owns this device"),
        verbose_name=_("Owner")
    )
    
    device_id = models.CharField(
        max_length=100,
        unique=True,
        help_text=_("Unique identifier for the device"),
        verbose_name=_("Device ID")
    )
    
    label = models.CharField(
        max_length=100,
        help_text=_("Human-readable name for the device"),
        verbose_name=_("Device Label")
    )
    
    water_level = models.PositiveIntegerField(
        default=100,
        help_text=_("Current water level percentage (0-100)"),
        verbose_name=_("Water Level (%)")
    )
    
    moisture_level = models.PositiveIntegerField(
        default=0,
        help_text=_("Current moisture level percentage (0-100)"),
        verbose_name=_("Moisture Level (%)")
    )
    
    water_container_capacity = models.PositiveIntegerField(
        default=2000,
        help_text=_("Maximum water capacity in milliliters"),
        verbose_name=_("Water Capacity (ml)")
    )
    
    water_reset = models.BooleanField(
        default=False,
        help_text=_("Whether water level needs to be reset"),
        verbose_name=_("Water Reset Required")
    )
    
    send_email = models.BooleanField(
        default=True,
        help_text=_("Whether to send email notifications"),
        verbose_name=_("Email Notifications")
    )
    
    is_connected = models.BooleanField(
        default=False,
        help_text=_("Whether the device is currently connected"),
        verbose_name=_("Connected")
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='offline',
        help_text=_("Current device status"),
        verbose_name=_("Status")
    )
    
    last_seen = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("When the device was last seen online"),
        verbose_name=_("Last Seen")
    )
    
    location = models.CharField(
        max_length=200,
        blank=True,
        help_text=_("Physical location of the device"),
        verbose_name=_("Location")
    )
    
    notes = models.TextField(
        blank=True,
        help_text=_("Additional notes about the device"),
        verbose_name=_("Notes")
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text=_("When this device was created"),
        verbose_name=_("Created At")
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text=_("When this device was last updated"),
        verbose_name=_("Updated At")
    )

    class Meta:
        """Meta options for Device model."""
        verbose_name = _("Device")
        verbose_name_plural = _("Devices")
        ordering = ['device_id']
        indexes = [
            models.Index(fields=['device_id']),
            models.Index(fields=['is_connected']),
            models.Index(fields=['status']),
            models.Index(fields=['last_seen']),
            models.Index(fields=['created_at']),
        ]

    def clean(self) -> None:
        """
        Validate model fields.
        
        Raises:
            ValidationError: If validation fails
        """
        super().clean()
        
        # Validate water level
        if self.water_level > 100:
            raise ValidationError({
                'water_level': _('Water level cannot exceed 100%')
            })
        
        # Validate moisture level
        if self.moisture_level > 100:
            raise ValidationError({
                'moisture_level': _('Moisture level cannot exceed 100%')
            })
        
        # Validate water container capacity
        if self.water_container_capacity < 100:
            raise ValidationError({
                'water_container_capacity': _('Water container capacity must be at least 100ml')
            })
        
        if self.water_container_capacity > 10000:
            raise ValidationError({
                'water_container_capacity': _('Water container capacity cannot exceed 10000ml')
            })
        
        # Validate device ID format
        if not self.device_id or len(self.device_id.strip()) < 3:
            raise ValidationError({
                'device_id': _('Device ID must be at least 3 characters long')
            })

    def save(self, *args, **kwargs) -> None:
        """Save the model instance with validation."""
        self.full_clean()
        super().save(*args, **kwargs)

    def get_absolute_url(self) -> str:
        """
        Get the absolute URL for this device.
        
        Returns:
            str: URL for the device detail view
        """
        return reverse("gadget_communicator_pull:device-info", kwargs={"id": self.id})

    def __str__(self) -> str:
        """
        String representation of the device.
        
        Returns:
            str: Human-readable representation
        """
        return f"{self.label} ({self.device_id})"

    def __repr__(self) -> str:
        """
        Developer representation of the device.
        
        Returns:
            str: Developer-friendly representation
        """
        return f"Device(id={self.id}, device_id='{self.device_id}', label='{self.label}')"

    @property
    def is_online(self) -> bool:
        """
        Check if the device is online.
        
        Returns:
            bool: True if the device is connected and online
        """
        return self.is_connected and self.status == 'online'

    @property
    def water_level_ml(self) -> int:
        """
        Get current water level in milliliters.
        
        Returns:
            int: Water level in milliliters
        """
        return int((self.water_level / 100) * self.water_container_capacity)

    @property
    def needs_water_refill(self) -> bool:
        """
        Check if the device needs water refill.
        
        Returns:
            bool: True if water level is below 20%
        """
        return self.water_level < 20

    @property
    def needs_watering(self) -> bool:
        """
        Check if the plant needs watering.
        
        Returns:
            bool: True if moisture level is below 30%
        """
        return self.moisture_level < 30

    def connect(self) -> None:
        """Mark device as connected."""
        self.is_connected = True
        self.status = 'online'
        from django.utils import timezone
        self.last_seen = timezone.now()
        self.save(update_fields=['is_connected', 'status', 'last_seen', 'updated_at'])

    def disconnect(self) -> None:
        """Mark device as disconnected."""
        self.is_connected = False
        self.status = 'offline'
        self.save(update_fields=['is_connected', 'status', 'updated_at'])

    def update_water_level(self, level: int) -> None:
        """
        Update water level.
        
        Args:
            level: New water level percentage (0-100)
        """
        if 0 <= level <= 100:
            self.water_level = level
            self.save(update_fields=['water_level', 'updated_at'])

    def update_moisture_level(self, level: int) -> None:
        """
        Update moisture level.
        
        Args:
            level: New moisture level percentage (0-100)
        """
        if 0 <= level <= 100:
            self.moisture_level = level
            self.save(update_fields=['moisture_level', 'updated_at'])

    def reset_water_level(self) -> None:
        """Reset water level to full capacity."""
        self.water_level = 100
        self.water_reset = False
        self.save(update_fields=['water_level', 'water_reset', 'updated_at'])

    def get_basic_plans(self) -> 'models.QuerySet':
        """Get all basic plans associated with this device."""
        return self.device_relation_b.all()

    def get_time_plans(self) -> 'models.QuerySet':
        """Get all time plans associated with this device."""
        return self.device_relation_t.all()

    def get_moisture_plans(self) -> 'models.QuerySet':
        """Get all moisture plans associated with this device."""
        return self.device_relation_m.all()

    def get_recent_statuses(self, limit: int = 10) -> 'models.QuerySet':
        """Get recent status entries for this device."""
        return self.status_relation.all()[:limit]

    @classmethod
    def get_online_devices(cls) -> 'models.QuerySet[Device]':
        """
        Get all online devices.
        
        Returns:
            QuerySet: Online devices
        """
        return cls.objects.filter(is_connected=True, status='online')

    @classmethod
    def get_devices_needing_water(cls) -> 'models.QuerySet[Device]':
        """
        Get devices that need water refill.
        
        Returns:
            QuerySet: Devices needing water
        """
        return cls.objects.filter(water_level__lt=20)

    @classmethod
    def get_devices_needing_watering(cls) -> 'models.QuerySet[Device]':
        """
        Get devices where plants need watering.
        
        Returns:
            QuerySet: Devices needing watering
        """
        return cls.objects.filter(moisture_level__lt=30)


class WaterChart(models.Model):
    """
    Water chart model for tracking water level history.
    
    Represents historical water level data for devices to enable
    trend analysis and monitoring.
    
    Attributes:
        water_level: Water level percentage at the time of recording
        device: Associated device
        recorded_at: When this data point was recorded
    """
    
    water_level = models.PositiveIntegerField(
        help_text=_("Water level percentage (0-100)"),
        verbose_name=_("Water Level (%)")
    )
    
    device = models.ForeignKey(
        Device,
        related_name='water_charts',
        on_delete=models.CASCADE,
        help_text=_("Associated device"),
        verbose_name=_("Device")
    )
    
    recorded_at = models.DateTimeField(
        auto_now_add=True,
        help_text=_("When this data point was recorded"),
        verbose_name=_("Recorded At")
    )

    class Meta:
        """Meta options for WaterChart model."""
        verbose_name = _("Water Chart")
        verbose_name_plural = _("Water Charts")
        ordering = ['-recorded_at']
        indexes = [
            models.Index(fields=['device', 'recorded_at']),
            models.Index(fields=['water_level']),
            models.Index(fields=['recorded_at']),
        ]

    def __str__(self) -> str:
        """String representation of the water chart entry."""
        return f"{self.device.label}: {self.water_level}% at {self.recorded_at}"

    def __repr__(self) -> str:
        """Developer representation of the water chart entry."""
        return f"WaterChart(id={self.id}, device={self.device.device_id}, level={self.water_level}%)"
