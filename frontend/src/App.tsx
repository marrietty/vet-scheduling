/**
 * Main App Component
 * Wraps the router with AuthProvider and passes auth context down.
 */

import { RouterProvider } from '@tanstack/react-router'
import { AuthProvider, useAuth } from './contexts/AuthContext'
import { router } from './router'

function InnerApp() {
  const auth = useAuth()
  return <RouterProvider router={router} context={{ auth }} />
}

function App() {
  return (
    <AuthProvider>
      <InnerApp />
    </AuthProvider>
  )
}

export default App
