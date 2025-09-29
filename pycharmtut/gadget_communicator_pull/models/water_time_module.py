"""
Water Time model for water plant automation system.

This module defines the WaterTime model which represents specific watering
times associated with time-based watering plans.
"""
import re
from typing import Optional
from django.db import models
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class WaterTime(models.Model):
    """
    Water time model for scheduled watering.
    
    Represents a specific time and day when watering should occur as part
    of a time-based watering plan. This model allows for flexible scheduling
    with multiple watering times per plan.
    
    Attributes:
        weekday: Day of the week for watering
        time_water: Time to water in HH:MM format
        time_plan: Associated time-based plan
        is_in_use: Whether this time slot is currently active
        created_at: Timestamp when the time was created
        updated_at: Timestamp when the time was last updated
    """
    
    # Weekday choices
    WEEKDAY_CHOICES = [
        (0, _('Monday')),
        (1, _('Tuesday')),
        (2, _('Wednesday')),
        (3, _('Thursday')),
        (4, _('Friday')),
        (5, _('Saturday')),
        (6, _('Sunday')),
    ]
    
    weekday = models.PositiveSmallIntegerField(
        choices=WEEKDAY_CHOICES,
        help_text=_("Day of the week for watering"),
        verbose_name=_("Weekday")
    )
    
    time_water = models.CharField(
        max_length=5,
        help_text=_("Time to water in HH:MM format (24-hour)"),
        verbose_name=_("Watering Time")
    )
    
    time_plan = models.ForeignKey(
        'TimePlan',
        related_name='weekday_times',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text=_("Associated time-based plan"),
        verbose_name=_("Time Plan")
    )
    
    is_in_use = models.BooleanField(
        default=True,
        help_text=_("Whether this time slot is currently active"),
        verbose_name=_("In Use")
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text=_("When this time was created"),
        verbose_name=_("Created At")
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text=_("When this time was last updated"),
        verbose_name=_("Updated At")
    )

    class Meta:
        """Meta options for WaterTime model."""
        verbose_name = _("Water Time")
        verbose_name_plural = _("Water Times")
        ordering = ['weekday', 'time_water']
        unique_together = ['weekday', 'time_water', 'time_plan']
        indexes = [
            models.Index(fields=['weekday']),
            models.Index(fields=['time_water']),
            models.Index(fields=['is_in_use']),
            models.Index(fields=['created_at']),
        ]

    def clean(self) -> None:
        """
        Validate model fields.
        
        Raises:
            ValidationError: If validation fails
        """
        super().clean()
        
        # Validate time format (HH:MM)
        time_pattern = re.compile(r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$')
        if not time_pattern.match(self.time_water):
            raise ValidationError({
                'time_water': _('Time must be in HH:MM format (24-hour)')
            })
        
        # Validate weekday
        if self.weekday not in [choice[0] for choice in self.WEEKDAY_CHOICES]:
            raise ValidationError({
                'weekday': _('Invalid weekday selection')
            })

    def save(self, *args, **kwargs) -> None:
        """Save the model instance with validation."""
        self.full_clean()
        super().save(*args, **kwargs)

    def get_absolute_url(self) -> str:
        """
        Get the absolute URL for this water time.
        
        Returns:
            str: URL for the water time detail view
        """
        return reverse("gadget_communicator_pull:water-info", kwargs={"id": self.id})

    def __str__(self) -> str:
        """
        String representation of the water time.
        
        Returns:
            str: Human-readable representation
        """
        weekday_name = dict(self.WEEKDAY_CHOICES)[self.weekday]
        return f"{weekday_name} at {self.time_water}"

    def __repr__(self) -> str:
        """
        Developer representation of the water time.
        
        Returns:
            str: Developer-friendly representation
        """
        return f"WaterTime(id={self.id}, weekday={self.weekday}, time='{self.time_water}')"

    @property
    def weekday_name(self) -> str:
        """
        Get the weekday name.
        
        Returns:
            str: Name of the weekday
        """
        return dict(self.WEEKDAY_CHOICES)[self.weekday]

    @property
    def is_valid_time(self) -> bool:
        """
        Check if the time is valid.
        
        Returns:
            bool: True if the time is valid
        """
        try:
            hour, minute = map(int, self.time_water.split(':'))
            return 0 <= hour <= 23 and 0 <= minute <= 59
        except (ValueError, AttributeError):
            return False

    def activate(self) -> None:
        """Activate this water time slot."""
        self.is_in_use = True
        self.save(update_fields=['is_in_use', 'updated_at'])

    def deactivate(self) -> None:
        """Deactivate this water time slot."""
        self.is_in_use = False
        self.save(update_fields=['is_in_use', 'updated_at'])

    def get_time_in_minutes(self) -> int:
        """
        Get the time in minutes since midnight.
        
        Returns:
            int: Minutes since midnight
        """
        try:
            hour, minute = map(int, self.time_water.split(':'))
            return hour * 60 + minute
        except (ValueError, AttributeError):
            return 0

    @classmethod
    def get_times_for_weekday(cls, weekday: int) -> 'models.QuerySet[WaterTime]':
        """
        Get all water times for a specific weekday.
        
        Args:
            weekday: Day of the week (0-6)
            
        Returns:
            QuerySet: Water times for the specified weekday
        """
        return cls.objects.filter(weekday=weekday, is_in_use=True)

    @classmethod
    def get_active_times(cls) -> 'models.QuerySet[WaterTime]':
        """
        Get all active water times.
        
        Returns:
            QuerySet: All active water times
        """
        return cls.objects.filter(is_in_use=True).order_by('weekday', 'time_water')
