"""
Status model for water plant automation system.

This module defines the Status model which represents the execution status
and results of watering operations.
"""
import uuid
from typing import Optional
from django.db import models
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class Status(models.Model):
    """
    Status model for watering operation results.
    
    Represents the execution status and results of watering operations,
    including success/failure status, messages, and timestamps.
    
    Attributes:
        execution_status: Whether the operation was successful
        message: Status message describing the result
        status_id: Unique identifier for the status
        status_time: Timestamp of the status
        created_at: When this status was created
        updated_at: When this status was last updated
    """
    
    # Status type choices
    STATUS_TYPE_CHOICES = [
        ('success', _('Success')),
        ('failure', _('Failure')),
        ('warning', _('Warning')),
        ('info', _('Information')),
    ]
    
    execution_status = models.BooleanField(
        default=False,
        help_text=_("Whether the watering operation was successful"),
        verbose_name=_("Execution Status")
    )
    
    message = models.CharField(
        max_length=500,
        help_text=_("Status message describing the result"),
        verbose_name=_("Status Message")
    )
    
    status_id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        help_text=_("Unique identifier for this status"),
        verbose_name=_("Status ID")
    )
    
    status_time = models.DateTimeField(
        auto_now_add=True,
        help_text=_("When this status was created"),
        verbose_name=_("Status Time")
    )
    
    status_type = models.CharField(
        max_length=20,
        choices=STATUS_TYPE_CHOICES,
        default='info',
        help_text=_("Type of status message"),
        verbose_name=_("Status Type")
    )
    
    device_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text=_("ID of the device that generated this status"),
        verbose_name=_("Device ID")
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text=_("When this status was created"),
        verbose_name=_("Created At")
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text=_("When this status was last updated"),
        verbose_name=_("Updated At")
    )

    class Meta:
        """Meta options for Status model."""
        verbose_name = _("Status")
        verbose_name_plural = _("Statuses")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['execution_status']),
            models.Index(fields=['status_type']),
            models.Index(fields=['device_id']),
            models.Index(fields=['created_at']),
            models.Index(fields=['status_id']),
        ]

    def clean(self) -> None:
        """
        Validate model fields.
        
        Raises:
            ValidationError: If validation fails
        """
        super().clean()
        
        # Validate message length
        if len(self.message.strip()) < 1:
            raise ValidationError({
                'message': _('Status message cannot be empty')
            })
        
        # Validate status type
        if self.status_type not in [choice[0] for choice in self.STATUS_TYPE_CHOICES]:
            raise ValidationError({
                'status_type': _('Invalid status type')
            })

    def save(self, *args, **kwargs) -> None:
        """Save the model instance with validation."""
        self.full_clean()
        super().save(*args, **kwargs)

    def get_absolute_url(self) -> str:
        """
        Get the absolute URL for this status.
        
        Returns:
            str: URL for the status detail view
        """
        return reverse("gadget_communicator_pull:water-status", kwargs={"id": self.id})

    def __str__(self) -> str:
        """
        String representation of the status.
        
        Returns:
            str: Human-readable representation
        """
        status_icon = "✓" if self.execution_status else "✗"
        return f"{status_icon} {self.message[:50]}..."

    def __repr__(self) -> str:
        """
        Developer representation of the status.
        
        Returns:
            str: Developer-friendly representation
        """
        return f"Status(id={self.id}, success={self.execution_status}, message='{self.message[:30]}...')"

    @property
    def is_success(self) -> bool:
        """
        Check if the status represents success.
        
        Returns:
            bool: True if the operation was successful
        """
        return self.execution_status

    @property
    def is_failure(self) -> bool:
        """
        Check if the status represents failure.
        
        Returns:
            bool: True if the operation failed
        """
        return not self.execution_status

    @property
    def status_icon(self) -> str:
        """
        Get an icon representing the status.
        
        Returns:
            str: Icon character for the status
        """
        if self.execution_status:
            return "✓"
        elif self.status_type == 'warning':
            return "⚠"
        elif self.status_type == 'info':
            return "ℹ"
        else:
            return "✗"

    @classmethod
    def create_success(cls, message: str, device_id: Optional[str] = None) -> 'Status':
        """
        Create a success status.
        
        Args:
            message: Success message
            device_id: Optional device ID
            
        Returns:
            Status: New success status instance
        """
        return cls.objects.create(
            execution_status=True,
            message=message,
            status_type='success',
            device_id=device_id
        )

    @classmethod
    def create_failure(cls, message: str, device_id: Optional[str] = None) -> 'Status':
        """
        Create a failure status.
        
        Args:
            message: Failure message
            device_id: Optional device ID
            
        Returns:
            Status: New failure status instance
        """
        return cls.objects.create(
            execution_status=False,
            message=message,
            status_type='failure',
            device_id=device_id
        )

    @classmethod
    def create_warning(cls, message: str, device_id: Optional[str] = None) -> 'Status':
        """
        Create a warning status.
        
        Args:
            message: Warning message
            device_id: Optional device ID
            
        Returns:
            Status: New warning status instance
        """
        return cls.objects.create(
            execution_status=False,
            message=message,
            status_type='warning',
            device_id=device_id
        )

    @classmethod
    def get_recent_statuses(cls, limit: int = 10) -> 'models.QuerySet[Status]':
        """
        Get recent status entries.
        
        Args:
            limit: Maximum number of statuses to return
            
        Returns:
            QuerySet: Recent status entries
        """
        return cls.objects.all()[:limit]

    @classmethod
    def get_statuses_by_device(cls, device_id: str) -> 'models.QuerySet[Status]':
        """
        Get all statuses for a specific device.
        
        Args:
            device_id: Device identifier
            
        Returns:
            QuerySet: Statuses for the specified device
        """
        return cls.objects.filter(device_id=device_id).order_by('-created_at')