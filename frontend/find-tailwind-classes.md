# Find Tailwind Classes Script

## Quick Command to Find Tailwind Classes

Run this in the frontend directory to find all files with Tailwind classes:

### Windows (PowerShell)
```powershell
Get-ChildItem -Path src -Recurse -Include *.tsx,*.ts | Select-String -Pattern "className=.*\b(bg-|text-|border-|rounded-|shadow-|px-|py-|mt-|mb-|ml-|mr-|w-|h-|flex|grid|absolute|relative|fixed|hidden|block|inline)" | Select-Object -Property Path -Unique
```

### Windows (CMD)
```cmd
findstr /s /i /r "className=.*bg-\|text-\|border-\|rounded-\|shadow-\|px-\|py-\|mt-\|mb-\|ml-\|mr-\|w-\|h-\|flex\|grid" src\*.tsx src\*.ts
```

### Linux/Mac
```bash
grep -r "className=" src/ | grep -E "(bg-|text-|border-|rounded-|shadow-|px-|py-|mt-|mb-|ml-|mr-|w-|h-|flex|grid|absolute|relative|fixed)" | cut -d: -f1 | sort -u
```

## Manual Check List

Check these files for Tailwind classes:

### Components
- [ ] src/components/ProtectedRoute.tsx
- [ ] src/components/auth/LoginForm.tsx
- [ ] src/components/auth/RegisterForm.tsx
- [ ] src/components/pets/PetCard.tsx
- [ ] src/components/pets/PetForm.tsx
- [ ] src/components/appointments/AppointmentCard.tsx
- [ ] src/components/appointments/AppointmentForm.tsx
- [ ] src/components/appointments/RescheduleForm.tsx
- [ ] src/components/profile/ProfileForm.tsx

### Pages
- [ ] src/pages/HomePage.tsx
- [ ] src/pages/LoginPage.tsx
- [ ] src/pages/RegisterPage.tsx
- [ ] src/pages/DashboardPage.tsx
- [ ] src/pages/PetsPage.tsx
- [ ] src/pages/AppointmentsPage.tsx
- [ ] src/pages/ProfilePage.tsx
- [ ] src/pages/AdminPage.tsx

## Common Tailwind Patterns to Look For

1. **Background Colors**: `bg-white`, `bg-gray-50`, `bg-blue-600`
2. **Text Colors**: `text-gray-700`, `text-blue-600`, `text-red-500`
3. **Padding**: `p-4`, `px-6`, `py-4`
4. **Margin**: `mt-4`, `mb-6`, `mx-auto`
5. **Border**: `border`, `border-gray-200`, `rounded-lg`
6. **Shadow**: `shadow-md`, `shadow-lg`
7. **Width/Height**: `w-full`, `h-16`, `max-w-7xl`
8. **Display**: `flex`, `grid`, `hidden`, `block`
9. **Position**: `absolute`, `relative`, `fixed`
10. **Responsive**: `sm:`, `md:`, `lg:` prefixes

## Replacement Strategy

For each file:
1. Open the file
2. Search for `className="`
3. Identify Tailwind classes
4. Replace with CSS classes or inline styles
5. Test the component
6. Mark as complete in the checklist above
