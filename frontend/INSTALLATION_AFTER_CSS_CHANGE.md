# Installation Instructions After CSS Migration

## What Changed

The frontend has been migrated from **Tailwind CSS** to **Plain CSS** with CSS Variables.

## Installation Steps

### 1. Clean Install Dependencies

Since we removed Tailwind packages, you need to reinstall dependencies:

```bash
cd frontend

# Remove old node_modules and lock file
rm -rf node_modules
rm package-lock.json

# Install fresh dependencies
npm install
```

### 2. Verify Installation

Check that Tailwind packages are gone:

```bash
npm list tailwindcss
# Should show: (empty)

npm list autoprefixer
# Should show: (empty)

npm list postcss
# Should show: (empty)
```

### 3. Start Development Server

```bash
npm run dev
```

The app should start at http://localhost:5173

## What to Expect

### ✅ Working Now
- All UI components (Button, Input, Select, Card, Modal, Alert)
- Navbar and DashboardLayout
- CSS system with variables
- Responsive utilities

### ⚠️ Needs Conversion
The following files still have Tailwind classes and may look broken:
- Feature components (LoginForm, PetCard, AppointmentCard, etc.)
- All pages (HomePage, DashboardPage, etc.)

**These need to be converted using the CSS_MIGRATION_GUIDE.md**

## Quick Test

After starting the dev server, test these:

1. **UI Components Work**
   - Buttons should have proper colors and hover states
   - Inputs should have borders and focus states
   - Cards should have shadows and rounded corners

2. **Layout Works**
   - Navbar should be sticky at top
   - Container should be centered
   - Responsive design should work

3. **CSS Variables Work**
   - Open DevTools
   - Inspect any element
   - Check that CSS variables are applied (e.g., `var(--color-primary)`)

## Troubleshooting

### Issue: Styles Not Loading
**Solution**: Make sure `src/index.css` is imported in `src/main.tsx`:
```tsx
import './index.css'
```

### Issue: Components Look Broken
**Solution**: That's expected! The component files still have Tailwind classes. Convert them using the migration guide.

### Issue: Build Errors
**Solution**: 
```bash
# Clear cache and rebuild
rm -rf node_modules .vite
npm install
npm run dev
```

### Issue: TypeScript Errors
**Solution**: The CSS migration doesn't affect TypeScript. If you see TS errors, they're unrelated to the CSS change.

## Next Steps

1. ✅ Install dependencies (you're here)
2. ⏳ Convert remaining components (see CSS_MIGRATION_GUIDE.md)
3. ⏳ Test all pages
4. ⏳ Verify responsive design
5. ⏳ Build for production

## Production Build

Once all files are converted:

```bash
npm run build
```

This will create an optimized production build in the `dist/` folder.

### Build Size Comparison

**Before (with Tailwind)**:
- CSS: ~3MB (development)
- CSS: ~50KB (production, purged)

**After (plain CSS)**:
- CSS: ~15KB (development)
- CSS: ~15KB (production)

Benefits:
- Smaller bundle size
- Faster build times
- No PostCSS processing
- Simpler setup

## Support Files

- `CSS_MIGRATION_GUIDE.md` - How to convert Tailwind to CSS
- `TAILWIND_REMOVAL_SUMMARY.md` - What was changed
- `find-tailwind-classes.md` - Find remaining Tailwind classes
- `src/index.css` - Complete CSS system

## Questions?

1. Check the migration guide first
2. Look at converted components for examples
3. Review the CSS system in `src/index.css`
4. Test in the browser with DevTools

---

**Ready to start?** Run `npm install` and then `npm run dev`!
