#!/usr/bin/env python3
"""
Create a test user for API authentication testing.

This script creates a test user in the Django database for use in API tests.
"""
import os
import sys
import django

# Add the Django project to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'pycharmtut'))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pycharmtut.test_settings')
django.setup()

from django.contrib.auth.models import User
from django.db import transaction


def create_test_user():
    """Create a test user for API authentication."""
    username = 'testuser'
    password = 'testpass123'
    email = 'test@example.com'
    
    try:
        with transaction.atomic():
            # Check if user already exists
            if User.objects.filter(username=username).exists():
                user = User.objects.get(username=username)
                user.set_password(password)
                user.save()
                print(f"✅ Updated existing test user: {username}")
            else:
                # Create new user
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    is_active=True,
                    is_staff=True,
                    is_superuser=True
                )
                print(f"✅ Created new test user: {username}")
            
            print(f"   Username: {username}")
            print(f"   Password: {password}")
            print(f"   Email: {email}")
            print(f"   Is Staff: {user.is_staff}")
            print(f"   Is Superuser: {user.is_superuser}")
            
            return user
            
    except Exception as e:
        print(f"❌ Error creating test user: {e}")
        return None


def test_authentication():
    """Test that the created user can authenticate."""
    from django.contrib.auth import authenticate
    
    username = 'testuser'
    password = 'testpass123'
    
    user = authenticate(username=username, password=password)
    if user:
        print(f"✅ Authentication test passed for user: {username}")
        return True
    else:
        print(f"❌ Authentication test failed for user: {username}")
        return False


if __name__ == '__main__':
    print("🔐 Creating test user for API authentication...")
    print("=" * 50)
    
    user = create_test_user()
    if user:
        print("\n🧪 Testing authentication...")
        test_authentication()
        
        print("\n📋 Test user credentials:")
        print("   Username: testuser")
        print("   Password: testpass123")
        print("\n💡 Use these credentials in your API tests for authentication.")
    else:
        print("❌ Failed to create test user")
        sys.exit(1)
