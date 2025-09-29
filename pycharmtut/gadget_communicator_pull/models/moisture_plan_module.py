"""
Moisture Plan model for water plant automation system.

This module defines the MoisturePlan model which represents intelligent watering
plans that monitor soil moisture levels and water plants when moisture drops
below a specified threshold.
"""
from typing import Optional
from django.db import models
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class MoisturePlan(models.Model):
    """
    Moisture-based watering plan model.
    
    Represents an intelligent watering plan that monitors soil moisture levels
    and automatically waters plants when moisture drops below a specified threshold.
    This plan type provides smart, condition-based watering.
    
    Attributes:
        name: Unique name for the plan
        plan_type: Type of plan (should be 'moisture')
        water_volume: Volume of water to deliver in milliliters
        moisture_threshold: Moisture level threshold (0.0-1.0)
        check_interval: Interval between moisture checks in minutes
        is_running: Whether the plan is currently active
        has_been_executed: Whether this plan has been executed
        created_at: Timestamp when the plan was created
        updated_at: Timestamp when the plan was last updated
    """
    
    # Plan type choices
    PLAN_TYPE_CHOICES = [
        ('moisture', _('Moisture Plan')),
    ]
    
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text=_("Unique name for the watering plan"),
        verbose_name=_("Plan Name")
    )
    
    plan_type = models.CharField(
        max_length=20,
        choices=PLAN_TYPE_CHOICES,
        default='moisture',
        help_text=_("Type of watering plan"),
        verbose_name=_("Plan Type")
    )
    
    water_volume = models.PositiveIntegerField(
        default=150,
        help_text=_("Volume of water to deliver in milliliters (50-2000ml)"),
        verbose_name=_("Water Volume (ml)")
    )
    
    moisture_threshold = models.FloatField(
        default=0.4,
        help_text=_("Moisture threshold for watering (0.0-1.0, where 0.4 = 40%)"),
        verbose_name=_("Moisture Threshold")
    )
    
    check_interval = models.PositiveIntegerField(
        default=30,
        help_text=_("Interval between moisture checks in minutes (5-1440)"),
        verbose_name=_("Check Interval (minutes)")
    )
    
    is_running = models.BooleanField(
        default=False,
        help_text=_("Whether the plan is currently active"),
        verbose_name=_("Running")
    )
    
    has_been_executed = models.BooleanField(
        default=False,
        help_text=_("Whether this plan has been executed"),
        verbose_name=_("Executed")
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text=_("When this plan was created"),
        verbose_name=_("Created At")
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text=_("When this plan was last updated"),
        verbose_name=_("Updated At")
    )

    class Meta:
        """Meta options for MoisturePlan model."""
        verbose_name = _("Moisture Plan")
        verbose_name_plural = _("Moisture Plans")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['plan_type']),
            models.Index(fields=['is_running']),
            models.Index(fields=['has_been_executed']),
            models.Index(fields=['created_at']),
        ]

    def clean(self) -> None:
        """
        Validate model fields.
        
        Raises:
            ValidationError: If validation fails
        """
        super().clean()
        
        # Validate water volume
        if self.water_volume < 50:
            raise ValidationError({
                'water_volume': _('Water volume must be at least 50ml')
            })
        
        if self.water_volume > 2000:
            raise ValidationError({
                'water_volume': _('Water volume cannot exceed 2000ml')
            })
        
        # Validate moisture threshold
        if self.moisture_threshold < 0.1:
            raise ValidationError({
                'moisture_threshold': _('Moisture threshold must be at least 0.1 (10%)')
            })
        
        if self.moisture_threshold > 1.0:
            raise ValidationError({
                'moisture_threshold': _('Moisture threshold cannot exceed 1.0 (100%)')
            })
        
        # Validate check interval
        if self.check_interval < 5:
            raise ValidationError({
                'check_interval': _('Check interval must be at least 5 minutes')
            })
        
        if self.check_interval > 1440:  # 24 hours
            raise ValidationError({
                'check_interval': _('Check interval cannot exceed 1440 minutes (24 hours)')
            })
        
        # Validate plan type
        if self.plan_type != 'moisture':
            raise ValidationError({
                'plan_type': _('Plan type must be "moisture" for MoisturePlan')
            })

    def save(self, *args, **kwargs) -> None:
        """Save the model instance with validation."""
        self.full_clean()
        super().save(*args, **kwargs)

    def get_absolute_url(self) -> str:
        """
        Get the absolute URL for this plan.
        
        Returns:
            str: URL for the plan detail view
        """
        return reverse("gadget_communicator_pull:moisture-plan", kwargs={"id": self.id})

    def __str__(self) -> str:
        """
        String representation of the plan.
        
        Returns:
            str: Human-readable representation
        """
        return f"MoisturePlan: {self.name} (threshold: {self.moisture_threshold:.1%}, {self.water_volume}ml)"

    def __repr__(self) -> str:
        """
        Developer representation of the plan.
        
        Returns:
            str: Developer-friendly representation
        """
        return (f"MoisturePlan(id={self.id}, name='{self.name}', "
                f"threshold={self.moisture_threshold:.1%}, volume={self.water_volume}ml)")

    @property
    def is_executable(self) -> bool:
        """
        Check if the plan can be executed.
        
        Returns:
            bool: True if the plan can be executed
        """
        return (not self.has_been_executed and 
                self.water_volume > 0 and 
                0.1 <= self.moisture_threshold <= 1.0)

    @property
    def moisture_threshold_percentage(self) -> float:
        """
        Get moisture threshold as percentage.
        
        Returns:
            float: Moisture threshold as percentage (0-100)
        """
        return self.moisture_threshold * 100

    def start_plan(self) -> None:
        """Start the moisture monitoring plan."""
        self.is_running = True
        self.save(update_fields=['is_running', 'updated_at'])

    def stop_plan(self) -> None:
        """Stop the moisture monitoring plan."""
        self.is_running = False
        self.save(update_fields=['is_running', 'updated_at'])

    def mark_as_executed(self) -> None:
        """Mark the plan as executed."""
        self.has_been_executed = True
        self.save(update_fields=['has_been_executed', 'updated_at'])

    def reset_execution_status(self) -> None:
        """Reset the execution status of the plan."""
        self.has_been_executed = False
        self.save(update_fields=['has_been_executed', 'updated_at'])

    def should_water(self, current_moisture: float) -> bool:
        """
        Check if watering should be triggered based on current moisture.
        
        Args:
            current_moisture: Current moisture level (0.0-1.0)
            
        Returns:
            bool: True if watering should be triggered
        """
        return current_moisture < self.moisture_threshold
