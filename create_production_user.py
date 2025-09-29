#!/usr/bin/env python3
"""
Create a production user for API authentication.

This script creates a user in the main Django database (not test database) for use in production.
"""
import os
import sys
import django

# Add the Django project to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'pycharmtut'))

# Set up Django with main settings (not test settings)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pycharmtut.settings')
django.setup()

from django.contrib.auth.models import User
from django.db import transaction


def create_production_user():
    """Create a production user for API authentication."""
    username = 'testuser'
    password = 'testpass123'
    email = 'test@example.com'
    
    try:
        with transaction.atomic():
            # Check if user already exists
            if User.objects.filter(username=username).exists():
                user = User.objects.get(username=username)
                user.set_password(password)
                user.is_active = True
                user.is_staff = True
                user.is_superuser = True
                user.save()
                print(f"✅ Updated existing production user: {username}")
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
                print(f"✅ Created new production user: {username}")
            
            print(f"   Username: {username}")
            print(f"   Password: {password}")
            print(f"   Email: {email}")
            print(f"   Is Active: {user.is_active}")
            print(f"   Is Staff: {user.is_staff}")
            print(f"   Is Superuser: {user.is_superuser}")
            
            return user
            
    except Exception as e:
        print(f"❌ Error creating production user: {e}")
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
    print("🔐 Creating production user for API authentication...")
    print("=" * 50)
    
    user = create_production_user()
    if user:
        print("\n🧪 Testing authentication...")
        test_authentication()
        
        print("\n📋 Production user credentials:")
        print("   Username: testuser")
        print("   Password: testpass123")
        print("\n💡 Use these credentials in your production API tests.")
    else:
        print("❌ Failed to create production user")
        sys.exit(1)
