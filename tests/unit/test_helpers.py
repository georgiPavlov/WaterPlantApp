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
from gadget_communicator_pull.helpers.helper import Helper
from gadget_communicator_pull.helpers.from_to_json_serializer import JSONSerializer


class TestTimeKeeper(TestCase):
    """Test cases for TimeKeeper helper."""
    
    def test_time_keeper_initialization(self):
        """Test TimeKeeper initialization."""
        time_keeper = TimeKeeper()
        
        # Should have current time
        self.assertIsNotNone(time_keeper.current_time)
        self.assertIsInstance(time_keeper.current_time, time)
    
    def test_time_keeper_with_custom_time(self):
        """Test TimeKeeper with custom time."""
        custom_time = time(14, 30, 0)
        time_keeper = TimeKeeper(custom_time)
        
        self.assertEqual(time_keeper.current_time, custom_time)
    
    def test_get_current_time(self):
        """Test getting current time."""
        time_keeper = TimeKeeper()
        current_time = time_keeper.get_current_time()
        
        self.assertIsInstance(current_time, time)
        self.assertIsNotNone(current_time)
    
    def test_get_current_date(self):
        """Test getting current date."""
        time_keeper = TimeKeeper()
        current_date = time_keeper.get_current_date()
        
        self.assertIsInstance(current_date, date)
        self.assertEqual(current_date, date.today())
    
    def test_get_current_datetime(self):
        """Test getting current datetime."""
        time_keeper = TimeKeeper()
        current_datetime = time_keeper.get_current_datetime()
        
        self.assertIsInstance(current_datetime, datetime)
        self.assertIsNotNone(current_datetime)
    
    def test_time_operations(self):
        """Test time operations."""
        time_keeper = TimeKeeper()
        
        # Test time addition
        result = time_keeper.add_time(time(10, 0, 0), 30)  # Add 30 minutes
        self.assertEqual(result, time(10, 30, 0))
        
        # Test time subtraction
        result = time_keeper.subtract_time(time(10, 30, 0), 30)  # Subtract 30 minutes
        self.assertEqual(result, time(10, 0, 0))
        
        # Test time difference
        diff = time_keeper.get_time_difference(time(10, 0, 0), time(11, 30, 0))
        self.assertEqual(diff, 90)  # 90 minutes
    
    def test_date_operations(self):
        """Test date operations."""
        time_keeper = TimeKeeper()
        
        # Test date addition
        result = time_keeper.add_days(date(2023, 1, 1), 7)
        self.assertEqual(result, date(2023, 1, 8))
        
        # Test date subtraction
        result = time_keeper.subtract_days(date(2023, 1, 8), 7)
        self.assertEqual(result, date(2023, 1, 1))
        
        # Test date difference
        diff = time_keeper.get_date_difference(date(2023, 1, 1), date(2023, 1, 8))
        self.assertEqual(diff, 7)  # 7 days
    
    def test_time_formatting(self):
        """Test time formatting."""
        time_keeper = TimeKeeper()
        
        # Test time to string
        time_str = time_keeper.time_to_string(time(14, 30, 0))
        self.assertEqual(time_str, "14:30:00")
        
        # Test string to time
        parsed_time = time_keeper.string_to_time("14:30:00")
        self.assertEqual(parsed_time, time(14, 30, 0))
    
    def test_date_formatting(self):
        """Test date formatting."""
        time_keeper = TimeKeeper()
        
        # Test date to string
        date_str = time_keeper.date_to_string(date(2023, 1, 15))
        self.assertEqual(date_str, "2023-01-15")
        
        # Test string to date
        parsed_date = time_keeper.string_to_date("2023-01-15")
        self.assertEqual(parsed_date, date(2023, 1, 15))
    
    def test_weekday_operations(self):
        """Test weekday operations."""
        time_keeper = TimeKeeper()
        
        # Test getting weekday name
        weekday_name = time_keeper.get_weekday_name(date(2023, 1, 2))  # Monday
        self.assertEqual(weekday_name, "monday")
        
        # Test getting weekday number
        weekday_num = time_keeper.get_weekday_number("monday")
        self.assertEqual(weekday_num, 0)
        
        # Test getting weekday from number
        weekday_name = time_keeper.get_weekday_from_number(0)
        self.assertEqual(weekday_name, "monday")
    
    def test_time_validation(self):
        """Test time validation."""
        time_keeper = TimeKeeper()
        
        # Test valid time
        self.assertTrue(time_keeper.is_valid_time(time(14, 30, 0)))
        
        # Test invalid time (should not raise exception, just return False)
        self.assertFalse(time_keeper.is_valid_time("invalid"))
    
    def test_date_validation(self):
        """Test date validation."""
        time_keeper = TimeKeeper()
        
        # Test valid date
        self.assertTrue(time_keeper.is_valid_date(date(2023, 1, 15)))
        
        # Test invalid date (should not raise exception, just return False)
        self.assertFalse(time_keeper.is_valid_date("invalid"))


class TestHelper(TestCase):
    """Test cases for Helper utility class."""
    
    def test_helper_initialization(self):
        """Test Helper initialization."""
        helper = Helper()
        self.assertIsNotNone(helper)
    
    def test_validate_email(self):
        """Test email validation."""
        helper = Helper()
        
        # Test valid emails
        self.assertTrue(helper.validate_email("test@example.com"))
        self.assertTrue(helper.validate_email("user.name@domain.co.uk"))
        self.assertTrue(helper.validate_email("test+tag@example.org"))
        
        # Test invalid emails
        self.assertFalse(helper.validate_email("invalid-email"))
        self.assertFalse(helper.validate_email("@example.com"))
        self.assertFalse(helper.validate_email("test@"))
        self.assertFalse(helper.validate_email(""))
        self.assertFalse(helper.validate_email(None))
    
    def test_validate_phone(self):
        """Test phone number validation."""
        helper = Helper()
        
        # Test valid phone numbers
        self.assertTrue(helper.validate_phone("+1234567890"))
        self.assertTrue(helper.validate_phone("123-456-7890"))
        self.assertTrue(helper.validate_phone("(123) 456-7890"))
        self.assertTrue(helper.validate_phone("123.456.7890"))
        
        # Test invalid phone numbers
        self.assertFalse(helper.validate_phone("123"))
        self.assertFalse(helper.validate_phone("abc-def-ghij"))
        self.assertFalse(helper.validate_phone(""))
        self.assertFalse(helper.validate_phone(None))
    
    def test_validate_url(self):
        """Test URL validation."""
        helper = Helper()
        
        # Test valid URLs
        self.assertTrue(helper.validate_url("https://example.com"))
        self.assertTrue(helper.validate_url("http://example.com"))
        self.assertTrue(helper.validate_url("https://subdomain.example.com/path"))
        self.assertTrue(helper.validate_url("https://example.com:8080/path?param=value"))
        
        # Test invalid URLs
        self.assertFalse(helper.validate_url("not-a-url"))
        self.assertFalse(helper.validate_url("ftp://example.com"))
        self.assertFalse(helper.validate_url(""))
        self.assertFalse(helper.validate_url(None))
    
    def test_sanitize_string(self):
        """Test string sanitization."""
        helper = Helper()
        
        # Test string sanitization
        result = helper.sanitize_string("  Hello World  ")
        self.assertEqual(result, "Hello World")
        
        result = helper.sanitize_string("\n\tTest String\n\t")
        self.assertEqual(result, "Test String")
        
        result = helper.sanitize_string("")
        self.assertEqual(result, "")
        
        result = helper.sanitize_string(None)
        self.assertEqual(result, "")
    
    def test_format_number(self):
        """Test number formatting."""
        helper = Helper()
        
        # Test number formatting
        result = helper.format_number(1234.5678, 2)
        self.assertEqual(result, "1,234.57")
        
        result = helper.format_number(1234.5678, 0)
        self.assertEqual(result, "1,235")
        
        result = helper.format_number(0, 2)
        self.assertEqual(result, "0.00")
        
        result = helper.format_number(-1234.5678, 2)
        self.assertEqual(result, "-1,234.57")
    
    def test_generate_random_string(self):
        """Test random string generation."""
        helper = Helper()
        
        # Test random string generation
        result = helper.generate_random_string(10)
        self.assertEqual(len(result), 10)
        self.assertTrue(result.isalnum())
        
        result = helper.generate_random_string(5)
        self.assertEqual(len(result), 5)
        
        result = helper.generate_random_string(0)
        self.assertEqual(len(result), 0)
    
    def test_calculate_percentage(self):
        """Test percentage calculation."""
        helper = Helper()
        
        # Test percentage calculation
        result = helper.calculate_percentage(25, 100)
        self.assertEqual(result, 25.0)
        
        result = helper.calculate_percentage(50, 200)
        self.assertEqual(result, 25.0)
        
        result = helper.calculate_percentage(0, 100)
        self.assertEqual(result, 0.0)
        
        result = helper.calculate_percentage(100, 100)
        self.assertEqual(result, 100.0)
        
        # Test division by zero
        result = helper.calculate_percentage(50, 0)
        self.assertEqual(result, 0.0)
    
    def test_convert_units(self):
        """Test unit conversion."""
        helper = Helper()
        
        # Test volume conversion (ml to liters)
        result = helper.convert_ml_to_liters(1000)
        self.assertEqual(result, 1.0)
        
        result = helper.convert_ml_to_liters(500)
        self.assertEqual(result, 0.5)
        
        result = helper.convert_ml_to_liters(0)
        self.assertEqual(result, 0.0)
        
        # Test temperature conversion (Celsius to Fahrenheit)
        result = helper.convert_celsius_to_fahrenheit(0)
        self.assertEqual(result, 32.0)
        
        result = helper.convert_celsius_to_fahrenheit(100)
        self.assertEqual(result, 212.0)
        
        result = helper.convert_celsius_to_fahrenheit(-40)
        self.assertEqual(result, -40.0)  # Same in both scales


class TestJSONSerializer(TestCase):
    """Test cases for JSONSerializer helper."""
    
    def test_json_serializer_initialization(self):
        """Test JSONSerializer initialization."""
        serializer = JSONSerializer()
        self.assertIsNotNone(serializer)
    
    def test_serialize_to_json(self):
        """Test serialization to JSON."""
        serializer = JSONSerializer()
        
        # Test simple object serialization
        data = {"name": "Test", "value": 123}
        result = serializer.serialize_to_json(data)
        self.assertIsInstance(result, str)
        
        # Parse back to verify
        parsed = json.loads(result)
        self.assertEqual(parsed["name"], "Test")
        self.assertEqual(parsed["value"], 123)
    
    def test_deserialize_from_json(self):
        """Test deserialization from JSON."""
        serializer = JSONSerializer()
        
        # Test valid JSON
        json_str = '{"name": "Test", "value": 123}'
        result = serializer.deserialize_from_json(json_str)
        self.assertEqual(result["name"], "Test")
        self.assertEqual(result["value"], 123)
        
        # Test invalid JSON
        invalid_json = '{"name": "Test", "value": 123'  # Missing closing brace
        result = serializer.deserialize_from_json(invalid_json)
        self.assertIsNone(result)
    
    def test_serialize_datetime(self):
        """Test datetime serialization."""
        serializer = JSONSerializer()
        
        # Test datetime serialization
        dt = datetime(2023, 1, 15, 14, 30, 0)
        data = {"timestamp": dt}
        result = serializer.serialize_to_json(data)
        
        # Parse back to verify
        parsed = json.loads(result)
        self.assertIn("timestamp", parsed)
    
    def test_serialize_decimal(self):
        """Test decimal serialization."""
        serializer = JSONSerializer()
        
        # Test decimal serialization
        decimal_val = Decimal("123.45")
        data = {"price": decimal_val}
        result = serializer.serialize_to_json(data)
        
        # Parse back to verify
        parsed = json.loads(result)
        self.assertEqual(float(parsed["price"]), 123.45)
    
    def test_serialize_nested_objects(self):
        """Test nested object serialization."""
        serializer = JSONSerializer()
        
        # Test nested object serialization
        data = {
            "user": {
                "name": "John Doe",
                "email": "john@example.com",
                "preferences": {
                    "theme": "dark",
                    "notifications": True
                }
            },
            "items": [1, 2, 3, 4, 5]
        }
        
        result = serializer.serialize_to_json(data)
        parsed = json.loads(result)
        
        self.assertEqual(parsed["user"]["name"], "John Doe")
        self.assertEqual(parsed["user"]["preferences"]["theme"], "dark")
        self.assertEqual(parsed["items"], [1, 2, 3, 4, 5])
    
    def test_serialize_with_custom_encoder(self):
        """Test serialization with custom encoder."""
        serializer = JSONSerializer()
        
        # Test with custom encoder
        class CustomEncoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, set):
                    return list(obj)
                return super().default(obj)
        
        data = {"tags": {"python", "django", "testing"}}
        result = serializer.serialize_to_json(data, encoder=CustomEncoder)
        parsed = json.loads(result)
        
        self.assertIsInstance(parsed["tags"], list)
        self.assertEqual(len(parsed["tags"]), 3)
    
    def test_validate_json(self):
        """Test JSON validation."""
        serializer = JSONSerializer()
        
        # Test valid JSON
        valid_json = '{"name": "Test", "value": 123}'
        self.assertTrue(serializer.validate_json(valid_json))
        
        # Test invalid JSON
        invalid_json = '{"name": "Test", "value": 123'  # Missing closing brace
        self.assertFalse(serializer.validate_json(invalid_json))
        
        # Test empty string
        self.assertFalse(serializer.validate_json(""))
        
        # Test None
        self.assertFalse(serializer.validate_json(None))
    
    def test_pretty_print_json(self):
        """Test pretty printing JSON."""
        serializer = JSONSerializer()
        
        data = {"name": "Test", "value": 123, "nested": {"key": "value"}}
        result = serializer.pretty_print_json(data)
        
        self.assertIsInstance(result, str)
        # Should contain newlines and indentation
        self.assertIn("\n", result)
        self.assertIn("  ", result)  # Indentation
    
    def test_serialize_with_error_handling(self):
        """Test serialization with error handling."""
        serializer = JSONSerializer()
        
        # Test with non-serializable object
        class NonSerializable:
            def __init__(self):
                self.func = lambda x: x
        
        data = {"obj": NonSerializable()}
        result = serializer.serialize_to_json(data)
        
        # Should handle error gracefully
        self.assertIsNone(result)
    
    def test_deserialize_with_error_handling(self):
        """Test deserialization with error handling."""
        serializer = JSONSerializer()
        
        # Test with malformed JSON
        malformed_json = '{"name": "Test", "value": 123'  # Missing closing brace
        result = serializer.deserialize_from_json(malformed_json)
        
        # Should handle error gracefully
        self.assertIsNone(result)
        
        # Test with empty string
        result = serializer.deserialize_from_json("")
        self.assertIsNone(result)
        
        # Test with None
        result = serializer.deserialize_from_json(None)
        self.assertIsNone(result)


class TestHelperIntegration(TestCase):
    """Test cases for helper integration and edge cases."""
    
    def test_time_keeper_with_helper_integration(self):
        """Test TimeKeeper integration with Helper."""
        time_keeper = TimeKeeper()
        helper = Helper()
        
        # Test time formatting with helper
        current_time = time_keeper.get_current_time()
        time_str = time_keeper.time_to_string(current_time)
        
        # Validate time string format
        self.assertTrue(helper.validate_time_format(time_str))
    
    def test_json_serializer_with_time_keeper(self):
        """Test JSONSerializer with TimeKeeper data."""
        time_keeper = TimeKeeper()
        serializer = JSONSerializer()
        
        # Test serializing time keeper data
        data = {
            "current_time": time_keeper.get_current_time(),
            "current_date": time_keeper.get_current_date(),
            "timestamp": time_keeper.get_current_datetime()
        }
        
        result = serializer.serialize_to_json(data)
        self.assertIsNotNone(result)
        
        # Parse back to verify
        parsed = serializer.deserialize_from_json(result)
        self.assertIsNotNone(parsed)
    
    def test_helper_validation_integration(self):
        """Test Helper validation methods integration."""
        helper = Helper()
        
        # Test email validation with sanitized input
        email = "  test@example.com  "
        sanitized_email = helper.sanitize_string(email)
        self.assertTrue(helper.validate_email(sanitized_email))
        
        # Test phone validation with formatted input
        phone = "123-456-7890"
        self.assertTrue(helper.validate_phone(phone))
        
        # Test URL validation
        url = "https://example.com"
        self.assertTrue(helper.validate_url(url))
    
    def test_edge_cases(self):
        """Test edge cases for all helpers."""
        time_keeper = TimeKeeper()
        helper = Helper()
        serializer = JSONSerializer()
        
        # Test TimeKeeper edge cases
        midnight = time(0, 0, 0)
        result = time_keeper.add_time(midnight, 1440)  # Add 24 hours
        self.assertEqual(result, time(0, 0, 0))
        
        # Test Helper edge cases
        result = helper.calculate_percentage(0, 0)
        self.assertEqual(result, 0.0)
        
        result = helper.generate_random_string(-1)
        self.assertEqual(len(result), 0)
        
        # Test JSONSerializer edge cases
        result = serializer.serialize_to_json({})
        self.assertEqual(result, "{}")
        
        result = serializer.deserialize_from_json("{}")
        self.assertEqual(result, {})
    
    def test_performance_considerations(self):
        """Test performance considerations for helpers."""
        time_keeper = TimeKeeper()
        helper = Helper()
        serializer = JSONSerializer()
        
        # Test large data serialization
        large_data = {"items": list(range(1000))}
        result = serializer.serialize_to_json(large_data)
        self.assertIsNotNone(result)
        
        # Test multiple time operations
        for i in range(100):
            result = time_keeper.add_time(time(10, 0, 0), i)
            self.assertIsNotNone(result)
        
        # Test multiple string operations
        for i in range(100):
            result = helper.sanitize_string(f"  test string {i}  ")
            self.assertIsNotNone(result)
