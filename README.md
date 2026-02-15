# Vet Clinic Scheduling System

A full-stack web application for veterinary clinic management, featuring appointment scheduling, pet management, user profiles, and admin controls.

## 🎯 Overview

This system provides a complete solution for veterinary clinics to manage their operations online. Pet owners can register, add their pets, book appointments, and manage their profiles. Administrators can manage clinic status, confirm appointments, and oversee all operations.

## ✨ Key Features

- **User Authentication** - Secure registration and login with JWT
- **Pet Management** - Add, edit, and track pet information
- **Appointment Booking** - Schedule and manage appointments
- **Admin Dashboard** - Clinic status and appointment management
- **Profile Management** - Update user information and preferences
- **Responsive Design** - Works on mobile, tablet, and desktop

## 🏗️ Architecture

### Backend (FastAPI + PostgreSQL)
- RESTful API with FastAPI
- PostgreSQL database with SQLModel ORM
- JWT authentication with token blacklisting
- 3-layer architecture (Router → Service → Repository)
- 197 passing tests with 76% coverage

### Frontend (React + TypeScript)
- React 19 with TypeScript
- Vite for fast development and builds
- React Router v7 for routing
- Vanilla CSS with CSS variables
- Feature-based component architecture
- Custom hooks for API logic

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Node.js 18+
- PostgreSQL database (or NeonDB account)

### 1. Clone Repository

```bash
git clone <repository-url>
cd vet-clinic-scheduling
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate

# Install dependencies
pip install fastapi uvicorn sqlmodel psycopg2-binary python-jose[cryptography] passlib[bcrypt] python-dotenv

# Create .env file
# Copy .env.example and update with your database credentials

# Start backend server
uvicorn app.main:app --reload
```

Backend will be available at `http://localhost:8000`

### 3. Frontend Setup

Open a new terminal:

```bash
cd frontend

# Install dependencies
npm install

# Create .env file
echo "VITE_API_BASE_URL=http://localhost:8000" > .env

# Start frontend server
npm run dev
```

Frontend will be available at `http://localhost:5173`

## 📁 Project Structure

```
vet-clinic-scheduling/
├── backend/                 # FastAPI Backend
│   ├── app/
│   │   ├── features/       # Feature modules
│   │   │   ├── auth/       # Authentication + Token blacklist
│   │   │   ├── users/      # User profiles
│   │   │   ├── pets/       # Pet management
│   │   │   ├── appointments/ # Appointments + Rescheduling
│   │   │   └── clinic/     # Clinic status
│   │   ├── core/           # Configuration
│   │   ├── common/         # Shared utilities
│   │   └── infrastructure/ # External services
│   ├── tests/              # 197 passing tests
│   └── .env                # Configuration
│
├── frontend/               # React Frontend
│   ├── src/
│   │   ├── components/    # UI Components
│   │   ├── hooks/         # API Logic Layer
│   │   ├── pages/         # Route pages
│   │   ├── layouts/       # Page layouts
│   │   ├── contexts/      # React contexts
│   │   └── types/         # TypeScript types
│   └── .env               # Configuration
│
├── docs/                  # Documentation
│   ├── prd.md            # Product requirements
│   └── sql.md            # Database schema
│
├── INSTALLATION.md        # Complete setup guide
├── PROJECT_SUMMARY.md     # Project overview
└── README.md             # This file
```

## 🔗 API Documentation

Once the backend is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 🎨 Technology Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLModel** - SQL database ORM
- **PostgreSQL** - Relational database
- **JWT** - Token-based authentication
- **Bcrypt** - Password hashing
- **Pydantic** - Data validation
- **Pytest** - Testing framework

### Frontend
- **React 19** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool
- **React Router v7** - Routing
- **Vanilla CSS** - Styling with CSS variables
- **date-fns** - Date handling
- **jwt-decode** - JWT parsing

## 📊 Project Statistics

- **Total Files**: 100+
- **Lines of Code**: ~10,000+
- **API Endpoints**: 17
- **Database Tables**: 5
- **Backend Tests**: 197 (all passing)
- **Test Coverage**: 76%
- **UI Components**: 20+
- **Pages**: 8

## 🔐 Default Credentials

### Admin Account

To create an admin account, register with the admin email:

```
Email: admin@vetclinic.com
Password: [your-password]
```

The first user registered with the admin email becomes an admin automatically.

## 🧪 Testing

### Backend Tests

```bash
cd backend
pytest

# With coverage
pytest --cov=app --cov-report=html
```

### Frontend Testing

```bash
cd frontend
npm run lint
```

## 🌐 API Endpoints

### Authentication (`/api/v1/auth`)
- `POST /register` - Register new user
- `POST /login` - Login user
- `POST /logout` - Logout and blacklist token

### Users (`/api/v1/users`)
- `GET /profile` - Get current user profile
- `PATCH /profile` - Update user profile

### Pets (`/api/v1/pets`)
- `GET /` - List pets
- `POST /` - Create pet
- `GET /{id}` - Get pet
- `PATCH /{id}` - Update pet
- `DELETE /{id}` - Delete pet

### Appointments (`/api/v1/appointments`)
- `GET /` - List appointments (with filters)
- `POST /` - Create appointment
- `PATCH /{id}/status` - Update status (admin)
- `PATCH /{id}/reschedule` - Reschedule appointment
- `DELETE /{id}` - Cancel appointment

### Clinic (`/api/v1/clinic`)
- `GET /status` - Get clinic status (public)
- `PATCH /status` - Update status (admin)

## 🎯 User Roles

### Pet Owner
- Register and manage account
- Add and manage pets
- Book appointments
- Reschedule own appointments
- Cancel own appointments
- Update profile

### Admin
- All pet owner features
- View all appointments and pets
- Confirm/reject appointments
- Complete appointments
- Update clinic status
- View statistics

## 🚀 Deployment

### Backend Deployment

Recommended platforms:
- Railway
- Render
- Heroku
- AWS (EC2, ECS, Lambda)

Requirements:
- Python 3.12+
- PostgreSQL database
- Environment variables configured

### Frontend Deployment

Recommended platforms:
- Vercel
- Netlify
- AWS S3 + CloudFront
- GitHub Pages

Requirements:
- Node.js 18+
- Environment variable for API URL

### Database

Recommended providers:
- NeonDB (PostgreSQL)
- Supabase
- AWS RDS
- Railway PostgreSQL

## 📚 Documentation

### Backend
- `backend/README.md` - Complete backend guide
- `backend/DATABASE_MANAGEMENT.md` - Database guide
- API docs at `/docs` (Swagger UI)

### Frontend
- `frontend/README.md` - Complete frontend guide
- `frontend/QUICKSTART.md` - Quick start guide
- `frontend/FEATURES.md` - Feature list
- `frontend/CSS_MIGRATION_GUIDE.md` - CSS system guide

### General
- `INSTALLATION.md` - Complete setup guide
- `PROJECT_SUMMARY.md` - Project overview
- `docs/prd.md` - Product requirements
- `docs/sql.md` - Database schema

## 🐛 Troubleshooting

### Backend Issues

**Database Connection Error**
```
ERROR: could not connect to server
```
Solution: Check `DATABASE_URL` in `backend/.env`

**Module Not Found**
```
ModuleNotFoundError: No module named 'fastapi'
```
Solution: Activate virtual environment and install dependencies

### Frontend Issues

**API Connection Failed**
```
Failed to fetch
```
Solution: Ensure backend is running and `VITE_API_BASE_URL` is correct

**Module Not Found**
```
Cannot find module 'react'
```
Solution: Run `npm install` in frontend directory

## 🔧 Development Workflow

### Running Both Servers

**Terminal 1 - Backend**:
```bash
cd backend
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
uvicorn app.main:app --reload
```

**Terminal 2 - Frontend**:
```bash
cd frontend
npm run dev
```

### Making Changes

1. **Backend Changes**: 
   - Edit files in `backend/app/`
   - Server auto-reloads
   - Check `http://localhost:8000/docs` for API updates

2. **Frontend Changes**:
   - Edit files in `frontend/src/`
   - Browser auto-reloads
   - Check browser console for errors

## 🎓 Best Practices

### Code Quality
- TypeScript strict mode
- ESLint configuration
- Consistent code style
- Comprehensive documentation
- Error handling
- Type safety

### Architecture
- Separation of concerns
- DRY principle
- SOLID principles
- Clean code
- Scalable structure

### Security
- Input validation
- Authentication
- Authorization
- Secure storage
- HTTPS ready

## 📈 Performance

### Backend
- Async/await support
- Database connection pooling
- Efficient queries (ORM)
- Background tasks (token cleanup)

### Frontend
- Code splitting
- Lazy loading
- Optimized re-renders
- Fast build (Vite)
- Small bundle size (~15KB CSS)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write/update tests
5. Update documentation
6. Submit a pull request

## 📄 License

[Your License Here]

## 👥 Authors

[Your Name/Team]

## 🙏 Acknowledgments

- FastAPI for the excellent web framework
- React team for the UI library
- All open source contributors

## 📞 Support

For issues and questions:
1. Check documentation
2. Review code comments
3. Check backend/frontend logs
4. Open an issue on the repository

## 🎉 Success Checklist

- [ ] Backend running on port 8000
- [ ] Frontend running on port 5173
- [ ] Can access API docs at `/docs`
- [ ] Can register new user
- [ ] Can login successfully
- [ ] Can add pets
- [ ] Can book appointments
- [ ] Can update profile
- [ ] Admin features work
- [ ] All tests passing

## 🌟 Features Roadmap

### Completed ✅
- User authentication and authorization
- Pet management (CRUD)
- Appointment booking and management
- Profile management
- Admin dashboard
- Clinic status management
- Token blacklisting
- Appointment rescheduling
- Background token cleanup

### Future Enhancements 🚀
- [ ] Email notifications
- [ ] SMS reminders
- [ ] Calendar view for appointments
- [ ] Pet photo uploads
- [ ] Medical records and prescriptions
- [ ] Payment integration
- [ ] Multi-clinic support
- [ ] Mobile app
- [ ] Real-time notifications
- [ ] Dark mode

## 📊 Project Status

**Status**: ✅ **PRODUCTION READY**

- All core features implemented
- All tests passing
- Complete documentation
- Security best practices
- Responsive design
- Error handling
- Ready for deployment

---

**Built with ❤️ using FastAPI, React, TypeScript, and Vanilla CSS**

**Last Updated**: February 2026
