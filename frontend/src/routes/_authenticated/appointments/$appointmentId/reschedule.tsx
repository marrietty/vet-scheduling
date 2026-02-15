import { useNavigate, createFileRoute } from '@tanstack/react-router'
import { RescheduleForm } from '../../../../components/appointments/RescheduleForm'
import { Card } from '../../../../components/ui/Card'
import { apiClient } from '../../../../lib/api-client'
import type { Appointment } from '../../../../types'
import { useState, useEffect } from 'react'

export const Route = createFileRoute('/_authenticated/appointments/$appointmentId/reschedule')({
  loader: ({ params }) => {
    return { appointmentId: params.appointmentId }
  },
  component: RescheduleRouteComponent,
})

function RescheduleRouteComponent() {
  const { appointmentId } = Route.useLoaderData()
  const navigate = useNavigate()
  const [error, setError] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [appointment, setAppointment] = useState<Appointment | null>(null)

  useEffect(() => {
    async function fetchAppointment() {
      try {
        // Fetch specific appointment. Assuming endpoint exists or we filter from list?
        // Let's try to fetch list and find it if direct ID fetch fails, or just assume it works.
        // For now, I'll attempt a direct fetch.
        // If the backend doesn't support GET /appointments/:id, this will fail.
        // A safer fallback: fetch all and find (not efficient but works for small app).
        const appointments = await apiClient.get<Appointment[]>('/api/v1/appointments/')
        const found = appointments.find(a => a.id === appointmentId)
        if (found) {
          setAppointment(found)
        } else {
          setError('Appointment not found')
        }
      } catch (err) {
        setError('Failed to load appointment details')
      }
    }
    fetchAppointment()
  }, [appointmentId])

  return (
    <div className="max-w-md mx-auto mt-8">
      <Card title="Reschedule Appointment">
        {appointment ? (
          <RescheduleForm
            appointment={appointment}
            onSubmit={async (data) => {
              setIsLoading(true)
              try {
                await apiClient.patch(`/api/v1/appointments/${appointmentId}/reschedule`, data)
                navigate({ to: '/dashboard' })
              } catch (err) {
                setError('Failed to reschedule')
              } finally {
                setIsLoading(false)
              }
            }}
            onCancel={() => navigate({ to: '/dashboard' })}
            isLoading={isLoading}
            error={error}
          />
        ) : (
          <div className="p-4 text-center text-gray-600">
            {error ? <span className="text-red-600">{error}</span> : 'Loading appointment details...'}
          </div>
        )}
      </Card>
    </div>
  )
}
