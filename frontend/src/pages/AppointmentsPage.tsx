/**
 * Appointments Management Page
 */

import { useState } from 'react';
import { useRouter } from '@tanstack/react-router';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Modal } from '../components/ui/Modal';
import { Alert } from '../components/ui/Alert';
import { Select } from '../components/ui/Select';
import { AppointmentCard } from '../components/appointments/AppointmentCard';
import { AppointmentForm } from '../components/appointments/AppointmentForm';
import { RescheduleForm } from '../components/appointments/RescheduleForm';
import { useAppointments } from '../hooks/useAppointments';
import { useAuth } from '../contexts/AuthContext';
import type { Appointment, AppointmentStatus, Pet } from '../types';

interface AppointmentsPageProps {
  appointments: Appointment[];
  pets: Pet[];
  search: {
    date?: string;
    status?: AppointmentStatus | 'all';
  };
}

export function AppointmentsPage({ appointments, pets, search }: AppointmentsPageProps) {
  const router = useRouter();
  const { user } = useAuth();

  // We use useAppointments only for mutations, disabling auto-fetch
  const {
    createAppointment,
    rescheduleAppointment,
    updateAppointmentStatus,
    cancelAppointment,
    fetchAvailableSlots,
    isLoading,
    error,
  } = useAppointments(undefined, { enabled: false });

  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [rescheduleAppointmentData, setRescheduleAppointmentData] = useState<Appointment | null>(null);
  const [deleteConfirm, setDeleteConfirm] = useState<string | null>(null);

  const handleSuccess = () => {
    router.invalidate();
  };

  const handleCreate = async (data: any) => {
    try {
      await createAppointment(data);
      setIsCreateModalOpen(false);
      handleSuccess();
    } catch {
      // Error is handled by hook
    }
  };

  const handleReschedule = async (data: any) => {
    if (rescheduleAppointmentData) {
      try {
        await rescheduleAppointment(rescheduleAppointmentData.id, data);
        setRescheduleAppointmentData(null);
        handleSuccess();
      } catch {
        // Error handled by hook
      }
    }
  };

  const handleCancel = async (appointmentId: string) => {
    if (deleteConfirm === appointmentId) {
      try {
        await cancelAppointment(appointmentId);
        setDeleteConfirm(null);
        handleSuccess();
      } catch {
        // Error handled by hook
      }
    } else {
      setDeleteConfirm(appointmentId);
      setTimeout(() => setDeleteConfirm(null), 3000);
    }
  };

  const handleUpdateStatus = async (appointmentId: string, status: string) => {
    await updateAppointmentStatus(appointmentId, { status: status as AppointmentStatus });
    handleSuccess();
  };

  const handleFilterChange = (status: string) => {
    router.navigate({
      to: '/appointments',
      search: {
        ...search,
        status: (status as AppointmentStatus) || undefined,
      },
    });
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

  // Map 'all' from search to '' for select value
  const currentStatusFilter = search.status === 'all' ? '' : search.status || '';

  return (
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
            value={currentStatusFilter}
            onChange={(e) => handleFilterChange(e.target.value)}
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
                <div style={{ marginTop: '0.5rem' }}>
                  <Alert type="warning">
                    Click cancel again to confirm
                  </Alert>
                </div>
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
          error={error}
          fetchAvailableSlots={fetchAvailableSlots}
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
  );
}
