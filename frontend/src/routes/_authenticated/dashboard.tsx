import { createFileRoute } from '@tanstack/react-router'
import { DashboardPage } from '../../pages/DashboardPage'
import { apiClient } from '../../lib/api-client'
import type { Appointment, ClinicStatus, Pet } from '../../types'

async function dashboardLoader() {
  const today = new Date().toISOString().split('T')[0]
  try {
    const [appointments, pets, status] = await Promise.all([
      apiClient.get<Appointment[]>('/api/v1/appointments/', { date: today }),
      apiClient.get<Pet[]>('/api/v1/pets'),
      apiClient.get<ClinicStatus>('/api/v1/clinic/status')
    ])
    return { appointments, pets, status }
  } catch {
    return {
      appointments: [] as Appointment[],
      pets: [] as Pet[],
      status: null
    }
  }
}

import { Spinner } from '../../components/ui/Spinner'

function DashboardRouteComponent() {
  const { appointments, pets, status } = Route.useLoaderData()
  return <DashboardPage appointments={appointments} pets={pets} status={status} />
}

export const Route = createFileRoute('/_authenticated/dashboard')({
  loader: dashboardLoader,
  component: DashboardRouteComponent,
  pendingComponent: Spinner,
  pendingMs: 0,
  staleTime: 30_000, // Cache data for 30 seconds
})
