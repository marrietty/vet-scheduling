import { createFileRoute, redirect } from '@tanstack/react-router'
import { AdminPage } from '../../pages/AdminPage'

export const Route = createFileRoute('/_authenticated/admin')({
  beforeLoad: ({ context }) => {
    if (context.auth.user?.role !== 'admin') {
      throw redirect({ to: '/dashboard' })
    }
  },
  component: AdminPage,
})
