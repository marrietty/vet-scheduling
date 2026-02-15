import { createFileRoute, redirect } from '@tanstack/react-router'
import { RegisterPage } from '../pages/RegisterPage'

export const Route = createFileRoute('/register')({
  beforeLoad: ({ context }) => {
    if (context.auth.isAuthenticated) {
      throw redirect({ to: '/dashboard' })
    }
  },
  component: RegisterPage,
})
