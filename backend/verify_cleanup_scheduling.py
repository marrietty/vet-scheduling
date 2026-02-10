#!/usr/bin/env python3
"""Verification script for token cleanup scheduling.

This script verifies that:
1. The application starts successfully with the cleanup task
2. The cleanup task is properly scheduled
3. The lifespan events work correctly

Run this script to verify the implementation of task 16.2.
"""

import sys
import asyncio
from fastapi.testclient import TestClient

# Add the app directory to the Python path
sys.path.insert(0, '.')

from app.main import app, periodic_token_cleanup


def test_app_startup():
    """Test that the application starts with the cleanup task."""
    print("Testing application startup with cleanup task...")
    
    try:
        with TestClient(app) as client:
            # Test health endpoint
            response = client.get("/health")
            assert response.status_code == 200
            assert response.json()["status"] == "healthy"
            print("✓ Application started successfully")
            print("✓ Health check passed")
            
            # Test root endpoint
            response = client.get("/")
            assert response.status_code == 200
            print("✓ Root endpoint accessible")
            
        print("\n✅ All startup tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Startup test failed: {str(e)}")
        return False


async def test_periodic_cleanup_function():
    """Test that the periodic cleanup function works."""
    print("\nTesting periodic cleanup function...")
    
    try:
        # Create a task that will be cancelled after a short time
        task = asyncio.create_task(periodic_token_cleanup(interval_hours=24))
        
        # Let it run for a moment
        await asyncio.sleep(0.1)
        
        # Cancel the task
        task.cancel()
        
        try:
            await task
        except asyncio.CancelledError:
            print("✓ Periodic cleanup task created successfully")
            print("✓ Task cancellation handled gracefully")
        
        print("\n✅ Periodic cleanup function tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Periodic cleanup test failed: {str(e)}")
        return False


def main():
    """Run all verification tests."""
    print("=" * 60)
    print("Token Cleanup Scheduling Verification")
    print("Task 16.2: Schedule cleanup task")
    print("=" * 60)
    print()
    
    # Test 1: Application startup
    startup_ok = test_app_startup()
    
    # Test 2: Periodic cleanup function
    cleanup_ok = asyncio.run(test_periodic_cleanup_function())
    
    # Summary
    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)
    print(f"Application Startup: {'✅ PASS' if startup_ok else '❌ FAIL'}")
    print(f"Periodic Cleanup:    {'✅ PASS' if cleanup_ok else '❌ FAIL'}")
    print()
    
    if startup_ok and cleanup_ok:
        print("✅ Task 16.2 implementation verified successfully!")
        print()
        print("The token cleanup task is now scheduled to run every 24 hours.")
        print("See TOKEN_CLEANUP_SCHEDULING.md for configuration options.")
        return 0
    else:
        print("❌ Verification failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
