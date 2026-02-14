/**
 * Pets Hook
 * Handles pet management API calls
 * Reference: backend/README.md - Pets endpoints
 */

import { useState, useCallback, useEffect } from 'react';
import { apiClient } from '../lib/api-client';
import { Pet, PetCreateRequest, PetUpdateRequest } from '../types';

export function usePets() {
  const [pets, setPets] = useState<Pet[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchPets = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      // GET /api/v1/pets
      const data = await apiClient.get<Pet[]>('/api/v1/pets');
      setPets(data);
      return data;
    } catch (err: any) {
      setError(err.message || 'Failed to fetch pets');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const getPet = useCallback(async (petId: string) => {
    setIsLoading(true);
    setError(null);

    try {
      // GET /api/v1/pets/{pet_id}
      const data = await apiClient.get<Pet>(`/api/v1/pets/${petId}`);
      return data;
    } catch (err: any) {
      setError(err.message || 'Failed to fetch pet');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const createPet = useCallback(async (petData: PetCreateRequest) => {
    setIsLoading(true);
    setError(null);

    try {
      // POST /api/v1/pets
      const data = await apiClient.post<Pet>('/api/v1/pets', petData);
      setPets((prev) => [...prev, data]);
      return data;
    } catch (err: any) {
      setError(err.message || 'Failed to create pet');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const updatePet = useCallback(async (petId: string, updates: PetUpdateRequest) => {
    setIsLoading(true);
    setError(null);

    try {
      // PATCH /api/v1/pets/{pet_id}
      const data = await apiClient.patch<Pet>(`/api/v1/pets/${petId}`, updates);
      setPets((prev) => prev.map((pet) => (pet.id === petId ? data : pet)));
      return data;
    } catch (err: any) {
      setError(err.message || 'Failed to update pet');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const deletePet = useCallback(async (petId: string) => {
    setIsLoading(true);
    setError(null);

    try {
      // DELETE /api/v1/pets/{pet_id}
      await apiClient.delete(`/api/v1/pets/${petId}`);
      setPets((prev) => prev.filter((pet) => pet.id !== petId));
    } catch (err: any) {
      setError(err.message || 'Failed to delete pet');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Auto-fetch pets on mount
  useEffect(() => {
    fetchPets();
  }, [fetchPets]);

  return {
    pets,
    fetchPets,
    getPet,
    createPet,
    updatePet,
    deletePet,
    isLoading,
    error,
  };
}
