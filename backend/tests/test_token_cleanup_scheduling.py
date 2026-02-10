"""Integration tests for token cleanup scheduling.

This module tests that the token cleanup background task is properly
scheduled and integrated into the FastAPI application lifespan.

Requirements:
    - 7.3: Provide mechanism to periodically remove expired tokens
"""

import pytest
import asyncio
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from app.main import app, periodic_token_cleanup


class TestTokenCleanupScheduling:
    """Test token cleanup task scheduling."""
    
    def test_app_starts_with_cleanup_task(self):
        """Test that the application starts successfully with the cleanup task.
        
        This test verifies that the FastAPI application can start with the
        background cleanup task without errors.
        
        Requirements: 7.3
        """
        # Act: Create a test client (this triggers the lifespan context)
        with TestClient(app) as client:
            # Assert: Application starts successfully
            response = client.get("/health")
            assert response.status_code == 200
            assert response.json() == {"status": "healthy"}
    
    @pytest.mark.asyncio
    async def test_periodic_cleanup_runs_on_interval(self):
        """Test that periodic cleanup task runs at the specified interval.
        
        This test verifies that the periodic_token_cleanup function calls
        the cleanup function after the specified interval.
        
        Requirements: 7.3
        """
        # Arrange: Mock the cleanup function and asyncio.sleep
        with patch('app.main.cleanup_expired_tokens') as mock_cleanup, \
             patch('app.main.asyncio.sleep') as mock_sleep:
            
            # Configure mocks
            mock_cleanup.return_value = 5  # Simulate removing 5 tokens
            
            # Make sleep raise CancelledError after first call to exit the loop
            mock_sleep.side_effect = [None, asyncio.CancelledError()]
            
            # Act: Run the periodic cleanup task
            try:
                await periodic_token_cleanup(interval_hours=1)
            except asyncio.CancelledError:
                pass  # Expected when task is cancelled
            
            # Assert: Sleep was called with correct interval (1 hour = 3600 seconds)
            assert mock_sleep.call_count >= 1
            mock_sleep.assert_any_call(3600)
            
            # Assert: Cleanup was called at least once
            assert mock_cleanup.call_count >= 1
    
    @pytest.mark.asyncio
    async def test_periodic_cleanup_handles_errors_gracefully(self):
        """Test that periodic cleanup continues after errors.
        
        This test verifies that if the cleanup function raises an exception,
        the periodic task logs the error and continues running.
        
        Requirements: 7.3
        """
        # Arrange: Mock the cleanup function to raise an error, then succeed
        with patch('app.main.cleanup_expired_tokens') as mock_cleanup, \
             patch('app.main.asyncio.sleep') as mock_sleep:
            
            # Configure mocks
            mock_cleanup.side_effect = [
                Exception("Database error"),  # First call fails
                3,  # Second call succeeds
            ]
            
            # Make sleep raise CancelledError after two calls to exit the loop
            mock_sleep.side_effect = [None, None, asyncio.CancelledError()]
            
            # Act: Run the periodic cleanup task
            try:
                await periodic_token_cleanup(interval_hours=1)
            except asyncio.CancelledError:
                pass  # Expected when task is cancelled
            
            # Assert: Cleanup was called twice (once failed, once succeeded)
            assert mock_cleanup.call_count == 2
            
            # Assert: Sleep was called multiple times (task continued after error)
            assert mock_sleep.call_count >= 2
    
    @pytest.mark.asyncio
    async def test_periodic_cleanup_respects_custom_interval(self):
        """Test that periodic cleanup uses the specified interval.
        
        This test verifies that the interval_hours parameter is correctly
        converted to seconds and passed to asyncio.sleep.
        
        Requirements: 7.3
        """
        # Arrange: Mock the cleanup function and asyncio.sleep
        with patch('app.main.cleanup_expired_tokens') as mock_cleanup, \
             patch('app.main.asyncio.sleep') as mock_sleep:
            
            # Configure mocks
            mock_cleanup.return_value = 0
            mock_sleep.side_effect = [None, asyncio.CancelledError()]
            
            # Act: Run with custom interval (12 hours)
            try:
                await periodic_token_cleanup(interval_hours=12)
            except asyncio.CancelledError:
                pass
            
            # Assert: Sleep was called with 12 hours in seconds (43200)
            mock_sleep.assert_any_call(43200)
    
    @pytest.mark.asyncio
    async def test_periodic_cleanup_cancellation(self):
        """Test that periodic cleanup task can be cancelled gracefully.
        
        This test verifies that when the task is cancelled (e.g., during
        application shutdown), it exits cleanly without errors.
        
        Requirements: 7.3
        """
        # Arrange: Mock the cleanup function and asyncio.sleep
        with patch('app.main.cleanup_expired_tokens') as mock_cleanup, \
             patch('app.main.asyncio.sleep') as mock_sleep:
            
            # Configure mocks to immediately cancel
            mock_sleep.side_effect = asyncio.CancelledError()
            
            # Act & Assert: Task should exit cleanly when cancelled
            try:
                await periodic_token_cleanup(interval_hours=1)
            except asyncio.CancelledError:
                pytest.fail("CancelledError should be caught inside the function")
            
            # Assert: Cleanup was not called (cancelled before first run)
            assert mock_cleanup.call_count == 0


class TestApplicationLifespan:
    """Test application lifespan integration."""
    
    def test_application_health_check_works(self):
        """Test that the application is healthy after startup.
        
        This is a basic integration test to ensure the application starts
        correctly with all the lifespan events (including cleanup task).
        
        Requirements: 7.3
        """
        # Act: Create test client and make request
        with TestClient(app) as client:
            response = client.get("/health")
        
        # Assert: Application is healthy
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_application_root_endpoint_works(self):
        """Test that the root endpoint works after startup.
        
        This verifies the application is fully functional with the
        background task running.
        
        Requirements: 7.3
        """
        # Act: Create test client and make request
        with TestClient(app) as client:
            response = client.get("/")
        
        # Assert: Root endpoint returns expected data
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Welcome to Vet Clinic Scheduling System API"
        assert data["version"] == "1.0.0"
