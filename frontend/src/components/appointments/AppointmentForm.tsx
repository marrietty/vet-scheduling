/**
 * Appointment Form Component (Create)
 * Uses date picker + available time slot selector
 */

import { useState, useEffect } from 'react';
import type { FormEvent } from 'react';
import { Select } from '../ui/Select';
import { Button } from '../ui/Button';
import { Alert } from '../ui/Alert';
import type { Pet, AppointmentCreateRequest, ServiceType } from '../../types';
import type { TimeSlot } from '../../hooks/useAppointments';

interface AppointmentFormProps {
  pets: Pet[];
  onSubmit: (data: AppointmentCreateRequest) => Promise<void>;
  onCancel: () => void;
  error: string | null;
  fetchAvailableSlots: (date: string, serviceType: string, signal?: AbortSignal) => Promise<TimeSlot[]>;
}

export function AppointmentForm({ pets, onSubmit, onCancel, error, fetchAvailableSlots }: AppointmentFormProps) {
  const [petId, setPetId] = useState(pets[0]?.id || '');
  const [serviceType, setServiceType] = useState<ServiceType>('routine');
  const [selectedDate, setSelectedDate] = useState('');
  const [selectedSlot, setSelectedSlot] = useState<TimeSlot | null>(null);
  const [notes, setNotes] = useState('');
  const [availableSlots, setAvailableSlots] = useState<TimeSlot[]>([]);
  const [slotsLoading, setSlotsLoading] = useState(false);
  const [slotsError, setSlotsError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  // Fetch available slots when date or service type changes
  useEffect(() => {
    if (!selectedDate) {
      setAvailableSlots([]);
      setSelectedSlot(null);
      return;
    }

    // Add timeout handling
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 10000); // 10s timeout

    const loadSlots = async () => {
      setSlotsLoading(true);
      setSlotsError(null);
      setSelectedSlot(null);

      try {
        const slots = await fetchAvailableSlots(selectedDate, serviceType, controller.signal);
        clearTimeout(timeoutId);
        setAvailableSlots(slots);
        if (slots.length === 0) {
          setSlotsError('No available slots for this date and service type.');
        }
      } catch (err: any) {
        clearTimeout(timeoutId);
        if (err.name === 'AbortError') {
          setSlotsError('Request timed out. Please try again.');
        } else {
          setSlotsError(err.message || 'Failed to load available slots');
        }
        setAvailableSlots([]);
      } finally {
        setSlotsLoading(false);
      }
    };

    loadSlots();

    // Cleanup on unmount
    return () => {
      clearTimeout(timeoutId);
      controller.abort();
    };
  }, [selectedDate, serviceType, fetchAvailableSlots]);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!selectedSlot) return;

    setIsSubmitting(true);
    setSubmitError(null);

    try {
      await onSubmit({
        pet_id: petId,
        start_time: selectedSlot.start_time,
        service_type: serviceType,
        notes: notes || undefined,
      });
    } catch (err: any) {
      setSubmitError(err.message || 'Failed to book appointment');
    } finally {
      setIsSubmitting(false);
    }
  };

  // Get today's date in YYYY-MM-DD format for the min attribute
  const today = new Date().toISOString().split('T')[0];

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

  const formatSlotTime = (isoString: string) => {
    const date = new Date(isoString);
    return date.toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true,
      timeZone: 'UTC',
    });
  };

  if (pets.length === 0) {
    return (
      <Alert type="warning" title="No Pets Found">
        You need to add a pet before booking an appointment.
      </Alert>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="form">
      {(error || submitError) && (
        <Alert type="error" title="Booking Error">
          {submitError || error}
        </Alert>
      )}

      <Select
        label="Select Pet"
        value={petId}
        onChange={(e) => setPetId(e.target.value)}
        options={petOptions}
        required
      />

      <Select
        label="Service Type"
        value={serviceType}
        onChange={(e) => {
          setServiceType(e.target.value as ServiceType);
          setSelectedSlot(null);
        }}
        options={serviceOptions}
        required
      />

      <div className="input-group">
        <label className="input-label">Appointment Date</label>
        <input
          type="date"
          className="input"
          value={selectedDate}
          onChange={(e) => setSelectedDate(e.target.value)}
          min={today}
          required
        />
        <p style={{ fontSize: '0.75rem', color: 'var(--color-gray-500)', marginTop: '0.25rem' }}>
          Clinic hours: 8:00 AM – 8:00 PM
        </p>
      </div>

      {selectedDate && (
        <div className="input-group">
          <label className="input-label">Available Time Slots</label>

          {slotsLoading && (
            <div style={{ padding: '1rem', textAlign: 'center', color: 'var(--color-gray-500)' }}>
              Loading available slots...
            </div>
          )}

          {slotsError && !slotsLoading && (
            <Alert type="warning" title="No Slots">
              {slotsError}
            </Alert>
          )}

          {!slotsLoading && !slotsError && availableSlots.length > 0 && (
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fill, minmax(140px, 1fr))',
              gap: '0.5rem',
              maxHeight: '240px',
              overflowY: 'auto',
              padding: '0.25rem',
            }}>
              {availableSlots.map((slot, index) => {
                const isSelected = selectedSlot?.start_time === slot.start_time;
                return (
                  <button
                    key={index}
                    type="button"
                    onClick={() => setSelectedSlot(slot)}
                    style={{
                      padding: '0.625rem 0.75rem',
                      borderRadius: '0.5rem',
                      border: isSelected ? '2px solid var(--color-primary)' : '1px solid var(--color-gray-300)',
                      background: isSelected ? 'var(--color-primary)' : 'var(--color-surface)',
                      color: isSelected ? '#fff' : 'var(--color-text)',
                      cursor: 'pointer',
                      fontSize: '0.85rem',
                      fontWeight: isSelected ? '600' : '400',
                      textAlign: 'center',
                      transition: 'all 0.15s ease',
                    }}
                  >
                    {formatSlotTime(slot.start_time)}
                  </button>
                );
              })}
            </div>
          )}

          {selectedSlot && (
            <p style={{ fontSize: '0.8rem', color: 'var(--color-primary)', marginTop: '0.5rem', fontWeight: '500' }}>
              ✓ Selected: {formatSlotTime(selectedSlot.start_time)} – {formatSlotTime(selectedSlot.end_time)}
            </p>
          )}
        </div>
      )}

      <div className="input-group">
        <label className="input-label">Notes (Optional)</label>
        <textarea
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
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
        <Button type="submit" isLoading={isSubmitting} disabled={!selectedSlot || isSubmitting}>
          Book Appointment
        </Button>
      </div>
    </form>
  );
}
