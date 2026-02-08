# Vet Clinic Scheduling System - Backend API

A REST API backend for a veterinary clinic scheduling system built with FastAPI, SQLModel, and PostgreSQL. The system implements role-based access control with two user types: **Admin** (clinic owner) and **Pet Owners** (customers).

## 🏗️ Architecture

The application follows a strict **three-layer architecture**:

```
┌─────────────────────────────────────┐
│   Router Layer (API Endpoints)      │  ← HTTP Request/Response
├─────────────────────────────────────┤
│   Service Layer (Business Logic)    │  ← Validation, Rules
├─────────────────────────────────────┤
│   Repository Layer (Data Access)    │  ← Database Queries
├─────────────────────────────────────┤
│   Database Layer (SQLModel ORM)     │  ← PostgreSQL/NeonDB
└─────────────────────────────────────┘
```

## 🚀 Features

### Authentication & Authorization
- JWT-based authentication
- Role-based access control (Admin vs Pet Owner)
- Automatic role assignment based on email
- Bcrypt password hashing

### Pet Management
- Register and manage pets
- Track vaccination status (valid, expired, unknown)
- Store medical history as JSON
- Role-based filtering (owners see only their pets, admins see all)

### Appointment Booking
- Create appointments with automatic end time calculation
- Service types: vaccination (30min), routine (45min), surgery (120min), emergency (15min)
- Overlap detection for double-booking prevention
- Status management: pending → confirmed → completed
- Filtering by status, date range

### Clinic Status Management
- Public endpoint to check if clinic is open
- Admin-only status updates (open, close, closing_soon)
- Prevents appointment creation when clinic is closed

## 📋 Technology Stack

- **Framework**: FastAPI (Python 3.12+)
- **Database**: NeonDB (PostgreSQL) via SQLModel (synchronous ORM)
- **Authentication**: JWT with python-jose and passlib[bcrypt]
- **Validation**: Pydantic (built into SQLModel)

## 📁 Project Structure

```
backend/
├── app/
│   ├── main.py                    # FastAPI app entry point
│   ├── core/                      # Core configuration
│   │   ├── config.py             # Environment config
│   │   └── database.py           # Database setup
│   ├── common/                    # Shared utilities
│   │   ├── enums.py              # String enums
│   │   ├── exceptions.py         # Custom HTTP exceptions
│   │   ├── dependencies.py       # FastAPI dependencies (auth, RBAC)
│   │   └── utils.py              # Helper functions
│   ├── infrastructure/            # External services
│   │   └── auth.py               # JWT & password hashing
│   └── features/                  # Feature modules
│       ├── auth/                  # Authentication
│       │   ├── router.py
│       │   ├── schemas.py
│       │   └── service.py
│       ├── users/                 # User management
│       │   ├── models.py
│       │   └── repository.py
│       ├── pets/                  # Pet management
│       │   ├── models.py
│       │   ├── schemas.py
│       │   ├── repository.py
│       │   ├── service.py
│       │   └── router.py
│       ├── appointments/          # Appointment booking
│       │   ├── models.py
│       │   ├── schemas.py
│       │   ├── repository.py
│       │   ├── service.py
│       │   └── router.py
│       └── clinic/                # Clinic status
│           ├── models.py
│           ├── schemas.py
│           ├── repository.py
│           ├── service.py
│           └── router.py
└── .env                          # Environment variables
```

## 🛠️ Setup Guide

### Prerequisites

- Python 3.12 or higher
- PostgreSQL database (or NeonDB account)
- pip or uv package manager

### 1. Clone the Repository

```bash
git clone <repository-url>
cd vet-scheduling/backend
```

### 2. Create Virtual Environment

```bash
# Using Python venv
python -m venv .venv

# Activate on Windows
.venv\Scripts\activate

# Activate on macOS/Linux
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install fastapi uvicorn sqlmodel psycopg2-binary python-jose[cryptography] passlib[bcrypt] python-dotenv
```

Or if you have a `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the `backend` directory:

```env
# Database Configuration
DATABASE_URL=postgresql://username:password@host:port/database?sslmode=require

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440

# Admin Configuration
ADMIN_EMAIL=admin@vetclinic.com

# CORS Configuration (comma-separated origins)
BACKEND_CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Environment
ENVIRONMENT=development

# Logging
LOG_LEVEL=INFO

# Timezone
CLINIC_TIMEZONE=Asia/Manila
```

#### Environment Variables Explained

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `JWT_SECRET_KEY` | Secret key for JWT token signing | `your-super-secret-jwt-key-change-in-production` |
| `JWT_ALGORITHM` | JWT signing algorithm | `HS256` |
| `JWT_EXPIRE_MINUTES` | Token expiration time in minutes | `1440` (24 hours) |
| `ADMIN_EMAIL` | Email that gets admin role on registration | `admin@vetclinic.com` |
| `BACKEND_CORS_ORIGINS` | Allowed CORS origins (comma-separated) | `*` |
| `ENVIRONMENT` | Environment mode | `development` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `CLINIC_TIMEZONE` | Clinic timezone | `Asia/Manila` |

### 5. Initialize Database

The database tables are created automatically on first run. Just start the application:

```bash
uvicorn app.main:app --reload
```

You should see:
```
Initializing database tables...
Database tables initialized successfully.
```

### 6. Access the API

Once running, access:

- **API Documentation (Swagger UI)**: http://localhost:8000/docs
- **Alternative Documentation (ReDoc)**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json
- **Health Check**: http://localhost:8000/health

## 📚 API Endpoints

### Authentication (`/api/v1/auth`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/register` | Register new user (auto-login) | No |
| POST | `/login` | Login existing user | No |

### Pets (`/api/v1/pets`)

| Method | Endpoint | Description | Auth Required | Admin Only |
|--------|----------|-------------|---------------|------------|
| POST | `/` | Create new pet | Yes | No |
| GET | `/` | List pets (filtered by role) | Yes | No |
| GET | `/{pet_id}` | Get specific pet | Yes | No |
| PATCH | `/{pet_id}` | Update pet | Yes | No |
| DELETE | `/{pet_id}` | Delete pet | Yes | No |

### Appointments (`/api/v1/appointments`)

| Method | Endpoint | Description | Auth Required | Admin Only |
|--------|----------|-------------|---------------|------------|
| POST | `/` | Create appointment | Yes | No |
| GET | `/` | List appointments (with filters) | Yes | No |
| PATCH | `/{id}/status` | Update appointment status | Yes | **Yes** |
| DELETE | `/{id}` | Cancel appointment | Yes | No |

**Query Parameters for GET:**
- `status`: Filter by status (pending, confirmed, cancelled, completed)
- `from_date`: Filter appointments starting on or after this date
- `to_date`: Filter appointments starting on or before this date

### Clinic Status (`/api/v1/clinic`)

| Method | Endpoint | Description | Auth Required | Admin Only |
|--------|----------|-------------|---------------|------------|
| GET | `/status` | Get clinic status | **No** | No |
| PATCH | `/status` | Update clinic status | Yes | **Yes** |

## 🔐 Authentication Flow

### Password Requirements

- **Minimum length**: 8 characters
- **Maximum length**: 64 characters
- Passwords are hashed using bcrypt before storage

### 1. Register a New User

```bash
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Error Responses:**
- `400 Bad Request`: Password too short/long or email already registered
- `422 Unprocessable Entity`: Invalid email format

### 2. Login

```bash
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

### 3. Use Token in Requests

```bash
GET /api/v1/pets
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## 👤 User Roles

### Admin
- Email matches `ADMIN_EMAIL` environment variable
- Full access to all resources
- Can manage all pets and appointments
- Can update clinic status
- Can confirm/complete appointments

### Pet Owner
- All other registered users
- Can only manage their own pets
- Can only view/cancel their own appointments
- Cannot update clinic status
- Cannot confirm/complete appointments

## 🧪 Testing the API

### Using Swagger UI (Recommended)

1. Navigate to http://localhost:8000/docs
2. Click "Authorize" button
3. Register/login to get a token
4. Paste token in the authorization dialog
5. Test endpoints interactively

### Using cURL

```bash
# Register admin user
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@vetclinic.com","password":"admin123"}'

# Create a pet
curl -X POST http://localhost:8000/api/v1/pets \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Buddy",
    "species": "dog",
    "breed": "Golden Retriever",
    "date_of_birth": "2020-05-15"
  }'

# Create an appointment
curl -X POST http://localhost:8000/api/v1/appointments \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "pet_id": "PET_UUID_HERE",
    "start_time": "2024-12-25T10:00:00",
    "service_type": "routine",
    "notes": "Annual checkup"
  }'
```

## 🗄️ Database Schema

### Users Table
- `id` (UUID, PK)
- `email` (String, Unique)
- `hashed_password` (String)
- `role` (String: "admin" or "pet_owner")
- `is_active` (Boolean)
- `created_at` (DateTime)

### Pets Table
- `id` (UUID, PK)
- `name` (String)
- `species` (String)
- `breed` (String, Optional)
- `date_of_birth` (Date, Optional)
- `last_vaccination` (DateTime, Optional)
- `medical_history` (JSON)
- `owner_id` (UUID, FK → users.id)
- `created_at` (DateTime)
- `updated_at` (DateTime)

### Appointments Table
- `id` (UUID, PK)
- `pet_id` (UUID, FK → pets.id)
- `user_id` (UUID, FK → users.id)
- `start_time` (DateTime)
- `end_time` (DateTime)
- `service_type` (String)
- `status` (String)
- `notes` (String, Optional)
- `created_at` (DateTime)
- `updated_at` (DateTime)

### Clinic Status Table
- `id` (Integer, PK, always 1)
- `status` (String: "open", "close", "closing_soon")
- `updated_at` (DateTime)

## 🔧 Business Rules

### Appointment Creation
1. Pet must exist and be owned by the user (or user is admin)
2. Start time must be in the future
3. Clinic must not be closed
4. Time slot must not overlap with existing pending/confirmed appointments
5. End time is automatically calculated based on service type

### Service Durations
- **Vaccination**: 30 minutes
- **Routine**: 45 minutes
- **Surgery**: 120 minutes
- **Emergency**: 15 minutes

### Vaccination Status
- **Valid**: Last vaccination within 365 days
- **Expired**: Last vaccination more than 365 days ago
- **Unknown**: No vaccination date recorded

### Appointment Status Transitions
- **Pending** → Confirmed (admin only)
- **Confirmed** → Completed (admin only)
- **Any** → Cancelled (owner or admin, except completed)
- **Completed/Cancelled** → Cannot be changed

## 🐛 Troubleshooting

### Database Schema Issues

```
psycopg2.errors.UndefinedColumn: column appointments.user_id does not exist
```

**Solution**: The database schema is out of sync. Run the migration script:

```bash
cd backend
python migrate_add_user_id.py
```

Or for development (deletes all data):
```bash
python reset_database.py
```

See `DATABASE_MANAGEMENT.md` for detailed instructions.

### Password Validation Errors

```
400 Bad Request: Password must be at least 8 characters long
```

**Solution**: Ensure password is between 8-64 characters. Bcrypt has a 72-byte limit, so we enforce 64 characters for safety.

### Bcrypt Errors

```
AttributeError: module 'bcrypt' has no attribute '__about__'
ValueError: password cannot be longer than 72 bytes
```

**Solution**: The application now uses bcrypt directly instead of through passlib to avoid version detection issues. This is already implemented in the code.

If you still see errors:
1. Ensure bcrypt is installed: `pip install bcrypt==4.1.3`
2. Restart the application
3. Check logs with `LOG_LEVEL=DEBUG` for detailed information

**Note**: The fix uses direct bcrypt implementation which is more reliable and provides better error messages.

### Database Connection Issues

```
ERROR: could not connect to server
```

**Solution**: Check your `DATABASE_URL` in `.env` file. Ensure:
- Database server is running
- Credentials are correct
- SSL mode is properly configured for NeonDB

### Import Errors

```
ModuleNotFoundError: No module named 'fastapi'
```

**Solution**: Ensure virtual environment is activated and dependencies are installed:
```bash
pip install -r requirements.txt
```

### JWT Token Errors

```
401 Unauthorized: Could not validate credentials
```

**Solution**: 
- Check if token is expired (default: 24 hours)
- Verify `JWT_SECRET_KEY` hasn't changed
- Ensure token is properly formatted in Authorization header

## 📝 Development

### Running in Development Mode

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Running in Production

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Code Style

The project follows:
- **DRY** (Don't Repeat Yourself)
- **KISS** (Keep It Simple)
- Python type hints everywhere
- Comprehensive docstrings

## 📄 License

[Your License Here]

## 👥 Contributors

[Your Name/Team]

## 📞 Support

For issues and questions, please open an issue on the repository.
