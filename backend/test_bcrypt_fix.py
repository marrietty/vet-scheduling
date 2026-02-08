"""
Quick test script to verify bcrypt fix works correctly.
Run this to test password hashing and verification.
"""

import sys
sys.path.insert(0, '.')

from app.infrastructure.auth import hash_password, verify_password, validate_password
from app.common.exceptions import BadRequestException

def test_password_operations():
    """Test password hashing and verification."""
    
    print("=" * 60)
    print("Testing Bcrypt Direct Implementation")
    print("=" * 60)
    
    # Test 1: Valid 8-character password
    print("\n✓ Test 1: Valid 8-character password")
    try:
        password = "12345678"
        hashed = hash_password(password)
        print(f"  Password: {password}")
        print(f"  Hashed: {hashed[:30]}...")
        
        # Verify correct password
        if verify_password(password, hashed):
            print("  ✓ Verification successful")
        else:
            print("  ✗ Verification failed")
            
        # Verify wrong password
        if not verify_password("wrongpass", hashed):
            print("  ✓ Wrong password correctly rejected")
        else:
            print("  ✗ Wrong password incorrectly accepted")
            
    except Exception as e:
        print(f"  ✗ Error: {e}")
    
    # Test 2: Password too short
    print("\n✓ Test 2: Password too short (should fail)")
    try:
        password = "1234567"  # 7 chars
        hashed = hash_password(password)
        print(f"  ✗ Should have failed but didn't")
    except BadRequestException as e:
        print(f"  ✓ Correctly rejected: {e}")
    except Exception as e:
        print(f"  ✗ Unexpected error: {e}")
    
    # Test 3: Password too long
    print("\n✓ Test 3: Password too long (should fail)")
    try:
        password = "a" * 65  # 65 chars
        hashed = hash_password(password)
        print(f"  ✗ Should have failed but didn't")
    except BadRequestException as e:
        print(f"  ✓ Correctly rejected: {e}")
    except Exception as e:
        print(f"  ✗ Unexpected error: {e}")
    
    # Test 4: Valid longer password
    print("\n✓ Test 4: Valid longer password (32 chars)")
    try:
        password = "a" * 32
        hashed = hash_password(password)
        print(f"  Password length: {len(password)} chars")
        print(f"  Hashed: {hashed[:30]}...")
        
        if verify_password(password, hashed):
            print("  ✓ Verification successful")
        else:
            print("  ✗ Verification failed")
            
    except Exception as e:
        print(f"  ✗ Error: {e}")
    
    # Test 5: Multi-byte characters
    print("\n✓ Test 5: Multi-byte characters (emoji)")
    try:
        password = "password🔒123"
        password_bytes = password.encode('utf-8')
        print(f"  Password: {password}")
        print(f"  Length: {len(password)} chars, {len(password_bytes)} bytes")
        
        hashed = hash_password(password)
        print(f"  Hashed: {hashed[:30]}...")
        
        if verify_password(password, hashed):
            print("  ✓ Verification successful")
        else:
            print("  ✗ Verification failed")
            
    except Exception as e:
        print(f"  ✗ Error: {e}")
    
    # Test 6: Edge case - exactly 64 characters
    print("\n✓ Test 6: Edge case - exactly 64 characters")
    try:
        password = "a" * 64
        hashed = hash_password(password)
        print(f"  Password length: {len(password)} chars")
        print(f"  Hashed: {hashed[:30]}...")
        
        if verify_password(password, hashed):
            print("  ✓ Verification successful")
        else:
            print("  ✗ Verification failed")
            
    except Exception as e:
        print(f"  ✗ Error: {e}")
    
    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)

if __name__ == "__main__":
    test_password_operations()
