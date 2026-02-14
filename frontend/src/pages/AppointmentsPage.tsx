/**
 * Appointments Management Page
 */

import { useState } from 'react';
import { DashboardLayout } from '../layouts/DashboardLayout';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Modal } from '../components/ui/Modal';
import { Alert } from '../components/ui/Alert';
import { Select } from '../components/ui/Select';
import { AppointmentCard } from '../components/appointments/AppointmentCard';
import { AppointmentForm } from '../components/appointments/AppointmentForm';
import { RescheduleForm } from '../components/appointments/RescheduleForm';
import { useAppointments } from '../hooks/useAppointments';
import { usePets } from '../hooks/usePets';
import { useAuth } from '../contexts/AuthContext';
import { Appointment, AppointmentStatus } from '../types';

export function AppointmentsPage() {
  const { user } = useAuth();
  const { pets } = usePets();
  const [statusFilter, setStatusFilter] = useState<AppointmentStatus | ''>('');
  const {
    appointments,
    createAppointment,
    rescheduleAppointment,
    updateAppointmentStatus,
    cancelAppointment,
    fetchAppointments,
    isLoading,
    error,
  } = useAppointments({ status: statusFilter || undefined });

  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [rescheduleAppointmentData, setRescheduleAppointmentData] = useState<Appointment | null>(null);
  const [deleteConfirm, setDeleteConfirm] = useState<string | null>(null);

  const handleCreate = async (data: any) => {
    await createAppointment(data);
    setIsCreateModalOpen(false);
  };

  const handleReschedule = async (data: any) => {
    if (rescheduleAppointmentData) {
      await rescheduleAppointment(rescheduleAppointmentData.id, data);
      setRescheduleAppointmentData(null);
    }
  };

  const handleCancel = async (appointmentId: string) => {
    if (deleteConfirm === appointmentId) {
      await cancelAppointment(appointmentId);
      setDeleteConfirm(null);
    } else {
      setDeleteConfirm(appointmentId);
      setTimeout(() => setDeleteConfirm(null), 3000);
    }
  };

  const handleUpdateStatus = async (appointmentId: string, status: string) => {
    await updateAppointmentStatus(appointmentId, { status: status as AppointmentStatus });
  };

  const getPetName = (petId: string) => {
    const pet = pets.find((p) => p.id === petId);
    return pet ? pet.name : 'Unknown Pet';
  };

  const statusOptions = [
    { value: '', label: 'All Appointments' },
    { value: 'pending', label: 'Pending' },
    { value: 'confirmed', label: 'Confirmed' },
    { value: 'completed', label: 'Completed' },
    { value: 'cancelled', label: 'Cancelled' },
  ];

  return (
    <DashboardLayout>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold">Appointments</h1>
            <p className="text-gray-600" style={{ marginTop: '0.5rem' }}>Manage your pet appointments</p>
          </div>
          <Button onClick={() => setIsCreateModalOpen(true)}>
            Book Appointment
          </Button>
        </div>

        {error && (
          <Alert type="error" title="Error">
            {error}
          </Alert>
        )}

        <Card>
          <div className="flex gap-4 items-center">
            <Select
              label="Filter by Status"
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value as AppointmentStatus | '')}
              options={statusOptions}
            />
          </div>
        </Card>

        {appointments.length === 0 ? (
          <Card>
            <div className="text-center" style={{ padding: '3rem 0' }}>
              <svg width="48" height="48" fill="none" viewBox="0 0 24 24" stroke="currentColor" style={{ margin: '0 auto', color: 'var(--color-gray-400)' }}>
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              <h3 className="text-sm font-medium" style={{ marginTop: '0.5rem' }}>No appointments</h3>
              <p className="text-sm text-gray-500" style={{ marginTop: '0.25rem' }}>Get started by booking your first appointment.</p>
              <div style={{ marginTop: '1.5rem' }}>
                <Button onClick={() => setIsCreateModalOpen(true)}>
                  Book Appointment
                </Button>
              </div>
            </div>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {appointments.map((appointment) => (
              <div key={appointment.id}>
                <AppointmentCard
                  appointment={appointment}
                  petName={getPetName(appointment.pet_id)}
                  onReschedule={setRescheduleAppointmentData}
                  onCancel={handleCancel}
                  onUpdateStatus={user?.role === 'admin' ? handleUpdateStatus : undefined}
                />
                {deleteConfirm === appointment.id && (
                  <Alert type="warning" style={{ marginTop: '0.5rem' }}>
                    Click cancel again to confirm
                  </Alert>
                )}
              </div>
            ))}
          </div>
        )}

        <Modal
          isOpen={isCreateModalOpen}
          onClose={() => setIsCreateModalOpen(false)}
          title="Book New Appointment"
        >
          <AppointmentForm
            pets={pets}
            onSubmit={handleCreate}
            onCancel={() => setIsCreateModalOpen(false)}
            isLoading={isLoading}
            error={error}
          />
        </Modal>

        <Modal
          isOpen={!!rescheduleAppointmentData}
          onClose={() => setRescheduleAppointmentData(null)}
          title="Reschedule Appointment"
        >
          {rescheduleAppointmentData && (
            <RescheduleForm
              appointment={rescheduleAppointmentData}
              onSubmit={handleReschedule}
              onCancel={() => setRescheduleAppointmentData(null)}
              isLoading={isLoading}
              error={error}
            />
          )}
        </Modal>
      </div>
    </DashboardLayout>
  );
}
