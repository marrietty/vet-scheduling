# Implementation Plan: Vet Clinic Scheduling System Backend API

## Overview

This implementation plan breaks down the development of a REST API backend for a veterinary clinic scheduling system. The system follows a strict three-layer architecture (Repository → Service → Router) and implements role-based access control for admins and pet owners. The implementation is organized into phases that build incrementally, with each phase adding functionality that can be validated through code execution.

## Tasks

- [ ] 1. Set up project foundation and core infrastructure
  - [x] 1.1 Enhance core configuration and database setup
    - Update `backend/app/core/config.py` to include JWT_SECRET_KEY, JWT_ALGORITHM, JWT_EXPIRE_MINUTES, ADMIN_EMAIL settings
    - Update `backend/app/core/database.py` to ensure proper SQLModel engine and session management
    - _Requirements: 1.1, 1.2, 12.6, 12.7_
  
  - [x] 1.2 Create common enums and constants
    - Create `backend/app/common/enums.py` with UserRole, AppointmentStatus, ServiceType, ClinicStatusEnum, VaccinationStatus enums
    - _Requirements: 5.6, 5.7, 5.8, 5.9, 8.4_
  
  - [x] 1.3 Create custom exceptions
    - Create `backend/app/common/exceptions.py` with NotFoundException, ForbiddenException, BadRequestException, UnauthorizedException
    - _Requirements: 10.2, 10.3, 10.4_
  
  - [x] 1.4 Create utility functions
    - Create `backend/app/common/utils.py` with SERVICE_DURATIONS constant, calculate_end_time(), and get_vaccination_status() functions
    - _Requirements: 4.1, 4.2, 4.3, 5.5_
  
  - [x] 1.5 Create authentication infrastructure
    - Create `backend/app/infrastructure/auth.py` with hash_password(), verify_password(), create_access_token(), verify_token() functions
    - _Requirements: 1.5, 1.7_

- [ ] 2. Implement database models
  - [x] 2.1 Create User model
    - Create `backend/app/features/users/models.py` with User SQLModel (id, email, hashed_password, role, is_active, created_at)
    - Include relationship to pets
    - _Requirements: 12.1_
  
  - [x] 2.2 Create Pet model
    - Create `backend/app/features/pets/models.py` with Pet SQLModel (id, name, species, breed, date_of_birth, last_vaccination, medical_history, owner_id, created_at, updated_at)
    - Include relationships to owner and appointments
    - Use Column(JSON) for medical_history field
    - _Requirements: 12.2, 3.9_
  
  - [x] 2.3 Create Appointment model
    - Create `backend/app/features/appointments/models.py` with Appointment SQLModel (id, pet_id, user_id, start_time, end_time, service_type, status, notes, created_at, updated_at)
    - Include relationships to pet and user
    - _Requirements: 12.3_
  
  - [x] 2.4 Create ClinicStatus model
    - Create `backend/app/features/clinic/models.py` with ClinicStatus SQLModel (id, status, updated_at)
    - Single-row table with id=1
    - _Requirements: 12.4_

- [ ] 3. Create request/response schemas
  - [x] 3.1 Create authentication schemas
    - Create `backend/app/features/auth/schemas.py` with RegisterRequest, LoginRequest, TokenResponse
    - _Requirements: 1.1, 1.5_
  
  - [x] 3.2 Create pet schemas
    - Create `backend/app/features/pets/schemas.py` with PetCreateRequest, PetUpdateRequest, PetResponse
    - Include vaccination_status in PetResponse (computed field)
    - _Requirements: 3.1, 3.4, 4.4_
  
  - [x] 3.3 Create appointment schemas
    - Create `backend/app/features/appointments/schemas.py` with AppointmentCreateRequest, AppointmentUpdateStatusRequest, AppointmentResponse
    - _Requirements: 5.1, 6.1_
  
  - [x] 3.4 Create clinic schemas
    - Create `backend/app/features/clinic/schemas.py` with ClinicStatusResponse, ClinicStatusUpdateRequest
    - _Requirements: 8.1, 8.2_

- [ ] 4. Implement repository layer
  - [x] 4.1 Create UserRepository
    - Create `backend/app/features/users/repository.py` with get_by_id(), get_by_email(), create() methods
    - _Requirements: 1.1, 1.4, 1.5_
  
  - [x] 4.2 Create PetRepository
    - Create `backend/app/features/pets/repository.py` with get_by_id(), get_all_by_owner(), get_all(), create(), update(), delete() methods
    - _Requirements: 3.1, 3.2, 3.3, 3.5, 3.6_
  
  - [x] 4.3 Create AppointmentRepository
    - Create `backend/app/features/appointments/repository.py` with get_by_id(), get_all(), get_by_owner_id(), check_overlap(), create(), update(), delete() methods
    - Implement filtering by status, from_date, to_date
    - _Requirements: 5.11, 7.1, 7.2, 7.3, 7.4, 7.5_
  
  - [x] 4.4 Create ClinicStatusRepository
    - Create `backend/app/features/clinic/repository.py` with get_current_status(), update_status() methods
    - Initialize with default "open" status if not exists
    - _Requirements: 8.1, 8.2_

- [ ] 5. Implement service layer with business logic
  - [x] 5.1 Create AuthService
    - Create `backend/app/features/auth/service.py` with register() and login() methods
    - Implement role assignment based on ADMIN_EMAIL
    - Implement password hashing and verification
    - Implement duplicate email checking
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7_
  
  - [ ]* 5.2 Write property tests for AuthService
    - **Property 1: Password hashing**
    - **Property 2: Role assignment for non-admin emails**
    - **Property 3: Duplicate email rejection**
    - **Property 4: Valid login returns token**
    - **Property 5: Invalid credentials rejection**
    - **Property 6: Email format validation**
    - **Property 7: JWT token round-trip**
    - **Property 8: Invalid token rejection**
    - **Validates: Requirements 1.1, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 2.5, 2.6**
  
  - [ ]* 5.3 Write unit tests for AuthService
    - Test admin email gets admin role (example)
    - Test edge cases: empty password, null values
    - Test error messages and status codes
    - _Requirements: 1.2_
  
  - [x] 5.4 Create PetService
    - Create `backend/app/features/pets/service.py` with create_pet(), get_pets(), get_pet_by_id(), update_pet(), delete_pet() methods
    - Implement ownership validation for pet owners
    - Implement role-based filtering (admin sees all, owners see own)
    - _Requirements: 2.2, 3.1, 3.2, 3.3, 3.5, 3.6, 3.7_
  
  - [ ]* 5.5 Write property tests for PetService
    - **Property 9: Pet ownership association**
    - **Property 10: Pet owner access control**
    - **Property 11: Pet data persistence**
    - **Property 12: Medical history JSON storage**
    - **Property 13: Pet update authorization**
    - **Property 14: Pet deletion authorization**
    - **Property 15: Vaccination status includes in response**
    - **Validates: Requirements 2.2, 3.1, 3.2, 3.4, 3.5, 3.6, 3.8, 3.9, 4.4**
  
  - [ ]* 5.6 Write unit tests for PetService
    - Test admin can access all pets (example)
    - Test admin can update/delete any pet (example)
    - Test edge cases: null breed, null date_of_birth
    - _Requirements: 3.3, 3.7_
  
  - [x] 5.7 Create AppointmentService
    - Create `backend/app/features/appointments/service.py` with create_appointment(), get_appointments(), update_appointment_status(), cancel_appointment() methods
    - Implement all appointment validation rules (pet exists, ownership, future time, clinic open, no overlaps)
    - Implement automatic end_time calculation
    - Implement status transition rules
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.10, 5.11, 5.12, 6.1, 6.2, 6.3, 6.5, 6.6, 6.7, 6.10_
  
  - [ ]* 5.8 Write property tests for AppointmentService
    - **Property 16: Expired vaccination detection**
    - **Property 17: Valid vaccination detection**
    - **Property 18: Non-existent pet rejection**
    - **Property 19: Appointment pet ownership validation**
    - **Property 20: Past time rejection**
    - **Property 21: End time calculation**
    - **Property 22: Closed clinic rejection**
    - **Property 23: Overlap detection**
    - **Property 24: Successful appointment creation**
    - **Property 25: Pet owner cannot confirm or complete**
    - **Property 26: Completed appointment immutability**
    - **Property 27: Cancelled appointment immutability**
    - **Property 28: Pet owner cancellation authorization**
    - **Property 29: Pet owner appointment filtering**
    - **Property 30: Status filter**
    - **Property 31: Date range filter**
    - **Property 32: Multiple filter combination**
    - **Validates: Requirements 4.2, 4.3, 5.1, 5.2, 5.4, 5.5, 5.10, 5.11, 5.12, 6.3, 6.5, 6.6, 6.7, 7.1, 7.3, 7.4, 7.5, 7.6**
  
  - [ ]* 5.9 Write unit tests for AppointmentService
    - Test admin can create appointment for any pet (example)
    - Test admin can confirm/complete appointments (example)
    - Test admin can cancel any appointment (example)
    - Test edge cases: adjacent appointments (no overlap), null notes
    - Test all service type durations (vaccination=30, routine=45, surgery=120, emergency=15)
    - _Requirements: 5.3, 5.6, 5.7, 5.8, 5.9, 6.1, 6.2, 6.9, 9.5_
  
  - [x] 5.10 Create ClinicService
    - Create `backend/app/features/clinic/service.py` with get_status() and update_status() methods
    - _Requirements: 8.1, 8.2_
  
  - [ ]* 5.11 Write property tests for ClinicService
    - **Property 33: Pet owner cannot update clinic status**
    - **Property 34: Clinic status enum validation**
    - **Validates: Requirements 8.3, 8.4**
  
  - [ ]* 5.12 Write unit tests for ClinicService
    - Test admin can update clinic status (example)
    - Test public access to clinic status (example)
    - _Requirements: 8.1, 8.2_

- [x] 6. Checkpoint - Ensure service layer tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 7. Implement authentication dependencies
  - [x] 7.1 Create authentication dependencies
    - Create `backend/app/common/dependencies.py` with get_current_user() and require_role() dependencies
    - Implement JWT token extraction and validation
    - Implement user lookup and active status check
    - _Requirements: 2.1, 2.4, 2.5, 2.6, 2.7_
  
  - [ ]* 7.2 Write unit tests for dependencies
    - Test missing token rejection (edge case)
    - Test inactive user rejection
    - Test role-based access control
    - _Requirements: 2.4, 2.7_

- [ ] 8. Implement router layer (API endpoints)
  - [x] 8.1 Create authentication router
    - Create `backend/app/features/auth/router.py` with POST /api/v1/auth/register and POST /api/v1/auth/login endpoints
    - Auto-login after registration (return token)
    - _Requirements: 1.1, 1.5_
  
  - [x] 8.2 Create pet router
    - Create `backend/app/features/pets/router.py` with GET, POST, PATCH, DELETE /api/v1/pets endpoints
    - Add computed vaccination_status to all pet responses
    - Require authentication for all endpoints
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 4.4_
  
  - [x] 8.3 Create appointment router
    - Create `backend/app/features/appointments/router.py` with GET, POST, PATCH, DELETE /api/v1/appointments endpoints
    - Implement query parameters for filtering (status, from_date, to_date)
    - Require authentication for all endpoints
    - Admin-only for PATCH /{id}/status
    - _Requirements: 5.1, 6.1, 7.1, 7.3, 7.4, 7.5_
  
  - [x] 8.4 Create clinic router
    - Create `backend/app/features/clinic/router.py` with GET /api/v1/clinic/status (public) and PATCH /api/v1/clinic/status (admin-only) endpoints
    - _Requirements: 8.1, 8.2, 8.3_

- [ ] 9. Wire up main application
  - [x] 9.1 Create main FastAPI application
    - Create/update `backend/app/main.py` to initialize FastAPI app
    - Include all routers (auth, pets, appointments, clinic)
    - Configure CORS if needed
    - Add startup event to create database tables
    - _Requirements: 11.1, 12.8_
  
  - [ ]* 9.2 Write integration tests for API endpoints
    - Test complete authentication flow (register → login → access protected endpoint)
    - Test complete appointment booking flow (register → create pet → book appointment)
    - Test role-based access control across endpoints
    - Test error responses and status codes
    - _Requirements: 2.1, 2.2, 2.4, 10.1, 10.2, 10.3, 10.4_

- [ ] 10. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Property tests validate universal correctness properties with minimum 100 iterations
- Unit tests validate specific examples and edge cases
- The three-layer architecture (Repository → Service → Router) must be consistently followed
- All functions and methods must have Python type hints
- Follow DRY and KISS principles throughout implementation
