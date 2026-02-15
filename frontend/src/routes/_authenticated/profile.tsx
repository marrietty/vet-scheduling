import { createFileRoute } from '@tanstack/react-router'
import { ProfilePage } from '../../pages/ProfilePage'
import { apiClient } from '../../lib/api-client'
import { Spinner } from '../../components/ui/Spinner'
import type { UserProfileResponse } from '../../types'

export const Route = createFileRoute('/_authenticated/profile')({
  loader: () => apiClient.get<UserProfileResponse>('/api/v1/users/profile'),
  component: RouteComponent,
  pendingComponent: Spinner,
  pendingMs: 0,
  staleTime: 30_000,
})

function RouteComponent() {
  const profile = Route.useLoaderData()
  return <ProfilePage profile={profile} />
}
