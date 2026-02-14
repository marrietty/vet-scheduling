/**
 * Appointment Form Component (Create)
 */

import { useState, FormEvent } from 'react';
import { Input } from '../ui/Input';
import { Select } from '../ui/Select';
import { Button } from '../ui/Button';
import { Alert } from '../ui/Alert';
import { Pet, AppointmentCreateRequest, ServiceType } from '../../types';

interface AppointmentFormProps {
  pets: Pet[];
  onSubmit: (data: AppointmentCreateRequest) => Promise<void>;
  onCancel: () => void;
  isLoading: boolean;
  error: string | null;
}

export function AppointmentForm({ pets, onSubmit, onCancel, isLoading, error }: AppointmentFormProps) {
  const [formData, setFormData] = useState({
    pet_id: pets[0]?.id || '',
    start_time: '',
    service_type: 'routine' as ServiceType,
    notes: '',
  });

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    
    // Convert local datetime to ISO format
    const startTime = new Date(formData.start_time).toISOString();
    
    await onSubmit({
      pet_id: formData.pet_id,
      start_time: startTime,
      service_type: formData.service_type,
      notes: formData.notes || undefined,
    });
  };

  const serviceOptions = [
    { value: 'vaccination', label: 'Vaccination (30 min)' },
    { value: 'routine', label: 'Routine Checkup (45 min)' },
    { value: 'surgery', label: 'Surgery (2 hours)' },
    { value: 'emergency', label: 'Emergency (15 min)' },
  ];

  const petOptions = pets.map((pet) => ({
    value: pet.id,
    label: `${pet.name} (${pet.species})`,
  }));

  if (pets.length === 0) {
    return (
      <Alert type="warning" title="No Pets Found">
        You need to add a pet before booking an appointment.
      </Alert>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="form">
      {error && (
        <Alert type="error" title="Error">
          {error}
        </Alert>
      )}

      <Select
        label="Select Pet"
        value={formData.pet_id}
        onChange={(e) => setFormData({ ...formData, pet_id: e.target.value })}
        options={petOptions}
        required
      />

      <Select
        label="Service Type"
        value={formData.service_type}
        onChange={(e) => setFormData({ ...formData, service_type: e.target.value as ServiceType })}
        options={serviceOptions}
        required
      />

      <Input
        label="Appointment Date & Time"
        type="datetime-local"
        value={formData.start_time}
        onChange={(e) => setFormData({ ...formData, start_time: e.target.value })}
        required
        min={new Date().toISOString().slice(0, 16)}
      />

      <div className="input-group">
        <label className="input-label">Notes (Optional)</label>
        <textarea
          value={formData.notes}
          onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
          rows={3}
          className="input"
          placeholder="Any special requirements or notes..."
          style={{ resize: 'vertical' }}
        />
      </div>

      <div className="flex gap-2 justify-end">
        <Button type="button" variant="secondary" onClick={onCancel}>
          Cancel
        </Button>
        <Button type="submit" isLoading={isLoading}>
          Book Appointment
        </Button>
      </div>
    </form>
  );
}
