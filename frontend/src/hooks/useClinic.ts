/**
 * Clinic Status Hook
 * Handles clinic status API calls
 * Reference: backend/README.md - Clinic Status endpoints
 */

import { useState, useCallback, useEffect } from 'react';
import { apiClient } from '../lib/api-client';
import { ClinicStatus, ClinicStatusUpdateRequest } from '../types';

export function useClinicStatus() {
  const [status, setStatus] = useState<ClinicStatus | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchStatus = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      // GET /api/v1/clinic/status (Public endpoint)
      const data = await apiClient.get<ClinicStatus>('/api/v1/clinic/status');
      setStatus(data);
      return data;
    } catch (err: any) {
      setError(err.message || 'Failed to fetch clinic status');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const updateStatus = useCallback(async (statusUpdate: ClinicStatusUpdateRequest) => {
    setIsLoading(true);
    setError(null);

    try {
      // PATCH /api/v1/clinic/status (Admin only)
      const data = await apiClient.patch<ClinicStatus>('/api/v1/clinic/status', statusUpdate);
      setStatus(data);
      return data;
    } catch (err: any) {
      setError(err.message || 'Failed to update clinic status');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Auto-fetch status on mount
  useEffect(() => {
    fetchStatus();
  }, [fetchStatus]);

  return {
    status,
    fetchStatus,
    updateStatus,
    isLoading,
    error,
  };
}
