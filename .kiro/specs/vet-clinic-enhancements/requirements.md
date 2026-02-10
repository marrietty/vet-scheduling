# Requirements Document: Vet Clinic Enhancements

## Introduction

This document specifies enhancements to an existing veterinary clinic scheduling system. The system currently supports user authentication, pet management, appointment scheduling, and clinic status management. These enhancements focus on improving authentication security, user profile management, client and pet data management, and appointment rescheduling capabilities.

## Glossary

- **System**: The veterinary clinic scheduling system
- **User**: A registered person in the system (can be a client or staff member)
- **Client**: A user who owns pets and books appointments
- **Pet**: An animal registered in the system with an owner
- **Appointment**: A scheduled time slot for a pet to receive veterinary services
- **Token**: A JWT authentication token used for API access
- **Token_Blacklist**: A database table storing invalidated tokens
- **Profile**: User account information including personal and contact details
- **Preferences**: User-specific settings and configuration options
- **Available_Slot**: A time period when appointments can be scheduled
- **Double_Booking**: Two or more appointments scheduled for the same time slot

## Requirements

### Requirement 1: Token-Based Logout

**User Story:** As a user, I want to securely logout of the system, so that my authentication token is invalidated and cannot be used after I log out.

#### Acceptance Criteria

1. WHEN a user requests logout, THE System SHALL add the user's current token to the Token_Blacklist
2. WHEN a blacklisted token is used for authentication, THE System SHALL reject the request and return an unauthorized error
3. WHEN adding a token to the blacklist, THE System SHALL store the token value and expiration timestamp
4. WHEN a logout request is received, THE System SHALL validate that the token exists and is currently valid before blacklisting
5. THE System SHALL provide an endpoint that accepts authenticated requests and invalidates the provided token

### Requirement 2: User Profile Viewing

**User Story:** As a user, I want to view my current profile information, so that I can see what information the system has about me.

#### Acceptance Criteria

1. WHEN a user requests their profile, THE System SHALL return the user's full name, email, phone, city, role, and account status
2. WHEN a user requests their profile, THE System SHALL NOT return the hashed password or other sensitive security information
3. THE System SHALL require valid authentication to access profile information
4. WHEN an unauthenticated request is made for profile information, THE System SHALL return an unauthorized error

### Requirement 3: User Profile Editing

**User Story:** As a user, I want to edit my profile information, so that I can keep my contact details and preferences up to date.

#### Acceptance Criteria

1. WHEN a user updates their full name, THE System SHALL validate the name is not empty and update the user record
2. WHEN a user updates their email, THE System SHALL validate the email format and ensure it is not already used by another user
3. WHEN a user updates their phone number, THE System SHALL validate the phone format and update the user record
4. WHEN a user updates their city, THE System SHALL update the city field in the user record
5. WHEN a user updates their preferences, THE System SHALL store the preferences data associated with the user
6. THE System SHALL require valid authentication to update profile information
7. WHEN a user attempts to update another user's profile, THE System SHALL reject the request with a forbidden error
8. WHEN profile update validation fails, THE System SHALL return descriptive error messages indicating which fields are invalid

### Requirement 4: Enhanced Client Profile with City

**User Story:** As a client, I want to store my city information in my profile, so that the clinic can better serve clients in different locations.

#### Acceptance Criteria

1. THE System SHALL support a city field in the user profile that accepts text values
2. WHEN a new user registers, THE System SHALL allow the city field to be optional
3. WHEN displaying user profiles, THE System SHALL include the city field if present
4. WHEN a user updates their city, THE System SHALL validate the city value is a non-empty string if provided

### Requirement 5: Enhanced Pet Profile Support

**User Story:** As a pet owner, I want to ensure my pet's species, breed, and notes are properly stored and displayed, so that veterinary staff have complete information about my pet.

#### Acceptance Criteria

1. THE System SHALL support species, breed, and notes fields for all pet records
2. WHEN creating a pet, THE System SHALL require species and allow breed and notes to be optional
3. WHEN updating a pet, THE System SHALL validate that species is not empty if provided
4. WHEN retrieving pet information, THE System SHALL include species, breed, and notes fields in the response
5. THE System SHALL allow notes to contain multi-line text and special characters

### Requirement 6: Appointment Rescheduling

**User Story:** As a client, I want to reschedule my pet's appointment to a different date and time, so that I can adjust to changes in my schedule.

#### Acceptance Criteria

1. WHEN a user requests to reschedule an appointment, THE System SHALL validate the user owns the pet associated with the appointment
2. WHEN rescheduling an appointment, THE System SHALL require both new start time and end time
3. WHEN rescheduling an appointment, THE System SHALL validate the new time slot does not conflict with existing appointments
4. WHEN rescheduling an appointment, THE System SHALL check that the clinic is open during the requested time
5. WHEN a valid reschedule request is received, THE System SHALL update the appointment's start time and end time
6. WHEN a reschedule request would create a double booking, THE System SHALL reject the request and return an error indicating the time slot is unavailable
7. WHEN an appointment is successfully rescheduled, THE System SHALL update the appointment's updated_at timestamp
8. THE System SHALL allow rescheduling only for appointments with status "scheduled" or "confirmed"
9. WHEN attempting to reschedule a completed or cancelled appointment, THE System SHALL reject the request with an appropriate error message

### Requirement 7: Token Blacklist Cleanup

**User Story:** As a system administrator, I want expired tokens to be automatically removed from the blacklist, so that the database does not grow indefinitely with old token records.

#### Acceptance Criteria

1. THE System SHALL store an expiration timestamp for each blacklisted token
2. WHEN checking if a token is blacklisted, THE System SHALL ignore tokens whose expiration timestamp has passed
3. THE System SHALL provide a mechanism to periodically remove expired tokens from the Token_Blacklist
4. WHEN removing expired tokens, THE System SHALL delete all records where the expiration timestamp is earlier than the current time

### Requirement 8: User Preferences Management

**User Story:** As a user, I want to save my preferences in the system, so that my experience can be customized to my needs.

#### Acceptance Criteria

1. THE System SHALL support storing user preferences as structured data
2. WHEN a user updates preferences, THE System SHALL validate the preferences data structure
3. WHEN a user retrieves their profile, THE System SHALL include their current preferences
4. WHEN a user has not set preferences, THE System SHALL return default or empty preferences
5. THE System SHALL allow preferences to be updated independently from other profile fields
