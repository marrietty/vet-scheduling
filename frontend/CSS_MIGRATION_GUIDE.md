# Tailwind to Plain CSS Migration Guide

## Overview
This guide helps you convert remaining Tailwind CSS classes to plain CSS classes throughout the application.

## Completed Files
- ✅ `package.json` - Removed Tailwind dependencies
- ✅ `tailwind.config.js` - Deleted
- ✅ `postcss.config.js` - Deleted
- ✅ `src/index.css` - Complete CSS system created
- ✅ `src/components/ui/Button.tsx`
- ✅ `src/components/ui/Input.tsx`
- ✅ `src/components/ui/Select.tsx`
- ✅ `src/components/ui/Card.tsx`
- ✅ `src/components/ui/Modal.tsx`
- ✅ `src/components/ui/Alert.tsx`
- ✅ `src/layouts/Navbar.tsx`
- ✅ `src/layouts/DashboardLayout.tsx`

## Common Tailwind to CSS Class Conversions

### Layout & Spacing
| Tailwind | Plain CSS |
|----------|-----------|
| `flex` | `flex` |
| `flex-col` | `flex-col` |
| `items-center` | `items-center` |
| `justify-between` | `justify-between` |
| `gap-2` | `gap-2` |
| `gap-4` | `gap-4` |
| `p-4` | `p-4` |
| `p-6` | `p-6` |
| `mt-4` | `mt-4` |
| `mb-4` | `mb-4` |

### Grid
| Tailwind | Plain CSS |
|----------|-----------|
| `grid` | `grid` |
| `grid-cols-1` | `grid-cols-1` |
| `grid-cols-2` | `grid-cols-2` |
| `grid-cols-3` | `grid-cols-3` |
| `md:grid-cols-2` | `md:grid-cols-2` |
| `lg:grid-cols-3` | `lg:grid-cols-3` |

### Text
| Tailwind | Plain CSS |
|----------|-----------|
| `text-sm` | `text-sm` |
| `text-base` | `text-base` |
| `text-lg` | `text-lg` |
| `text-xl` | `text-xl` |
| `text-2xl` | `text-2xl` |
| `font-medium` | `font-medium` |
| `font-semibold` | `font-semibold` |
| `font-bold` | `font-bold` |
| `text-center` | `text-center` |
| `text-gray-500` | `text-gray-500` |
| `text-gray-700` | `text-gray-700` |
| `text-gray-900` | `text-gray-900` |

### Width
| Tailwind | Plain CSS |
|----------|-----------|
| `w-full` | `w-full` |
| `max-w-md` | `max-w-md` |
| `max-w-lg` | `max-w-lg` |
| `max-w-xl` | `max-w-xl` |
| `max-w-2xl` | `max-w-2xl` |

### Complex Tailwind Classes to Replace

#### Background & Colors
```
bg-white → Use card class or inline style
bg-gray-50 → Already set on body
bg-blue-600 → Use btn-primary or inline style
text-blue-600 → Use inline style: style={{ color: 'var(--color-primary)' }}
```

#### Borders & Shadows
```
rounded-lg → Use card class or inline style: { borderRadius: 'var(--radius-lg)' }
shadow-md → Use card class
border border-gray-200 → inline style: { border: '1px solid var(--color-gray-200)' }
```

#### Positioning
```
fixed inset-0 → inline style: { position: 'fixed', inset: 0 }
absolute → inline style: { position: 'absolute' }
relative → inline style: { position: 'relative' }
```

#### Display
```
hidden → inline style: { display: 'none' }
block → inline style: { display: 'block' }
inline-flex → inline style: { display: 'inline-flex' }
```

## Files That Need Manual Conversion

### Components
- `src/components/ProtectedRoute.tsx`
- `src/components/auth/LoginForm.tsx`
- `src/components/auth/RegisterForm.tsx`
- `src/components/pets/PetCard.tsx`
- `src/components/pets/PetForm.tsx`
- `src/components/appointments/AppointmentCard.tsx`
- `src/components/appointments/AppointmentForm.tsx`
- `src/components/appointments/RescheduleForm.tsx`
- `src/components/profile/ProfileForm.tsx`

### Pages
- `src/pages/HomePage.tsx`
- `src/pages/LoginPage.tsx`
- `src/pages/RegisterPage.tsx`
- `src/pages/DashboardPage.tsx`
- `src/pages/PetsPage.tsx`
- `src/pages/AppointmentsPage.tsx`
- `src/pages/ProfilePage.tsx`
- `src/pages/AdminPage.tsx`

## Conversion Strategy

### 1. For Simple Utility Classes
Replace directly with the CSS class from the table above.

**Before:**
```tsx
<div className="flex items-center gap-4">
```

**After:**
```tsx
<div className="flex items-center gap-4">
```
(No change needed - these are already in our CSS)

### 2. For Complex Styling
Use inline styles with CSS variables.

**Before:**
```tsx
<div className="bg-white rounded-lg shadow-md p-6">
```

**After:**
```tsx
<div className="card">
  <div className="card-body">
```

### 3. For Color Classes
Use CSS variables in inline styles.

**Before:**
```tsx
<span className="text-blue-600">
```

**After:**
```tsx
<span style={{ color: 'var(--color-primary)' }}>
```

### 4. For Responsive Classes
Keep the responsive utility classes (they're in our CSS).

**Before:**
```tsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
```

**After:**
```tsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
```
(No change needed)

## Quick Reference: CSS Variables

```css
/* Colors */
--color-primary: #2563eb
--color-success: #16a34a
--color-danger: #dc2626
--color-warning: #f59e0b

/* Grays */
--color-gray-50 to --color-gray-900

/* Spacing */
--spacing-xs: 0.25rem
--spacing-sm: 0.5rem
--spacing-md: 1rem
--spacing-lg: 1.5rem
--spacing-xl: 2rem

/* Border Radius */
--radius-sm: 0.25rem
--radius-md: 0.5rem
--radius-lg: 0.75rem
--radius-full: 9999px

/* Shadows */
--shadow-sm, --shadow-md, --shadow-lg, --shadow-xl
```

## Testing After Conversion

1. Run `npm install` to update dependencies
2. Run `npm run dev` to start the dev server
3. Check each page visually
4. Verify responsive behavior
5. Test all interactive elements

## Notes

- The new CSS system uses CSS variables for consistency
- All utility classes are still available
- Components should look identical after conversion
- Performance may improve without Tailwind's large CSS bundle
