/**
 * Pets Management Page
 */

import { useState } from 'react';
import { DashboardLayout } from '../layouts/DashboardLayout';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Modal } from '../components/ui/Modal';
import { Alert } from '../components/ui/Alert';
import { PetCard } from '../components/pets/PetCard';
import { PetForm } from '../components/pets/PetForm';
import { usePets } from '../hooks/usePets';
import { Pet } from '../types';

export function PetsPage() {
  const { pets, createPet, updatePet, deletePet, isLoading, error } = usePets();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingPet, setEditingPet] = useState<Pet | null>(null);
  const [deleteConfirm, setDeleteConfirm] = useState<string | null>(null);

  const handleCreate = async (data: any) => {
    await createPet(data);
    setIsModalOpen(false);
  };

  const handleUpdate = async (data: any) => {
    if (editingPet) {
      await updatePet(editingPet.id, data);
      setEditingPet(null);
      setIsModalOpen(false);
    }
  };

  const handleDelete = async (petId: string) => {
    if (deleteConfirm === petId) {
      await deletePet(petId);
      setDeleteConfirm(null);
    } else {
      setDeleteConfirm(petId);
      setTimeout(() => setDeleteConfirm(null), 3000);
    }
  };

  const openCreateModal = () => {
    setEditingPet(null);
    setIsModalOpen(true);
  };

  const openEditModal = (pet: Pet) => {
    setEditingPet(pet);
    setIsModalOpen(true);
  };

  const closeModal = () => {
    setIsModalOpen(false);
    setEditingPet(null);
  };

  return (
    <DashboardLayout>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold">My Pets</h1>
            <p className="text-gray-600" style={{ marginTop: '0.5rem' }}>Manage your pet information</p>
          </div>
          <Button onClick={openCreateModal}>
            Add New Pet
          </Button>
        </div>

        {error && (
          <Alert type="error" title="Error">
            {error}
          </Alert>
        )}

        {pets.length === 0 ? (
          <Card>
            <div className="text-center" style={{ padding: '3rem 0' }}>
              <svg width="48" height="48" fill="none" viewBox="0 0 24 24" stroke="currentColor" style={{ margin: '0 auto', color: 'var(--color-gray-400)' }}>
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 10h4.764a2 2 0 011.789 2.894l-3.5 7A2 2 0 0115.263 21h-4.017c-.163 0-.326-.02-.485-.06L7 20m7-10V5a2 2 0 00-2-2h-.095c-.5 0-.905.405-.905.905 0 .714-.211 1.412-.608 2.006L7 11v9m7-10h-2M7 20H5a2 2 0 01-2-2v-6a2 2 0 012-2h2.5" />
              </svg>
              <h3 className="text-sm font-medium" style={{ marginTop: '0.5rem' }}>No pets</h3>
              <p className="text-sm text-gray-500" style={{ marginTop: '0.25rem' }}>Get started by adding your first pet.</p>
              <div style={{ marginTop: '1.5rem' }}>
                <Button onClick={openCreateModal}>
                  Add Pet
                </Button>
              </div>
            </div>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {pets.map((pet) => (
              <div key={pet.id}>
                <PetCard
                  pet={pet}
                  onEdit={openEditModal}
                  onDelete={handleDelete}
                />
                {deleteConfirm === pet.id && (
                  <Alert type="warning" style={{ marginTop: '0.5rem' }}>
                    Click delete again to confirm
                  </Alert>
                )}
              </div>
            ))}
          </div>
        )}

        <Modal
          isOpen={isModalOpen}
          onClose={closeModal}
          title={editingPet ? 'Edit Pet' : 'Add New Pet'}
        >
          <PetForm
            pet={editingPet || undefined}
            onSubmit={editingPet ? handleUpdate : handleCreate}
            onCancel={closeModal}
            isLoading={isLoading}
            error={error}
          />
        </Modal>
      </div>
    </DashboardLayout>
  );
}
