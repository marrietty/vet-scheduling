/**
 * Pet Card Component
 */

import type { Pet } from '../../types';
import { Card } from '../ui/Card';
import { Button } from '../ui/Button';
import { format } from 'date-fns';

interface PetCardProps {
  pet: Pet;
  onEdit: (pet: Pet) => void;
  onDelete: (petId: string) => void;
}

export function PetCard({ pet, onEdit, onDelete }: PetCardProps) {
  const getVaccinationStatus = () => {
    if (!pet.last_vaccination) return { status: 'Unknown' };

    const lastVaccination = new Date(pet.last_vaccination);
    const daysSince = Math.floor((Date.now() - lastVaccination.getTime()) / (1000 * 60 * 60 * 24));

    if (daysSince <= 365) {
      return { status: 'Valid' };
    } else {
      return { status: 'Expired' };
    }
  };

  const vaccination = getVaccinationStatus();

  return (
    <Card>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        <div className="flex justify-between items-center">
          <div>
            <h3 className="text-xl font-bold">{pet.name}</h3>
            <p className="text-sm text-gray-600" style={{ textTransform: 'capitalize' }}>{pet.species}</p>
          </div>
          <div className="flex gap-2">
            <Button size="sm" variant="secondary" onClick={() => onEdit(pet)}>
              Edit
            </Button>
            <Button size="sm" variant="danger" onClick={() => onDelete(pet.id)}>
              Delete
            </Button>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-2 text-sm">
          {pet.breed && (
            <div>
              <span className="font-medium text-gray-700">Breed:</span>
              <span className="text-gray-600" style={{ marginLeft: '0.5rem' }}>{pet.breed}</span>
            </div>
          )}
          {pet.date_of_birth && (
            <div>
              <span className="font-medium text-gray-700">Birth Date:</span>
              <span className="text-gray-600" style={{ marginLeft: '0.5rem' }}>
                {format(new Date(pet.date_of_birth), 'MMM dd, yyyy')}
              </span>
            </div>
          )}
          <div>
            <span className="font-medium text-gray-700">Vaccination:</span>
            <span className="font-medium" style={{
              marginLeft: '0.5rem',
              color: vaccination.status === 'Valid' ? 'var(--color-success)' :
                vaccination.status === 'Expired' ? 'var(--color-danger)' :
                  'var(--color-gray-600)'
            }}>
              {vaccination.status}
            </span>
          </div>
        </div>

        {pet.notes && (
          <div style={{ paddingTop: '0.5rem', borderTop: '1px solid var(--color-gray-200)' }}>
            <p className="text-sm text-gray-600">{pet.notes}</p>
          </div>
        )}
      </div>
    </Card>
  );
}
