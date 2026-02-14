/**
 * Admin Dashboard Page
 */

import { useState } from 'react';
import { DashboardLayout } from '../layouts/DashboardLayout';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Select } from '../components/ui/Select';
import { Alert } from '../components/ui/Alert';
import { useAppointments } from '../hooks/useAppointments';
import { useClinicStatus } from '../hooks/useClinic';
import { usePets } from '../hooks/usePets';
import { ClinicStatusType } from '../types';
import { format } from 'date-fns';

export function AdminPage() {
  const { appointments, updateAppointmentStatus } = useAppointments();
  const { status, updateStatus, isLoading: statusLoading } = useClinicStatus();
  const { pets } = usePets();
  const [newStatus, setNewStatus] = useState<ClinicStatusType>(status?.status || 'open');
  const [success, setSuccess] = useState(false);

  const handleStatusUpdate = async () => {
    try {
      await updateStatus({ status: newStatus });
      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
    } catch (err) {
      // Error handled by hook
    }
  };

  const pendingAppointments = appointments.filter((apt) => apt.status === 'pending');
  const confirmedAppointments = appointments.filter((apt) => apt.status === 'confirmed');

  const statusOptions = [
    { value: 'open', label: 'Open' },
    { value: 'closing_soon', label: 'Closing Soon' },
    { value: 'close', label: 'Closed' },
  ];

  return (
    <DashboardLayout>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
        <div>
          <h1 className="text-3xl font-bold">Admin Dashboard</h1>
          <p className="text-gray-600" style={{ marginTop: '0.5rem' }}>Manage clinic operations</p>
        </div>

        {/* Clinic Status Management */}
        <Card title="Clinic Status">
          {success && (
            <Alert type="success" style={{ marginBottom: '1rem' }}>
              Clinic status updated successfully!
            </Alert>
          )}
          <div className="flex gap-4 items-end">
            <div style={{ flex: 1 }}>
              <Select
                label="Current Status"
                value={newStatus}
                onChange={(e) => setNewStatus(e.target.value as ClinicStatusType)}
                options={statusOptions}
              />
            </div>
            <Button onClick={handleStatusUpdate} isLoading={statusLoading}>
              Update Status
            </Button>
          </div>
        </Card>

        {/* Statistics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card>
            <div className="text-center">
              <p className="text-sm text-gray-600">Total Pets</p>
              <p className="text-3xl font-bold">{pets.length}</p>
            </div>
          </Card>
          <Card>
            <div className="text-center">
              <p className="text-sm text-gray-600">Total Appointments</p>
              <p className="text-3xl font-bold">{appointments.length}</p>
            </div>
          </Card>
          <Card>
            <div className="text-center">
              <p className="text-sm text-gray-600">Pending</p>
              <p className="text-3xl font-bold" style={{ color: 'var(--color-warning)' }}>{pendingAppointments.length}</p>
            </div>
          </Card>
          <Card>
            <div className="text-center">
              <p className="text-sm text-gray-600">Confirmed</p>
              <p className="text-3xl font-bold" style={{ color: 'var(--color-primary)' }}>{confirmedAppointments.length}</p>
            </div>
          </Card>
        </div>

        {/* Pending Appointments */}
        {pendingAppointments.length > 0 && (
          <Card title="Pending Appointments">
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              {pendingAppointments.map((apt) => {
                const pet = pets.find((p) => p.id === apt.pet_id);
                return (
                  <div
                    key={apt.id}
                    className="flex justify-between items-center"
                    style={{ 
                      padding: '1rem', 
                      backgroundColor: 'var(--color-gray-50)', 
                      borderRadius: 'var(--radius-lg)' 
                    }}
                  >
                    <div>
                      <p className="font-medium">
                        {pet?.name || 'Unknown Pet'} - {pet?.species}
                      </p>
                      <p className="text-sm text-gray-600">
                        {format(new Date(apt.start_time), 'MMM dd, yyyy h:mm a')}
                      </p>
                      <p className="text-sm text-gray-600" style={{ textTransform: 'capitalize' }}>{apt.service_type}</p>
                    </div>
                    <div className="flex gap-2">
                      <Button
                        size="sm"
                        variant="success"
                        onClick={() => updateAppointmentStatus(apt.id, { status: 'confirmed' })}
                      >
                        Confirm
                      </Button>
                      <Button
                        size="sm"
                        variant="danger"
                        onClick={() => updateAppointmentStatus(apt.id, { status: 'cancelled' })}
                      >
                        Reject
                      </Button>
                    </div>
                  </div>
                );
              })}
            </div>
          </Card>
        )}

        {/* Confirmed Appointments */}
        {confirmedAppointments.length > 0 && (
          <Card title="Confirmed Appointments">
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              {confirmedAppointments.slice(0, 5).map((apt) => {
                const pet = pets.find((p) => p.id === apt.pet_id);
                return (
                  <div
                    key={apt.id}
                    className="flex justify-between items-center"
                    style={{ 
                      padding: '1rem', 
                      backgroundColor: 'var(--color-gray-50)', 
                      borderRadius: 'var(--radius-lg)' 
                    }}
                  >
                    <div>
                      <p className="font-medium">
                        {pet?.name || 'Unknown Pet'} - {pet?.species}
                      </p>
                      <p className="text-sm text-gray-600">
                        {format(new Date(apt.start_time), 'MMM dd, yyyy h:mm a')}
                      </p>
                      <p className="text-sm text-gray-600" style={{ textTransform: 'capitalize' }}>{apt.service_type}</p>
                    </div>
                    <Button
                      size="sm"
                      variant="success"
                      onClick={() => updateAppointmentStatus(apt.id, { status: 'completed' })}
                    >
                      Mark Complete
                    </Button>
                  </div>
                );
              })}
            </div>
          </Card>
        )}
      </div>
    </DashboardLayout>
  );
}
