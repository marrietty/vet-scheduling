/**
 * Appointments Hook
 * Handles appointment management API calls
 * Reference: backend/README.md - Appointments endpoints
 */

import { useState, useCallback, useEffect } from 'react';
import { apiClient } from '../lib/api-client';
import type {
  Appointment,
  AppointmentCreateRequest,
  AppointmentUpdateStatusRequest,
  AppointmentRescheduleRequest,
  AppointmentFilters,
} from '../types';

export interface TimeSlot {
  start_time: string;
  end_time: string;
}

export function useAppointments(filters?: AppointmentFilters, options = { enabled: true }) {
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchAppointments = useCallback(async (customFilters?: AppointmentFilters) => {
    setIsLoading(true);
    setError(null);

    try {
      const params: Record<string, string> = {};
      const activeFilters = customFilters || filters || {};

      if (activeFilters.status) params.status = activeFilters.status;
      if (activeFilters.from_date) params.from_date = activeFilters.from_date;
      if (activeFilters.to_date) params.to_date = activeFilters.to_date;

      // GET /api/v1/appointments
      const data = await apiClient.get<Appointment[]>('/api/v1/appointments', params);
      setAppointments(data);
      return data;
    } catch (err: any) {
      setError(err.message || 'Failed to fetch appointments');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [filters]);

  const fetchAvailableSlots = useCallback(async (date: string, serviceType: string, signal?: AbortSignal): Promise<TimeSlot[]> => {
    try {
      const data = await apiClient.get<TimeSlot[]>('/api/v1/appointments/available-slots', {
        date,
        service_type: serviceType,
      }, signal);
      return data;
    } catch (err: any) {
      throw err;
    }
  }, []);

  const createAppointment = useCallback(async (appointmentData: AppointmentCreateRequest) => {
    setIsLoading(true);
    setError(null);

    try {
      // POST /api/v1/appointments
      const data = await apiClient.post<Appointment>('/api/v1/appointments', appointmentData);
      setAppointments((prev) => [...prev, data]);
      return data;
    } catch (err: any) {
      setError(err.message || 'Failed to create appointment');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const updateAppointmentStatus = useCallback(
    async (appointmentId: string, statusUpdate: AppointmentUpdateStatusRequest) => {
      setIsLoading(true);
      setError(null);

      try {
        // PATCH /api/v1/appointments/{id}/status (Admin only)
        const data = await apiClient.patch<Appointment>(
          `/api/v1/appointments/${appointmentId}/status`,
          statusUpdate
        );
        setAppointments((prev) =>
          prev.map((apt) => (apt.id === appointmentId ? data : apt))
        );
        return data;
      } catch (err: any) {
        setError(err.message || 'Failed to update appointment status');
        throw err;
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  const rescheduleAppointment = useCallback(
    async (appointmentId: string, rescheduleData: AppointmentRescheduleRequest) => {
      setIsLoading(true);
      setError(null);

      try {
        // PATCH /api/v1/appointments/{id}/reschedule
        const data = await apiClient.patch<Appointment>(
          `/api/v1/appointments/${appointmentId}/reschedule`,
          rescheduleData
        );
        setAppointments((prev) =>
          prev.map((apt) => (apt.id === appointmentId ? data : apt))
        );
        return data;
      } catch (err: any) {
        setError(err.message || 'Failed to reschedule appointment');
        throw err;
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  const cancelAppointment = useCallback(async (appointmentId: string) => {
    setIsLoading(true);
    setError(null);

    try {
      // DELETE /api/v1/appointments/{id}
      await apiClient.delete(`/api/v1/appointments/${appointmentId}`);
      setAppointments((prev) => prev.filter((apt) => apt.id !== appointmentId));
    } catch (err: any) {
      setError(err.message || 'Failed to cancel appointment');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Auto-fetch appointments on mount or when filters change
  useEffect(() => {
    if (options.enabled) {
      fetchAppointments();
    }
  }, [fetchAppointments, options.enabled]);

  return {
    appointments,
    fetchAppointments,
    fetchAvailableSlots,
    createAppointment,
    updateAppointmentStatus,
    rescheduleAppointment,
    cancelAppointment,
    isLoading,
    error,
  };
}
