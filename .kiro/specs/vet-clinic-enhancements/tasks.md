# Implementation Plan: Vet Clinic Enhancements

## Overview

This implementation plan breaks down the vet clinic enhancements into discrete coding tasks. The approach follows a layered implementation strategy: database migrations first, then models and repositories, followed by services, and finally API endpoints. Testing tasks are integrated throughout to validate functionality incrementally.

## Tasks

- [ ] 2. Token blacklist model and repository
  - [x] 2.1 Create TokenBlacklist SQLAlchemy model
    - Define model with all required fields and relationships
    - Add indexes on token field for fast lookup
    - _Requirements: 1.1, 1.3_
  
  - [x] 2.2 Implement TokenBlacklistRepository
    - Implement add_token() method
    - Implement is_token_blacklisted() method with expiration check
    - Implement remove_expired_tokens() method
    - _Requirements: 1.1, 1.2, 7.2, 7.4_
  
  - [ ]* 2.3 Write property tests for token blacklist
    - **Property 1: Token blacklist persistence**
    - **Property 4: Expired token blacklist exclusion**
    - **Property 5: Cleanup removes only expired tokens**
    - **Validates: Requirements 1.1, 1.3, 7.2, 7.4**

- [ ] 3. Authentication service enhancement
  - [x] 3.1 Add logout functionality to AuthService
    - Implement logout() method that extracts token expiration and adds to blacklist
    - Implement verify_token_not_blacklisted() method
    - Integrate blacklist check into existing token verification flow
    - _Requirements: 1.1, 1.2, 1.4_
  
  - [ ]* 3.2 Write property tests for authentication
    - **Property 2: Blacklisted token rejection**
    - **Property 3: Invalid token logout rejection**
    - **Validates: Requirements 1.2, 1.4**
  
  - [x] 3.3 Add logout endpoint to auth router
    - Create POST /auth/logout endpoint
    - Extract token from Authorization header
    - Call auth_service.logout() with token and current user
    - Return success response
    - _Requirements: 1.5_
  
  - [ ]* 3.4 Write integration tests for logout endpoint
    - Test successful logout flow
    - Test logout with invalid token
    - Test authentication with blacklisted token
    - _Requirements: 1.1, 1.2, 1.4_

- [x] 4. Checkpoint - Ensure authentication tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 5. User model and repository updates
  - [x] 5.1 Update User model with new fields
    - Add city column (VARCHAR, nullable)
    - Add preferences column (JSONB, nullable)
    - _Requirements: 4.1, 8.1_
  
  - [x] 5.2 Extend UserRepository with profile methods
    - Implement get_user_profile() method
    - Implement update_user_profile() method
    - Implement email_exists_for_other_user() method for uniqueness check
    - _Requirements: 2.1, 3.1, 3.2_

- [ ] 6. User profile schemas
  - [x] 6.1 Create UserProfileResponse schema
    - Include all profile fields (id, full_name, email, phone, city, role, is_active, preferences, created_at)
    - Exclude sensitive fields (hashed_password)
    - _Requirements: 2.1, 2.2_
  
  - [x] 6.2 Create UserProfileUpdate schema
    - Define optional fields for full_name, email, phone, city, preferences
    - Add validators for email format, phone format, non-empty name
    - Add validator for non-empty city when provided
    - _Requirements: 3.1, 3.2, 3.3, 4.4_

- [ ] 7. User profile service
  - [x] 7.1 Create UserService with profile methods
    - Implement get_current_user_profile() method
    - Implement update_user_profile() method with validation logic
    - Add email uniqueness check before updating email
    - Add validation for empty name, invalid email format, invalid phone format
    - _Requirements: 2.1, 3.1, 3.2, 3.3, 3.4, 3.5, 3.7_
  
  - [ ]* 7.2 Write property tests for user profile
    - **Property 6: Profile response completeness**
    - **Property 7: Profile response excludes sensitive data**
    - **Property 8: Empty name rejection**
    - **Property 9: Invalid email format rejection**
    - **Property 10: Duplicate email rejection**
    - **Property 11: Phone format validation**
    - **Property 12: City update round-trip**
    - **Property 13: Preferences update round-trip**
    - **Property 14: Cross-user profile update prevention**
    - **Property 15: Empty city rejection when provided**
    - **Property 16: Preferences field independence**
    - **Property 17: Invalid preferences structure rejection**
    - **Validates: Requirements 2.1, 2.2, 3.1, 3.2, 3.3, 3.4, 3.5, 3.7, 4.4, 8.2, 8.5**

- [ ] 8. User profile endpoints
  - [x] 8.1 Create user router with profile endpoints
    - Create GET /users/profile endpoint (returns current user's profile)
    - Create PATCH /users/profile endpoint (updates current user's profile)
    - Use get_current_user dependency for authentication
    - _Requirements: 2.1, 2.3, 3.6_
  
  - [ ]* 8.2 Write integration tests for profile endpoints
    - Test profile retrieval with valid authentication
    - Test profile retrieval without authentication
    - Test profile update with valid data
    - Test profile update with invalid email
    - Test profile update with duplicate email
    - Test cross-user profile update attempt
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 3.1, 3.2, 3.7_

- [x] 9. Checkpoint - Ensure profile management tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 10. Pet profile verification and enhancement
  - [x] 10.1 Verify pet model has required fields
    - Confirm species, breed, and notes fields exist in Pet model
    - Ensure species is required, breed and notes are optional
    - _Requirements: 5.1, 5.2_
  
  - [x] 10.2 Update pet schemas if needed
    - Ensure PetCreate schema requires species
    - Ensure PetUpdate schema validates non-empty species if provided
    - Ensure PetResponse schema includes species, breed, and notes
    - _Requirements: 5.2, 5.3, 5.4_
  
  - [ ]* 10.3 Write property tests for pet profiles
    - **Property 18: Pet creation requires species**
    - **Property 19: Empty species rejection**
    - **Property 20: Pet response completeness**
    - **Property 21: Notes field accepts complex text**
    - **Validates: Requirements 5.2, 5.3, 5.4, 5.5**

- [ ] 11. Appointment rescheduling schemas
  - [x] 11.1 Create AppointmentReschedule schema
    - Define start_time and end_time fields (both required)
    - Add validator to ensure end_time is after start_time
    - _Requirements: 6.2_

- [ ] 12. Appointment repository extension
  - [x] 12.1 Add rescheduling methods to AppointmentRepository
    - Implement get_appointment_by_id() method
    - Implement check_time_slot_available() method (checks for overlapping appointments)
    - Implement update_appointment_times() method
    - _Requirements: 6.3, 6.5_

- [ ] 13. Appointment service extension
  - [x] 13.1 Add reschedule_appointment method to AppointmentService
    - Fetch appointment and verify it exists
    - Verify current user owns the pet associated with the appointment
    - Verify appointment status is 'scheduled' or 'confirmed'
    - Check clinic is open during new time (use existing clinic service)
    - Check time slot is available (no double booking)
    - Update appointment times via repository
    - Return updated appointment
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.7, 6.8_
  
  - [ ]* 13.2 Write property tests for appointment rescheduling
    - **Property 22: Appointment ownership validation**
    - **Property 23: Reschedule requires complete time range**
    - **Property 24: Double-booking prevention**
    - **Property 25: Clinic hours validation**
    - **Property 26: Reschedule time update round-trip**
    - **Property 27: Updated timestamp invariant**
    - **Property 28: Status-based reschedule restriction**
    - **Validates: Requirements 6.1, 6.2, 6.3, 6.4, 6.5, 6.7, 6.8**

- [ ] 14. Appointment rescheduling endpoint
  - [x] 14.1 Add reschedule endpoint to appointment router
    - Create PATCH /appointments/{appointment_id}/reschedule endpoint
    - Accept AppointmentReschedule schema in request body
    - Call appointment_service.reschedule_appointment()
    - Return updated appointment
    - Handle all error cases with appropriate status codes
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.8, 6.9_
  
  - [ ]* 14.2 Write integration tests for reschedule endpoint
    - Test successful reschedule
    - Test reschedule with invalid appointment ID
    - Test reschedule by non-owner
    - Test reschedule with conflicting time slot
    - Test reschedule outside clinic hours
    - Test reschedule of completed appointment
    - _Requirements: 6.1, 6.3, 6.4, 6.8_

- [x] 15. Checkpoint - Ensure appointment rescheduling tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 16. Token cleanup background task
  - [x] 16.1 Create background task for token cleanup
    - Create cleanup_expired_tokens() function
    - Call token_blacklist_repository.remove_expired_tokens()
    - Add logging for number of tokens removed
    - _Requirements: 7.3, 7.4_
  
  - [x] 16.2 Schedule cleanup task
    - Add cleanup task to FastAPI lifespan or startup event
    - Configure to run periodically (e.g., daily)
    - _Requirements: 7.3_
  
  - [ ]* 16.3 Write unit tests for cleanup task
    - Test cleanup removes only expired tokens
    - Test cleanup with empty blacklist
    - Test cleanup with mixed expired/valid tokens
    - _Requirements: 7.4_

- [ ] 17. Error handling and validation
  - [x] 17.1 Add custom exception classes
    - Create TokenBlacklistedException for blacklisted tokens
    - Create ProfileUpdateForbiddenException for cross-user updates
    - Create AppointmentRescheduleForbiddenException for ownership violations
    - Create TimeSlotUnavailableException for double bookings
    - _Requirements: 1.2, 3.7, 6.1, 6.3_
  
  - [x] 17.2 Add exception handlers
    - Register exception handlers in FastAPI app
    - Map exceptions to appropriate HTTP status codes and error messages
    - Ensure all error responses include timestamp and error type
    - _Requirements: 1.2, 2.4, 3.7, 3.8, 6.6, 6.9_

- [ ] 18. Integration and wiring
  - [x] 18.1 Wire all new routers into main application
    - Register user router with /users prefix
    - Ensure auth router includes new logout endpoint
    - Ensure appointment router includes reschedule endpoint
    - _Requirements: All_
  
  - [x] 18.2 Update API documentation
    - Add docstrings to all new endpoints
    - Ensure OpenAPI schema includes all new endpoints and schemas
    - _Requirements: All_
  
  - [ ]* 18.3 Write end-to-end integration tests
    - Test complete logout flow (login → logout → attempt to use token)
    - Test complete profile update flow (get profile → update → verify changes)
    - Test complete reschedule flow (create appointment → reschedule → verify new time)
    - _Requirements: 1.1, 1.2, 3.4, 3.5, 6.5_

- [x] 19. Final checkpoint - Ensure all tests pass
  - Run full test suite (unit + property + integration)
  - Verify test coverage meets 90% threshold
  - Ensure all 28 correctness properties are implemented as tests
  - Ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Property tests validate universal correctness properties with 100+ iterations
- Unit tests validate specific examples and edge cases
- Integration tests validate end-to-end API flows
- Checkpoints ensure incremental validation throughout implementation
- Database migrations should be reviewed carefully before running in production
- Token cleanup task frequency should be configured based on token expiration times
