/**
 * Reschedule Appointment Form Component
 */

import { useState } from 'react';
import type { FormEvent } from 'react';
import { Input } from '../ui/Input';
import { Button } from '../ui/Button';
import { Alert } from '../ui/Alert';
import type { Appointment, AppointmentRescheduleRequest } from '../../types';
import { format } from 'date-fns';

interface RescheduleFormProps {
  appointment: Appointment;
  onSubmit: (data: AppointmentRescheduleRequest) => Promise<void>;
  onCancel: () => void;
  isLoading: boolean;
  error: string | null;
}

export function RescheduleForm({ appointment, onSubmit, onCancel, isLoading, error }: RescheduleFormProps) {
  const [formData, setFormData] = useState({
    start_time: format(new Date(appointment.start_time), "yyyy-MM-dd'T'HH:mm"),
    end_time: format(new Date(appointment.end_time), "yyyy-MM-dd'T'HH:mm"),
  });

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();

    await onSubmit({
      start_time: new Date(formData.start_time).toISOString(),
      end_time: new Date(formData.end_time).toISOString(),
    });
  };

  return (
    <form onSubmit={handleSubmit} className="form">
      {error && (
        <Alert type="error" title="Error">
          {error}
        </Alert>
      )}

      <Alert type="info">
        Rescheduling appointment for {format(new Date(appointment.start_time), 'MMM dd, yyyy')}
      </Alert>

      <Input
        label="New Start Time"
        type="datetime-local"
        value={formData.start_time}
        onChange={(e) => setFormData({ ...formData, start_time: e.target.value })}
        required
        min={new Date().toISOString().slice(0, 16)}
      />

      <Input
        label="New End Time"
        type="datetime-local"
        value={formData.end_time}
        onChange={(e) => setFormData({ ...formData, end_time: e.target.value })}
        required
        min={formData.start_time}
      />

      <div className="flex gap-2 justify-end">
        <Button type="button" variant="secondary" onClick={onCancel}>
          Cancel
        </Button>
        <Button type="submit" isLoading={isLoading}>
          Reschedule
        </Button>
      </div>
    </form>
  );
}
