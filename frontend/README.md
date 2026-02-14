# Vet Clinic Frontend

A modern, responsive React application for managing veterinary clinic operations, built with TypeScript and vanilla CSS.

## 🚀 Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

The application will be available at `http://localhost:5173`

## 📋 Prerequisites

- Node.js 18+ or higher
- npm 9+ or higher
- Backend API running on `http://localhost:8000`

## 🏗️ Architecture

### Clean, Scalable Structure

```
frontend/
├── src/
│   ├── components/          # Feature-based components
│   │   ├── ui/             # Reusable UI components
│   │   ├── auth/           # Authentication components
│   │   ├── pets/           # Pet management components
│   │   ├── appointments/   # Appointment components
│   │   └── profile/        # Profile components
│   ├── contexts/           # React contexts
│   ├── hooks/              # Custom hooks (API logic layer)
│   ├── layouts/            # Page layouts
│   ├── lib/                # Utilities
│   ├── pages/              # Route pages
│   ├── types/              # TypeScript types
│   ├── index.css           # CSS system
│   ├── main.tsx            # App entry point
│   └── App.tsx             # Routing configuration
├── public/                 # Static assets
└── package.json            # Dependencies
```

## 🎨 Styling System

### Vanilla CSS with CSS Variables

No CSS framework dependencies! The app uses a custom CSS system with:

- **CSS Variables** for consistent theming
- **Component Classes** for reusable patterns
- **Utility Classes** for common layouts
- **Responsive Design** with media queries

#### CSS Variables
```css
--color-primary: #2563eb
--color-success: #16a34a
--color-danger: #dc2626
--spacing-md: 1rem
--radius-lg: 0.75rem
--shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1)
```

#### Component Classes
```css
.btn, .btn-primary, .btn-sm
.input, .input-group, .input-label
.card, .card-header, .card-body
.modal, .modal-backdrop
.alert, .alert-success
.badge, .badge-primary
```

## 🎯 Key Features

### Authentication & Authorization
- User registration with validation
- Secure login with JWT tokens
- Token-based logout
- Protected routes
- Role-based access control (Admin/Pet Owner)

### User Profile Management
- View and update profile information
- Email and phone validation
- City and preferences support

### Pet Management
- Add, edit, and delete pets
- Track species, breed, and notes
- Vaccination status tracking
- Date of birth and medical history

### Appointment Booking
- Book appointments with service type selection
- View appointments with status filtering
- Reschedule appointments
- Cancel appointments with confirmation
- Service types: Vaccination, Routine, Surgery, Emergency

### Admin Dashboard
- Clinic status management
- Confirm/reject appointments
- Complete appointments
- View statistics
- Manage all pets and appointments

## 🔧 Technology Stack

- **React 19** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **React Router v7** - Client-side routing
- **Vanilla CSS** - Styling with CSS variables
- **date-fns** - Date formatting and manipulation
- **jwt-decode** - JWT token parsing

## 📁 Project Structure Explained

### `/hooks` - The Logic Layer

All API calls are centralized in custom hooks:

```typescript
// usePets.ts handles ALL pet-related API calls
const { pets, createPet, updatePet, deletePet, isLoading, error } = usePets();
```

Benefits:
- Single source of truth for each backend entity
- Reusable across multiple components
- Consistent error handling
- Automatic loading state management
- Prevents redundant API calls

### `/components` - Feature-Based Organization

Components are organized by feature, not by type:

```
components/
├── ui/              # Reusable atoms (Button, Input, Card)
├── auth/            # LoginForm, RegisterForm
├── pets/            # PetCard, PetForm
├── appointments/    # AppointmentCard, AppointmentForm
└── profile/         # ProfileForm
```

### `/types` - Backend Schema Alignment

TypeScript interfaces match backend schemas exactly:

```typescript
export interface Pet {
  id: string;
  name: string;
  species: string;
  breed: string | null;
  // ... matches backend API
}
```

### `/pages` - Lean Route Components

Pages compose features and layouts:

```typescript
export function PetsPage() {
  const { pets, createPet } = usePets(); // Logic from hook
  return (
    <DashboardLayout>
      <PetCard /> {/* UI from components */}
    </DashboardLayout>
  );
}
```

## 🔐 Authentication Flow

1. User submits credentials (register/login)
2. Backend returns JWT token
3. Token stored in localStorage
4. User profile fetched and stored in context
5. Protected routes check authentication
6. Token sent with all API requests
7. Logout blacklists token on backend

## 🌐 API Integration

### Base URL Configuration

Set the API base URL in `.env`:

```env
VITE_API_BASE_URL=http://localhost:8000
```

### API Client

All API calls use the custom API client (`src/lib/api-client.ts`):

```typescript
import { apiClient } from '../lib/api-client';

// Automatically includes JWT token
const response = await apiClient.get('/api/v1/pets');
```

### Custom Hooks Pattern

```typescript
// ✅ CORRECT - Use custom hooks
const { pets, createPet, isLoading, error } = usePets();

// ❌ WRONG - Don't call API directly
fetch('/api/v1/pets')
```

## 📱 Responsive Design

The application is fully responsive:

- **Mobile** (< 768px): Single column, touch-friendly
- **Tablet** (768px - 1024px): 2-column grid
- **Desktop** (> 1024px): 3-column grid, full navigation

## 🧪 Development Guidelines

### Adding a New Feature

1. **Define Types** in `/types/index.ts`
2. **Create Hook** in `/hooks` for API calls
3. **Build Components** in `/components`
4. **Add Page** in `/pages`
5. **Register Route** in `App.tsx`

### Code Style

- TypeScript strict mode enabled
- ESLint configured for React
- camelCase for variables
- PascalCase for components
- One component per file

### Error Handling

Errors are handled at the hook level:

```typescript
const { error } = usePets();

{error && <Alert type="error">{error}</Alert>}
```

## 🚦 Available Scripts

```bash
# Development
npm run dev          # Start dev server with hot reload

# Production
npm run build        # Build for production
npm run preview      # Preview production build

# Code Quality
npm run lint         # Run ESLint
```

## 🔗 API Endpoints

All endpoints are documented in `backend/README.md`:

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login user
- `POST /api/v1/auth/logout` - Logout and blacklist token

### Users
- `GET /api/v1/users/profile` - Get current user profile
- `PATCH /api/v1/users/profile` - Update user profile

### Pets
- `GET /api/v1/pets` - List all pets
- `POST /api/v1/pets` - Create new pet
- `GET /api/v1/pets/{id}` - Get pet by ID
- `PATCH /api/v1/pets/{id}` - Update pet
- `DELETE /api/v1/pets/{id}` - Delete pet

### Appointments
- `GET /api/v1/appointments` - List appointments (with filters)
- `POST /api/v1/appointments` - Create appointment
- `PATCH /api/v1/appointments/{id}/status` - Update status (admin)
- `PATCH /api/v1/appointments/{id}/reschedule` - Reschedule
- `DELETE /api/v1/appointments/{id}` - Cancel appointment

### Clinic
- `GET /api/v1/clinic/status` - Get clinic status (public)
- `PATCH /api/v1/clinic/status` - Update status (admin)

## 🐛 Troubleshooting

### API Connection Issues

**Error**: `Failed to fetch`

**Solution**: 
- Ensure backend is running on `http://localhost:8000`
- Check `VITE_API_BASE_URL` in `.env`
- Verify CORS settings in backend

### Authentication Issues

**Error**: `401 Unauthorized`

**Solution**:
- Token may be expired or blacklisted
- Try logging out and logging in again
- Check browser localStorage for token

### Build Errors

**Error**: `Module not found`

**Solution**:
```bash
rm -rf node_modules package-lock.json
npm install
```

### Port Already in Use

**Error**: `Port 5173 is already in use`

**Solution**:
```bash
# Windows
npx kill-port 5173

# Linux/Mac
lsof -ti:5173 | xargs kill -9
```

## 🎯 Environment Variables

Create a `.env` file in the frontend directory:

```env
# API Configuration
VITE_API_BASE_URL=http://localhost:8000

# Optional: Enable debug mode
VITE_DEBUG=false
```

## 📦 Dependencies

### Production Dependencies
- `react` - UI library
- `react-dom` - React DOM renderer
- `react-router-dom` - Routing
- `jwt-decode` - JWT parsing
- `date-fns` - Date utilities

### Development Dependencies
- `typescript` - Type checking
- `vite` - Build tool
- `eslint` - Code linting
- `@vitejs/plugin-react-swc` - Fast refresh

## 🚀 Deployment

### Build for Production

```bash
npm run build
```

Output will be in the `dist/` directory.

### Deploy to Vercel

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel
```

### Deploy to Netlify

```bash
# Install Netlify CLI
npm i -g netlify-cli

# Deploy
netlify deploy --prod --dir=dist
```

### Environment Variables for Production

Set these in your hosting platform:

```
VITE_API_BASE_URL=https://your-api-domain.com
```

## 📚 Additional Documentation

- `QUICKSTART.md` - Quick start guide
- `FEATURES.md` - Complete feature list
- `CSS_MIGRATION_GUIDE.md` - CSS conversion guide
- `CONVERSION_COMPLETE.md` - Tailwind to CSS migration summary

## 🤝 Contributing

1. Follow the existing code structure
2. Use TypeScript for all new files
3. Add types for all props and state
4. Use custom hooks for API calls
5. Keep components small and focused
6. Write descriptive commit messages

## 📄 License

[Your License Here]

## 👥 Support

For issues and questions:
1. Check this README
2. Review `backend/README.md` for API details
3. Check browser console for errors
4. Review network tab for API issues

## 🎉 Success Checklist

- [ ] Dependencies installed (`npm install`)
- [ ] Backend running on port 8000
- [ ] Frontend running on port 5173
- [ ] Can register new user
- [ ] Can login successfully
- [ ] Can add pets
- [ ] Can book appointments
- [ ] Can update profile
- [ ] Admin features work (if admin user)

---

Built with ❤️ using React, TypeScript, and Vanilla CSS
