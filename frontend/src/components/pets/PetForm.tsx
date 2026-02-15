/**
 * Pet Form Component (Create/Edit)
 */

import { useState } from 'react';
import type { FormEvent } from 'react';
import { Button } from '../ui/Button';
import { Input } from '../ui/Input';
import { Alert } from '../ui/Alert';
import type { Pet, PetCreateRequest, PetUpdateRequest } from '../../types';

interface PetFormProps {
  pet?: Pet;
  onSubmit: (data: PetCreateRequest | PetUpdateRequest) => Promise<void>;
  onCancel: () => void;
  isLoading: boolean;
  error: string | null;
}

export function PetForm({ pet, onSubmit, onCancel, isLoading, error }: PetFormProps) {
  const [formData, setFormData] = useState({
    name: pet?.name || '',
    species: pet?.species || '',
    breed: pet?.breed || '',
    notes: pet?.notes || '',
    date_of_birth: pet?.date_of_birth || '',
    last_vaccination: pet?.last_vaccination || '',
  });

  const [dobError, setDobError] = useState<string | null>(null);
  const [vaccinationError, setVaccinationError] = useState<string | null>(null);

  // Today's date for max attribute
  const today = new Date().toISOString().split('T')[0];

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();

    const data: any = {
      name: formData.name,
      species: formData.species,
    };

    if (formData.breed) data.breed = formData.breed;
    if (formData.notes) data.notes = formData.notes;
    if (formData.date_of_birth) data.date_of_birth = formData.date_of_birth;
    if (formData.last_vaccination) data.last_vaccination = formData.last_vaccination;

    await onSubmit(data);
  };

  return (
    <form onSubmit={handleSubmit} className="form">
      {error && (
        <Alert type="error" title="Error">
          {error}
        </Alert>
      )}

      <Input
        label="Pet Name"
        type="text"
        value={formData.name}
        onChange={(e) => setFormData({ ...formData, name: e.target.value })}
        required
        placeholder="Buddy"
      />

      <Input
        label="Species"
        type="text"
        value={formData.species}
        onChange={(e) => setFormData({ ...formData, species: e.target.value })}
        required
        placeholder="Dog, Cat, Bird, etc."
      />

      <Input
        label="Breed"
        type="text"
        value={formData.breed}
        onChange={(e) => setFormData({ ...formData, breed: e.target.value })}
        placeholder="Golden Retriever (optional)"
      />

      <Input
        label="Date of Birth"
        type="date"
        value={formData.date_of_birth}
        onChange={(e) => {
          const val = e.target.value;
          if (val && val > today) {
            setDobError('Date cannot be in the future.');
            setFormData({ ...formData, date_of_birth: '' });
          } else {
            setDobError(null);
            setFormData({ ...formData, date_of_birth: val });
          }
        }}
        max={today}
        error={dobError || undefined}
      />

      <Input
        label="Last Vaccination"
        type="date"
        value={formData.last_vaccination}
        onChange={(e) => {
          const val = e.target.value;
          if (val && val > today) {
            setVaccinationError('Date cannot be in the future.');
            setFormData({ ...formData, last_vaccination: '' });
          } else {
            setVaccinationError(null);
            setFormData({ ...formData, last_vaccination: val });
          }
        }}
        max={today}
        error={vaccinationError || undefined}
      />

      <div className="input-group">
        <label className="input-label">Notes</label>
        <textarea
          value={formData.notes}
          onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
          rows={3}
          className="input"
          placeholder="Any additional information about your pet..."
          style={{ resize: 'vertical' }}
        />
      </div>

      <div className="flex gap-2 justify-end">
        <Button type="button" variant="secondary" onClick={onCancel}>
          Cancel
        </Button>
        <Button type="submit" isLoading={isLoading}>
          {pet ? 'Update Pet' : 'Add Pet'}
        </Button>
      </div>
    </form>
  );
}
