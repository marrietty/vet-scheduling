# Quick Start Guide - Vet Clinic Frontend

## 🚀 Get Started in 3 Steps

### Step 1: Install Dependencies

```bash
cd frontend
npm install
```

This will install:
- React 19 + TypeScript
- React Router v7
- Tailwind CSS
- date-fns
- jwt-decode
- And all dev dependencies

### Step 2: Configure Environment

Create `.env` file:

```bash
echo "VITE_API_BASE_URL=http://localhost:8000" > .env
```

### Step 3: Start Development Server

```bash
npm run dev
```

Visit `http://localhost:5173` 🎉

## 📋 Prerequisites

Make sure the backend is running:

```bash
cd backend
uvicorn app.main:app --reload
```

Backend should be accessible at `http://localhost:8000`

## 🧪 Test the Application

### 1. Register a New Account

- Go to `http://localhost:5173/register`
- Fill in:
  - Full Name: `John Doe`
  - Email: `john@example.com`
  - Password: `password123`
- Click "Create Account"

### 2. Add a Pet

- Navigate to "My Pets"
- Click "Add New Pet"
- Fill in:
  - Name: `Buddy`
  - Species: `Dog`
  - Breed: `Golden Retriever`
- Click "Add Pet"

### 3. Book an Appointment

- Navigate to "Appointments"
- Click "Book Appointment"
- Select your pet
- Choose service type
- Pick date and time
- Click "Book Appointment"

### 4. Test Admin Features (Optional)

Register with admin email (configured in backend `.env`):
- Email: `admin@vetclinic.com`
- Password: `admin123`

Access admin dashboard at `/admin`

## 🎨 Key Features to Test

- ✅ Login/Logout
- ✅ Profile Management
- ✅ Pet CRUD Operations
- ✅ Appointment Booking
- ✅ Appointment Rescheduling
- ✅ Admin Dashboard (if admin)

## 🐛 Common Issues

### Port Already in Use

```bash
# Kill process on port 5173
npx kill-port 5173
```

### API Connection Failed

Check:
1. Backend is running on port 8000
2. `.env` file has correct `VITE_API_BASE_URL`
3. CORS is configured in backend

### Module Not Found

```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

## 📚 Next Steps

- Read `README.md` for full documentation
- Check `backend/README.md` for API reference
- Explore the code structure in `src/`

## 🎯 Project Structure Overview

```
src/
├── hooks/          # API calls (THE LOGIC LAYER)
├── components/     # UI components
├── pages/          # Route pages
├── layouts/        # Page layouts
├── contexts/       # React contexts
├── types/          # TypeScript types
└── lib/            # Utilities
```

## 💡 Tips

1. **Hot Reload**: Changes auto-reload in dev mode
2. **TypeScript**: Hover over variables for type info
3. **Tailwind**: Use Tailwind classes for styling
4. **API Calls**: Always use custom hooks, never fetch directly

Happy coding! 🚀
