"""
Unit tests for WaterPlantApp helpers.

This module contains comprehensive unit tests for all helper modules
in the WaterPlantApp Django application.
"""
import pytest
import json
from datetime import datetime, date, time
from decimal import Decimal
from django.test import TestCase
from unittest.mock import Mock, patch

from gadget_communicator_pull.helpers.time_keeper import TimeKeeper
from gadget_communicator_pull.helpers.helper import BitChoices, WEEKDAYS, WEEKDAYS_NUMERIC
from gadget_communicator_pull.helpers.from_to_json_serializer import to_json_serializer, remove_device_field_from_json


class TestTimeKeeper(TestCase):
    """Test cases for TimeKeeper helper."""

    def test_time_keeper_initialization(self):
        """Test TimeKeeper initialization."""
        current_time = datetime.now()
        time_keeper = TimeKeeper(current_time)
        
        self.assertEqual(time_keeper.current_time, current_time)
        self.assertIsNone(time_keeper.time_last_watered)
        self.assertIsNone(time_keeper.date_last_watered)

    def test_time_keeper_setters(self):
        """Test TimeKeeper setter methods."""
        current_time = datetime.now()
        time_keeper = TimeKeeper(current_time)
        
        # Test set_current_time
        new_time = datetime.now()
        time_keeper.set_current_time(new_time)
        self.assertEqual(time_keeper.current_time, new_time)
        
        # Test set_time_last_watered
        water_time = time(9, 0)
        time_keeper.set_time_last_watered(water_time)
        self.assertEqual(time_keeper.time_last_watered, water_time)
        
        # Test set_date_last_watered
        water_date = date.today()
        time_keeper.set_date_last_watered(water_date)
        self.assertEqual(time_keeper.date_last_watered, water_date)

    def test_time_keeper_validation(self):
        """Test TimeKeeper validation methods."""
        current_time = datetime.now()
        time_keeper = TimeKeeper(current_time)
        
        # Test valid time
        self.assertTrue(time_keeper.is_valid_time("09:00"))
        self.assertTrue(time_keeper.is_valid_time("23:59"))
        
        # Test invalid time
        self.assertFalse(time_keeper.is_valid_time("25:00"))
        self.assertFalse(time_keeper.is_valid_time("12:60"))
        self.assertFalse(time_keeper.is_valid_time("invalid"))

    def test_time_keeper_date_validation(self):
        """Test TimeKeeper date validation."""
        current_time = datetime.now()
        time_keeper = TimeKeeper(current_time)
        
        # Test valid date
        self.assertTrue(time_keeper.is_valid_date("2024-01-01"))
        self.assertTrue(time_keeper.is_valid_date("2024-12-31"))
        
        # Test invalid date
        self.assertFalse(time_keeper.is_valid_date("2024-13-01"))
        self.assertFalse(time_keeper.is_valid_date("2024-02-30"))
        self.assertFalse(time_keeper.is_valid_date("invalid"))


class TestBitChoices(TestCase):
    """Test cases for BitChoices utility class."""

    def test_bitchoices_initialization(self):
        """Test BitChoices initialization."""
        choices = [('option1', 'Option 1'), ('option2', 'Option 2')]
        bit_choices = BitChoices(choices)
        self.assertIsNotNone(bit_choices)

    def test_bitchoices_iteration(self):
        """Test BitChoices iteration."""
        choices = [('option1', 'Option 1'), ('option2', 'Option 2')]
        bit_choices = BitChoices(choices)
        
        # Test iteration
        for choice in bit_choices:
            self.assertIsInstance(choice, tuple)
            self.assertEqual(len(choice), 2)

    def test_bitchoices_length(self):
        """Test BitChoices length."""
        choices = [('option1', 'Option 1'), ('option2', 'Option 2')]
        bit_choices = BitChoices(choices)
        self.assertEqual(len(bit_choices), 2)

    def test_bitchoices_attribute_access(self):
        """Test BitChoices attribute access."""
        choices = [('option1', 'Option 1'), ('option2', 'Option 2')]
        bit_choices = BitChoices(choices)
        
        # Test attribute access
        self.assertEqual(bit_choices.option1, 1)  # 2^0
        self.assertEqual(bit_choices.option2, 2)  # 2^1

    def test_weekdays_constants(self):
        """Test WEEKDAYS constants."""
        # Test WEEKDAYS
        self.assertIsNotNone(WEEKDAYS)
        self.assertEqual(len(WEEKDAYS), 7)
        
        # Test WEEKDAYS_NUMERIC
        self.assertIsNotNone(WEEKDAYS_NUMERIC)
        self.assertEqual(len(WEEKDAYS_NUMERIC), 7)
        self.assertEqual(WEEKDAYS_NUMERIC['Monday'], 1)
        self.assertEqual(WEEKDAYS_NUMERIC['Sunday'], 64)


class TestJSONSerializer(TestCase):
    """Test cases for JSON serializer functions."""

    def test_to_json_serializer(self):
        """Test to_json_serializer function."""
        # Mock serializer with data
        mock_serializer = Mock()
        mock_serializer.data = {'test': 'data', 'number': 123}
        
        # Test serialization
        result = to_json_serializer(mock_serializer)
        self.assertEqual(result, {'test': 'data', 'number': 123})

    def test_remove_device_field_from_json(self):
        """Test remove_device_field_from_json function."""
        # Test with device field
        json_obj = {'device': 'test', 'other': 'data'}
        result = remove_device_field_from_json(json_obj)
        self.assertNotIn('device', result)
        self.assertIn('other', result)
        
        # Test without device field
        json_obj = {'other': 'data'}
        result = remove_device_field_from_json(json_obj)
        self.assertEqual(result, {'other': 'data'})


class TestHelperIntegration(TestCase):
    """Test cases for helper integration."""

    def test_time_keeper_integration(self):
        """Test TimeKeeper integration with other components."""
        current_time = datetime.now()
        time_keeper = TimeKeeper(current_time)
        
        # Test integration
        self.assertIsNotNone(time_keeper)
        self.assertTrue(hasattr(time_keeper, 'current_time'))

    def test_bitchoices_integration(self):
        """Test BitChoices integration."""
        choices = [('test', 'Test')]
        bit_choices = BitChoices(choices)
        
        # Test integration
        self.assertIsNotNone(bit_choices)
        self.assertEqual(bit_choices.test, 1)

    def test_json_serializer_integration(self):
        """Test JSON serializer integration."""
        # Test integration
        mock_serializer = Mock()
        mock_serializer.data = {'test': 'data'}
        
        result = to_json_serializer(mock_serializer)
        self.assertEqual(result, {'test': 'data'})