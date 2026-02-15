import { createFileRoute } from '@tanstack/react-router'
import { PetsPage } from '../../pages/PetsPage'
import { apiClient } from '../../lib/api-client'
import type { Pet } from '../../types'
import { Spinner } from '../../components/ui/Spinner'

export const Route = createFileRoute('/_authenticated/pets')({
  loader: () => apiClient.get<Pet[]>('/api/v1/pets'),
  component: RouteComponent,
  pendingComponent: Spinner,
  pendingMs: 0,
  staleTime: 30_000,
})

function RouteComponent() {
  const pets = Route.useLoaderData()
  return <PetsPage pets={pets} />
}
