/**
 * User Profile Hook
 * Handles user profile API calls
 * Reference: backend/README.md - Users endpoints
 */

import { useState, useCallback } from 'react';
import { apiClient } from '../lib/api-client';
import { useAuth } from '../contexts/AuthContext';
import { UserProfileResponse, UserProfileUpdate } from '../types';

export function useUserProfile() {
  const { updateUser } = useAuth();
  const [profile, setProfile] = useState<UserProfileResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchProfile = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      // GET /api/v1/users/profile
      const data = await apiClient.get<UserProfileResponse>('/api/v1/users/profile');
      setProfile(data);
      
      // Update auth context with latest profile
      updateUser({
        id: data.id,
        email: data.email,
        full_name: data.full_name,
        phone: data.phone,
        city: data.city,
        role: data.role,
        is_active: data.is_active,
        preferences: data.preferences,
        created_at: data.created_at,
      });
      
      return data;
    } catch (err: any) {
      setError(err.message || 'Failed to fetch profile');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [updateUser]);

  const updateProfile = useCallback(async (updates: UserProfileUpdate) => {
    setIsLoading(true);
    setError(null);

    try {
      // PATCH /api/v1/users/profile
      const data = await apiClient.patch<UserProfileResponse>('/api/v1/users/profile', updates);
      setProfile(data);
      
      // Update auth context with latest profile
      updateUser({
        id: data.id,
        email: data.email,
        full_name: data.full_name,
        phone: data.phone,
        city: data.city,
        role: data.role,
        is_active: data.is_active,
        preferences: data.preferences,
        created_at: data.created_at,
      });
      
      return data;
    } catch (err: any) {
      setError(err.message || 'Failed to update profile');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [updateUser]);

  return {
    profile,
    fetchProfile,
    updateProfile,
    isLoading,
    error,
  };
}
