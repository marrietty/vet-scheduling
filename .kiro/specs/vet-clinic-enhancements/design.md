# Design Document: Vet Clinic Enhancements

## Overview

This design extends the existing FastAPI-based veterinary clinic scheduling system with enhanced authentication, user profile management, and appointment rescheduling capabilities. The enhancements maintain the current architecture while adding new endpoints, database tables, and business logic to support secure logout, profile editing, and flexible appointment management.

The design follows RESTful API principles and leverages the existing SQLAlchemy ORM, JWT authentication infrastructure, and PostgreSQL database. All new features integrate seamlessly with the current system's user, pet, and appointment management capabilities.

## Architecture

### System Components

The enhancements follow the existing layered architecture:

1. **API Layer (Router)**: FastAPI routers exposing REST endpoints
2. **Service Layer**: Business logic and orchestration
3. **Repository Layer**: Data access and database operations
4. **Model Layer**: SQLAlchemy ORM models
5. **Schema Layer**: Pydantic models for request/response validation

### New Components

1. **Token Blacklist Service**: Manages token invalidation and cleanup
2. **User Profile Service**: Handles profile viewing and editing operations
3. **Appointment Reschedule Service**: Validates and processes appointment time changes

### Database Schema Changes

#### New Table: token_blacklist

```
token_blacklist
├── id (UUID, primary key)
├── token (TEXT, unique, not null)
├── expires_at (TIMESTAMP, not null)
├── blacklisted_at (TIMESTAMP, not null, default: now())
└── user_id (UUID, foreign key to users.id)
```

#### Modified Table: users

```
users (existing fields remain)
└── city (VARCHAR(100), nullable)  -- NEW FIELD
└── preferences (JSONB, nullable)  -- NEW FIELD
```

The pets and appointments tables already have the required fields (species, breed, notes for pets; start_time, end_time, status for appointments), so no modifications are needed.

## Components and Interfaces

### 1. Authentication Enhancement

#### Token Blacklist Model

```python
class TokenBlacklist(Base):
    __tablename__ = "token_blacklist"
    
    id: UUID
    token: str  # The JWT token string
    expires_at: datetime  # When the token naturally expires
    blacklisted_at: datetime  # When it was blacklisted
    user_id: UUID  # Reference to the user
```

#### Token Blacklist Repository

```python
class TokenBlacklistRepository:
    def add_token(token: str, expires_at: datetime, user_id: UUID) -> TokenBlacklist
    def is_token_blacklisted(token: str) -> bool
    def remove_expired_tokens() -> int
```

#### Auth Service Extension

```python
class AuthService:
    # Existing methods...
    
    def logout(token: str, user_id: UUID) -> None:
        # Extract expiration from token
        # Add to blacklist
        
    def verify_token_not_blacklisted(token: str) -> None:
        # Check if token is in blacklist
        # Raise exception if blacklisted
```

#### Auth Router Extension

```python
@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    # Extract token from request
    # Call auth_service.logout()
    # Return success response
```

### 2. User Profile Management

#### User Profile Schemas

```python
class UserProfileResponse(BaseModel):
    id: UUID
    full_name: str
    email: str
    phone: Optional[str]
    city: Optional[str]
    role: str
    is_active: bool
    preferences: Optional[dict]
    created_at: datetime

class UserProfileUpdate(BaseModel):
    full_name: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    city: Optional[str]
    preferences: Optional[dict]
```

#### User Repository Extension

```python
class UserRepository:
    # Existing methods...
    
    def get_user_profile(user_id: UUID) -> User
    def update_user_profile(user_id: UUID, updates: dict) -> User
    def email_exists_for_other_user(email: str, user_id: UUID) -> bool
```

#### User Service

```python
class UserService:
    def get_current_user_profile(user_id: UUID) -> UserProfileResponse:
        # Fetch user from repository
        # Transform to response schema (exclude sensitive fields)
        
    def update_user_profile(user_id: UUID, updates: UserProfileUpdate) -> UserProfileResponse:
        # Validate email uniqueness if email is being updated
        # Validate phone format if phone is being updated
        # Validate city format if city is being updated
        # Update user via repository
        # Return updated profile
```

#### User Router

```python
@router.get("/profile")
async def get_profile(current_user: User = Depends(get_current_user)):
    # Call user_service.get_current_user_profile()
    
@router.patch("/profile")
async def update_profile(
    updates: UserProfileUpdate,
    current_user: User = Depends(get_current_user)
):
    # Call user_service.update_user_profile()
```

### 3. Pet Profile Enhancement

The existing pet models already support species, breed, and notes fields. The enhancement ensures:

1. **Validation**: Species is required, breed and notes are optional
2. **API Responses**: All three fields are included in pet response schemas
3. **Update Operations**: All three fields can be updated via existing endpoints

No new components needed - verification of existing implementation only.

### 4. Appointment Rescheduling

#### Appointment Schemas Extension

```python
class AppointmentReschedule(BaseModel):
    start_time: datetime
    end_time: datetime
    
    @validator('end_time')
    def end_after_start(cls, v, values):
        if 'start_time' in values and v <= values['start_time']:
            raise ValueError('end_time must be after start_time')
        return v
```

#### Appointment Repository Extension

```python
class AppointmentRepository:
    # Existing methods...
    
    def get_appointment_by_id(appointment_id: UUID) -> Optional[Appointment]
    def check_time_slot_available(start_time: datetime, end_time: datetime, exclude_appointment_id: Optional[UUID]) -> bool
    def update_appointment_times(appointment_id: UUID, start_time: datetime, end_time: datetime) -> Appointment
```

#### Appointment Service Extension

```python
class AppointmentService:
    # Existing methods...
    
    def reschedule_appointment(
        appointment_id: UUID,
        user_id: UUID,
        new_start: datetime,
        new_end: datetime
    ) -> Appointment:
        # Fetch appointment
        # Verify user owns the pet
        # Verify appointment status is 'scheduled' or 'confirmed'
        # Check clinic is open during new time
        # Check time slot is available (no double booking)
        # Update appointment times
        # Return updated appointment
```

#### Appointment Router Extension

```python
@router.patch("/{appointment_id}/reschedule")
async def reschedule_appointment(
    appointment_id: UUID,
    reschedule_data: AppointmentReschedule,
    current_user: User = Depends(get_current_user)
):
    # Call appointment_service.reschedule_appointment()
```

### 5. Token Cleanup Background Task

```python
# In a background task or scheduled job
async def cleanup_expired_tokens():
    # Call token_blacklist_repository.remove_expired_tokens()
    # Log number of tokens removed
```

This can be implemented as:
- A FastAPI background task triggered periodically
- A separate cron job or scheduled task
- Part of application startup/shutdown lifecycle

## Data Models

### Token Blacklist

- **id**: Unique identifier for the blacklist entry
- **token**: The full JWT token string (indexed for fast lookup)
- **expires_at**: Natural expiration time of the token (for cleanup)
- **blacklisted_at**: Timestamp when token was blacklisted (for auditing)
- **user_id**: Reference to the user who logged out (for auditing)

### User (Enhanced)

- **city**: Optional text field for user's city location
- **preferences**: JSONB field storing user preferences as flexible key-value pairs

### Pet (Existing - Verification)

- **species**: Required text field (e.g., "Dog", "Cat", "Bird")
- **breed**: Optional text field (e.g., "Labrador", "Persian")
- **notes**: Optional text field for additional information

### Appointment (Existing - Used for Rescheduling)

- **start_time**: Appointment start timestamp
- **end_time**: Appointment end timestamp
- **status**: Current status (scheduled, confirmed, completed, cancelled)
- **updated_at**: Last modification timestamp

## Correctness Properties


*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Authentication and Token Management Properties

**Property 1: Token blacklist persistence**
*For any* valid authentication token and user, when logout is called with that token, the token should appear in the token blacklist with the correct expiration timestamp.
**Validates: Requirements 1.1, 1.3**

**Property 2: Blacklisted token rejection**
*For any* token that exists in the token blacklist and has not expired, authentication attempts using that token should be rejected with an unauthorized error.
**Validates: Requirements 1.2**

**Property 3: Invalid token logout rejection**
*For any* malformed or expired token, attempting to logout with that token should be rejected with an appropriate error.
**Validates: Requirements 1.4**

**Property 4: Expired token blacklist exclusion**
*For any* token in the blacklist whose expiration timestamp is in the past, the blacklist check should return false (token is not considered blacklisted).
**Validates: Requirements 7.2**

**Property 5: Cleanup removes only expired tokens**
*For any* state of the token blacklist, after running the cleanup operation, all remaining tokens should have expiration timestamps in the future, and all tokens with past expiration timestamps should be removed.
**Validates: Requirements 7.4**

### User Profile Management Properties

**Property 6: Profile response completeness**
*For any* user, the profile response should include full_name, email, phone, city, role, is_active, preferences, and created_at fields.
**Validates: Requirements 2.1**

**Property 7: Profile response excludes sensitive data**
*For any* user, the profile response should never contain hashed_password or other authentication credentials.
**Validates: Requirements 2.2**

**Property 8: Empty name rejection**
*For any* string composed entirely of whitespace or empty string, attempting to update a user's full_name to that value should be rejected.
**Validates: Requirements 3.1**

**Property 9: Invalid email format rejection**
*For any* string that does not match valid email format (missing @, invalid domain, etc.), attempting to update a user's email to that value should be rejected.
**Validates: Requirements 3.2**

**Property 10: Duplicate email rejection**
*For any* two different users, if user A attempts to update their email to match user B's existing email, the update should be rejected.
**Validates: Requirements 3.2**

**Property 11: Phone format validation**
*For any* valid phone number format, updating a user's phone should succeed, and for any invalid phone format, the update should be rejected.
**Validates: Requirements 3.3**

**Property 12: City update round-trip**
*For any* user and valid city string, if the user updates their city and then retrieves their profile, the returned city should match the updated value.
**Validates: Requirements 3.4**

**Property 13: Preferences update round-trip**
*For any* user and valid preferences object, if the user updates their preferences and then retrieves their profile, the returned preferences should match the updated value.
**Validates: Requirements 3.5**

**Property 14: Cross-user profile update prevention**
*For any* two different users A and B, user A should not be able to update user B's profile information.
**Validates: Requirements 3.7**

**Property 15: Empty city rejection when provided**
*For any* empty string or whitespace-only string, if provided as a city value in a profile update, the update should be rejected.
**Validates: Requirements 4.4**

**Property 16: Preferences field independence**
*For any* user, updating the preferences field should not modify any other profile fields (full_name, email, phone, city should remain unchanged).
**Validates: Requirements 8.5**

**Property 17: Invalid preferences structure rejection**
*For any* malformed preferences data that doesn't match the expected structure, the profile update should be rejected with a validation error.
**Validates: Requirements 8.2**

### Pet Profile Properties

**Property 18: Pet creation requires species**
*For any* pet creation request without a species field, the creation should be rejected, and for any request with a valid species, the creation should succeed (with breed and notes being optional).
**Validates: Requirements 5.2**

**Property 19: Empty species rejection**
*For any* empty string or whitespace-only string, attempting to update a pet's species to that value should be rejected.
**Validates: Requirements 5.3**

**Property 20: Pet response completeness**
*For any* pet, the pet response should include species, breed, and notes fields (with breed and notes potentially null/empty).
**Validates: Requirements 5.4**

**Property 21: Notes field accepts complex text**
*For any* string containing newlines, special characters, or unicode, storing that string in a pet's notes field and then retrieving the pet should return the exact same string.
**Validates: Requirements 5.5**

### Appointment Rescheduling Properties

**Property 22: Appointment ownership validation**
*For any* appointment and user, if the user does not own the pet associated with the appointment, attempting to reschedule that appointment should be rejected with a forbidden error.
**Validates: Requirements 6.1**

**Property 23: Reschedule requires complete time range**
*For any* reschedule request missing either start_time or end_time, the request should be rejected with a validation error.
**Validates: Requirements 6.2**

**Property 24: Double-booking prevention**
*For any* appointment reschedule request where the new time range overlaps with an existing appointment's time range, the reschedule should be rejected with an error indicating the time slot is unavailable.
**Validates: Requirements 6.3**

**Property 25: Clinic hours validation**
*For any* appointment reschedule request where the new time falls outside clinic operating hours, the reschedule should be rejected with an error indicating the clinic is closed.
**Validates: Requirements 6.4**

**Property 26: Reschedule time update round-trip**
*For any* valid appointment reschedule to a new start_time and end_time, after the reschedule operation, retrieving the appointment should return the new times.
**Validates: Requirements 6.5**

**Property 27: Updated timestamp invariant**
*For any* appointment, after a successful reschedule operation, the appointment's updated_at timestamp should be more recent than it was before the reschedule.
**Validates: Requirements 6.7**

**Property 28: Status-based reschedule restriction**
*For any* appointment with status other than "scheduled" or "confirmed", attempting to reschedule should be rejected with an error indicating the appointment cannot be rescheduled.
**Validates: Requirements 6.8**

## Error Handling

### Authentication Errors

1. **Invalid Token**: Return 401 Unauthorized with message "Invalid or expired token"
2. **Blacklisted Token**: Return 401 Unauthorized with message "Token has been invalidated"
3. **Missing Token**: Return 401 Unauthorized with message "Authentication required"

### Validation Errors

1. **Empty Required Field**: Return 422 Unprocessable Entity with field-specific message
2. **Invalid Email Format**: Return 422 with message "Invalid email format"
3. **Duplicate Email**: Return 409 Conflict with message "Email already in use"
4. **Invalid Phone Format**: Return 422 with message "Invalid phone number format"
5. **Invalid Time Range**: Return 422 with message "End time must be after start time"

### Authorization Errors

1. **Unauthorized Profile Access**: Return 403 Forbidden with message "Cannot access another user's profile"
2. **Unauthorized Appointment Reschedule**: Return 403 Forbidden with message "You can only reschedule appointments for your own pets"

### Business Logic Errors

1. **Time Slot Unavailable**: Return 409 Conflict with message "The requested time slot is not available"
2. **Clinic Closed**: Return 422 with message "Clinic is closed during the requested time"
3. **Invalid Appointment Status**: Return 422 with message "Cannot reschedule completed or cancelled appointments"

### Database Errors

1. **Record Not Found**: Return 404 Not Found with entity-specific message
2. **Database Connection Error**: Return 503 Service Unavailable with message "Service temporarily unavailable"

All errors should include:
- Appropriate HTTP status code
- Clear error message
- Error type/code for client handling
- Timestamp of the error

## Testing Strategy

### Overview

This feature will be tested using a dual approach combining unit tests for specific scenarios and property-based tests for universal correctness properties. This ensures both concrete examples work correctly and general rules hold across all possible inputs.

### Property-Based Testing

**Framework**: Use `hypothesis` for Python property-based testing

**Configuration**:
- Minimum 100 iterations per property test
- Each test tagged with format: `# Feature: vet-clinic-enhancements, Property N: [property description]`
- Use custom generators for domain objects (users, tokens, appointments, pets)

**Test Organization**:
```
tests/
├── property_tests/
│   ├── test_auth_properties.py          # Properties 1-5
│   ├── test_profile_properties.py       # Properties 6-17
│   ├── test_pet_properties.py           # Properties 18-21
│   └── test_appointment_properties.py   # Properties 22-28
```

**Custom Generators**:
- `user_generator()`: Generate valid user objects with random data
- `token_generator()`: Generate valid JWT tokens with varying expiration
- `pet_generator()`: Generate pet objects with various species/breeds
- `appointment_generator()`: Generate appointments with valid time ranges
- `datetime_generator()`: Generate timestamps within business hours

**Property Test Examples**:

```python
# Feature: vet-clinic-enhancements, Property 1: Token blacklist persistence
@given(token=token_generator(), user=user_generator())
def test_token_blacklist_persistence(token, user):
    auth_service.logout(token, user.id)
    assert token_blacklist_repo.is_token_blacklisted(token)

# Feature: vet-clinic-enhancements, Property 13: Preferences update round-trip
@given(user=user_generator(), preferences=st.dictionaries(st.text(), st.text()))
def test_preferences_round_trip(user, preferences):
    user_service.update_profile(user.id, {"preferences": preferences})
    profile = user_service.get_profile(user.id)
    assert profile.preferences == preferences
```

### Unit Testing

**Focus Areas**:
- Specific edge cases (empty strings, null values, boundary conditions)
- Integration between layers (router → service → repository)
- Error message content and format
- Database transaction handling
- Authentication middleware integration

**Test Organization**:
```
tests/
├── unit/
│   ├── test_auth_service.py
│   ├── test_user_service.py
│   ├── test_appointment_service.py
│   ├── test_token_blacklist_repo.py
│   └── test_validators.py
├── integration/
│   ├── test_auth_endpoints.py
│   ├── test_profile_endpoints.py
│   └── test_appointment_endpoints.py
```

**Unit Test Examples**:
- Test logout with already-blacklisted token
- Test profile update with SQL injection attempt
- Test reschedule with appointment at exact clinic closing time
- Test cleanup with mixed expired/valid tokens
- Test preferences with deeply nested JSON structures

### Test Data Management

**Fixtures**:
- Use pytest fixtures for database setup/teardown
- Create factory functions for test data generation
- Use database transactions that rollback after each test

**Test Database**:
- Separate test database instance
- Reset schema between test runs
- Seed with minimal required data (clinic hours, etc.)

### Coverage Goals

- **Line Coverage**: Minimum 90% for new code
- **Branch Coverage**: Minimum 85% for business logic
- **Property Coverage**: 100% of correctness properties implemented as tests
- **Integration Coverage**: All new API endpoints tested end-to-end

### Continuous Integration

- Run property tests with 100 iterations on every commit
- Run full test suite (unit + property + integration) on pull requests
- Generate coverage reports and fail if below thresholds
- Run extended property tests (1000+ iterations) nightly

### Manual Testing Checklist

While automated tests provide comprehensive coverage, manual verification should include:
- [ ] Logout from multiple devices/sessions
- [ ] Profile updates with various international phone formats
- [ ] Appointment rescheduling across different time zones
- [ ] Token cleanup job execution and monitoring
- [ ] Error messages are user-friendly and actionable
