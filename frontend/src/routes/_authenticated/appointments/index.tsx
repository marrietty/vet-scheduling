import { createFileRoute } from '@tanstack/react-router'
import { AppointmentsPage } from '../../../pages/AppointmentsPage'
import { apiClient } from '../../../lib/api-client'
import { Spinner } from '../../../components/ui/Spinner'
import type { Appointment, AppointmentStatus, Pet } from '../../../types'

type AppointmentSearchParams = {
  date?: string
  status?: AppointmentStatus | 'all'
}

export const Route = createFileRoute('/_authenticated/appointments/')({
  validateSearch: (search: Record<string, unknown>): AppointmentSearchParams => {
    return {
      date: typeof search.date === 'string' ? search.date : undefined,
      status: typeof search.status === 'string' && ['pending', 'confirmed', 'completed', 'cancelled', 'all'].includes(search.status)
        ? (search.status as AppointmentStatus | 'all')
        : 'all',
    }
  },
  loaderDeps: ({ search: { date, status } }) => ({ date, status }),
  loader: async ({ deps: { date, status } }) => {
    const params: Record<string, string> = {}
    if (date) params.date = date
    if (status && status !== 'all') params.status = status

    const [appointments, pets] = await Promise.all([
      apiClient.get<Appointment[]>('/api/v1/appointments', params),
      apiClient.get<Pet[]>('/api/v1/pets')
    ])
    return { appointments, pets }
  },
  component: RouteComponent,
  pendingComponent: Spinner,
  pendingMs: 0,
  staleTime: 30_000,
})

function RouteComponent() {
  const { appointments, pets } = Route.useLoaderData()
  const search = Route.useSearch()
  return <AppointmentsPage appointments={appointments} pets={pets} search={search} />
}
