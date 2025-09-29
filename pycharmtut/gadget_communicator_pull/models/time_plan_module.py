"""
Time Plan model for water plant automation system.

This module defines the TimePlan model which represents scheduled watering
plans that water plants at specific times and days of the week.
"""
from typing import List, Optional
from django.db import models
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class TimePlan(models.Model):
    """
    Time-based watering plan model.
    
    Represents a scheduled watering plan that waters plants at specific times
    and days of the week. This plan type provides automated, time-based watering
    with flexible scheduling options.
    
    Attributes:
        name: Unique name for the plan
        plan_type: Type of plan (should be 'time_based')
        water_volume: Volume of water to deliver in milliliters
        execute_only_once: Whether the plan should execute only once
        is_running: Whether the plan is currently active
        has_been_executed: Whether this plan has been executed
        created_at: Timestamp when the plan was created
        updated_at: Timestamp when the plan was last updated
    """
    
    # Plan type choices
    PLAN_TYPE_CHOICES = [
        ('time_based', _('Time-based Plan')),
    ]
    
    # Weekday choices
    WEEKDAY_CHOICES = [
        ('Monday', _('Monday')),
        ('Tuesday', _('Tuesday')),
        ('Wednesday', _('Wednesday')),
        ('Thursday', _('Thursday')),
        ('Friday', _('Friday')),
        ('Saturday', _('Saturday')),
        ('Sunday', _('Sunday')),
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
        default='time_based',
        help_text=_("Type of watering plan"),
        verbose_name=_("Plan Type")
    )
    
    water_volume = models.PositiveIntegerField(
        default=180,
        help_text=_("Volume of water to deliver in milliliters (50-2000ml)"),
        verbose_name=_("Water Volume (ml)")
    )
    
    execute_only_once = models.BooleanField(
        default=False,
        help_text=_("Whether the plan should execute only once"),
        verbose_name=_("Execute Only Once")
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
        """Meta options for TimePlan model."""
        verbose_name = _("Time Plan")
        verbose_name_plural = _("Time Plans")
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
        
        # Validate plan type
        if self.plan_type != 'time_based':
            raise ValidationError({
                'plan_type': _('Plan type must be "time_based" for TimePlan')
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
        return reverse("gadget_communicator_pull:time-plan", kwargs={"id": self.id})

    def __str__(self) -> str:
        """
        String representation of the plan.
        
        Returns:
            str: Human-readable representation
        """
        return f"TimePlan: {self.name} ({self.water_volume}ml)"

    def __repr__(self) -> str:
        """
        Developer representation of the plan.
        
        Returns:
            str: Developer-friendly representation
        """
        return f"TimePlan(id={self.id}, name='{self.name}', volume={self.water_volume}ml)"

    @property
    def is_executable(self) -> bool:
        """
        Check if the plan can be executed.
        
        Returns:
            bool: True if the plan can be executed
        """
        return (not self.has_been_executed and 
                self.water_volume > 0)

    def start_plan(self) -> None:
        """Start the time-based plan."""
        self.is_running = True
        self.save(update_fields=['is_running', 'updated_at'])

    def stop_plan(self) -> None:
        """Stop the time-based plan."""
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

    def get_weekday_times(self) -> List[dict]:
        """
        Get all scheduled times for this plan.
        
        Returns:
            List[dict]: List of scheduled times with weekday and time
        """
        return list(self.weekday_times.values('weekday', 'time_water'))

    def add_weekday_time(self, weekday: str, time_water: str) -> None:
        """
        Add a scheduled time for a specific weekday.
        
        Args:
            weekday: Day of the week
            time_water: Time to water (HH:MM format)
        """
        from .water_time_module import WaterTime
        WaterTime.objects.create(
            time_plan=self,
            weekday=weekday,
            time_water=time_water
        )

    def remove_weekday_time(self, weekday: str, time_water: str) -> None:
        """
        Remove a scheduled time for a specific weekday.
        
        Args:
            weekday: Day of the week
            time_water: Time to water (HH:MM format)
        """
        from .water_time_module import WaterTime
        WaterTime.objects.filter(
            time_plan=self,
            weekday=weekday,
            time_water=time_water
        ).delete()