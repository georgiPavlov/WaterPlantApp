"""
Basic Plan model for water plant automation system.

This module defines the BasicPlan model which represents simple watering plans
that execute a fixed volume of water without complex scheduling or conditions.
"""
from typing import Optional
from django.db import models
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class BasicPlan(models.Model):
    """
    Basic watering plan model.
    
    Represents a simple watering plan that delivers a fixed volume of water
    when executed. This is the simplest type of watering plan available.
    
    Attributes:
        name: Unique name for the plan
        plan_type: Type of plan (should be 'basic')
        water_volume: Volume of water to deliver in milliliters
        has_been_executed: Whether this plan has been executed
        created_at: Timestamp when the plan was created
        updated_at: Timestamp when the plan was last updated
    """
    
    # Plan type choices
    PLAN_TYPE_CHOICES = [
        ('basic', _('Basic Plan')),
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
        default='basic',
        help_text=_("Type of watering plan"),
        verbose_name=_("Plan Type")
    )
    
    water_volume = models.PositiveIntegerField(
        default=100,
        help_text=_("Volume of water to deliver in milliliters (50-2000ml)"),
        verbose_name=_("Water Volume (ml)")
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
        """Meta options for BasicPlan model."""
        verbose_name = _("Basic Plan")
        verbose_name_plural = _("Basic Plans")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['plan_type']),
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
        if self.plan_type != 'basic':
            raise ValidationError({
                'plan_type': _('Plan type must be "basic" for BasicPlan')
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
        return reverse("gadget_communicator_pull:basic-plan", kwargs={"id": self.id})

    def __str__(self) -> str:
        """
        String representation of the plan.
        
        Returns:
            str: Human-readable representation
        """
        return f"BasicPlan: {self.name} ({self.water_volume}ml)"

    def __repr__(self) -> str:
        """
        Developer representation of the plan.
        
        Returns:
            str: Developer-friendly representation
        """
        return f"BasicPlan(id={self.id}, name='{self.name}', volume={self.water_volume}ml)"

    @property
    def is_executable(self) -> bool:
        """
        Check if the plan can be executed.
        
        Returns:
            bool: True if the plan can be executed
        """
        return not self.has_been_executed and self.water_volume > 0

    def mark_as_executed(self) -> None:
        """Mark the plan as executed."""
        self.has_been_executed = True
        self.save(update_fields=['has_been_executed', 'updated_at'])

    def reset_execution_status(self) -> None:
        """Reset the execution status of the plan."""
        self.has_been_executed = False
        self.save(update_fields=['has_been_executed', 'updated_at'])
