/**
 * Appointment Card Component
 */

import { Appointment } from '../../types';
import { Card } from '../ui/Card';
import { Button } from '../ui/Button';
import { format } from 'date-fns';
import { useAuth } from '../../contexts/AuthContext';

interface AppointmentCardProps {
  appointment: Appointment;
  petName?: string;
  onReschedule: (appointment: Appointment) => void;
  onCancel: (appointmentId: string) => void;
  onUpdateStatus?: (appointmentId: string, status: string) => void;
}

export function AppointmentCard({
  appointment,
  petName,
  onReschedule,
  onCancel,
  onUpdateStatus,
}: AppointmentCardProps) {
  const { user } = useAuth();
  const isAdmin = user?.role === 'admin';

  const getStatusBadgeClass = (status: string) => {
    switch (status) {
      case 'pending': return 'badge-warning';
      case 'confirmed': return 'badge-primary';
      case 'cancelled': return 'badge-danger';
      case 'completed': return 'badge-success';
      default: return 'badge-gray';
    }
  };

  const serviceTypeLabels = {
    vaccination: 'Vaccination (30 min)',
    routine: 'Routine Checkup (45 min)',
    surgery: 'Surgery (2 hours)',
    emergency: 'Emergency (15 min)',
  };

  const canReschedule = appointment.status === 'pending' || appointment.status === 'confirmed';
  const canCancel = appointment.status !== 'completed' && appointment.status !== 'cancelled';

  return (
    <Card>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        <div className="flex justify-between items-center">
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-lg font-bold">
                {format(new Date(appointment.start_time), 'MMM dd, yyyy')}
              </h3>
              <span className={`badge ${getStatusBadgeClass(appointment.status)}`}>
                {appointment.status.toUpperCase()}
              </span>
            </div>
            <p className="text-sm text-gray-600">
              {format(new Date(appointment.start_time), 'h:mm a')} -{' '}
              {format(new Date(appointment.end_time), 'h:mm a')}
            </p>
          </div>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }} className="text-sm">
          {petName && (
            <div>
              <span className="font-medium text-gray-700">Pet:</span>
              <span className="text-gray-600" style={{ marginLeft: '0.5rem' }}>{petName}</span>
            </div>
          )}
          <div>
            <span className="font-medium text-gray-700">Service:</span>
            <span className="text-gray-600" style={{ marginLeft: '0.5rem' }}>{serviceTypeLabels[appointment.service_type]}</span>
          </div>
          {appointment.notes && (
            <div>
              <span className="font-medium text-gray-700">Notes:</span>
              <span className="text-gray-600" style={{ marginLeft: '0.5rem' }}>{appointment.notes}</span>
            </div>
          )}
        </div>

        <div className="flex gap-2" style={{ paddingTop: '0.5rem', borderTop: '1px solid var(--color-gray-200)' }}>
          {canReschedule && (
            <Button size="sm" variant="secondary" onClick={() => onReschedule(appointment)}>
              Reschedule
            </Button>
          )}
          {canCancel && (
            <Button size="sm" variant="danger" onClick={() => onCancel(appointment.id)}>
              Cancel
            </Button>
          )}
          {isAdmin && onUpdateStatus && appointment.status === 'pending' && (
            <Button size="sm" variant="success" onClick={() => onUpdateStatus(appointment.id, 'confirmed')}>
              Confirm
            </Button>
          )}
          {isAdmin && onUpdateStatus && appointment.status === 'confirmed' && (
            <Button size="sm" variant="success" onClick={() => onUpdateStatus(appointment.id, 'completed')}>
              Complete
            </Button>
          )}
        </div>
      </div>
    </Card>
  );
}
