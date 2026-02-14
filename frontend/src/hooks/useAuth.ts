/**
 * Authentication Hook
 * Handles login, register, logout API calls
 * Reference: backend/README.md - Authentication endpoints
 */

import { useState } from 'react';
import { apiClient } from '../lib/api-client';
import { useAuth as useAuthContext } from '../contexts/AuthContext';
import {
  LoginRequest,
  RegisterRequest,
  TokenResponse,
  LogoutResponse,
  UserProfileResponse,
} from '../types';
import { jwtDecode } from 'jwt-decode';

interface JWTPayload {
  sub: string; // user_id
  role: string;
  exp: number;
}

export function useAuthActions() {
  const { login: setAuth, logout: clearAuth } = useAuthContext();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const register = async (data: RegisterRequest) => {
    setIsLoading(true);
    setError(null);

    try {
      // POST /api/v1/auth/register
      const response = await apiClient.post<TokenResponse>('/api/v1/auth/register', data);
      
      // Decode JWT to get user info
      const decoded = jwtDecode<JWTPayload>(response.access_token);
      
      // Fetch full user profile
      const userProfile = await apiClient.get<UserProfileResponse>('/api/v1/users/profile');
      
      setAuth(response.access_token, {
        id: decoded.sub,
        email: data.email,
        full_name: data.full_name,
        phone: userProfile.phone,
        city: userProfile.city,
        role: decoded.role as 'admin' | 'pet_owner',
        is_active: userProfile.is_active,
        preferences: userProfile.preferences,
        created_at: userProfile.created_at,
      });

      return response;
    } catch (err: any) {
      setError(err.message || 'Registration failed');
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (data: LoginRequest) => {
    setIsLoading(true);
    setError(null);

    try {
      // POST /api/v1/auth/login
      const response = await apiClient.post<TokenResponse>('/api/v1/auth/login', data);
      
      // Store token temporarily to fetch profile
      localStorage.setItem('access_token', response.access_token);
      
      // Decode JWT to get user info
      const decoded = jwtDecode<JWTPayload>(response.access_token);
      
      // Fetch full user profile
      const userProfile = await apiClient.get<UserProfileResponse>('/api/v1/users/profile');
      
      setAuth(response.access_token, {
        id: decoded.sub,
        email: userProfile.email,
        full_name: userProfile.full_name,
        phone: userProfile.phone,
        city: userProfile.city,
        role: decoded.role as 'admin' | 'pet_owner',
        is_active: userProfile.is_active,
        preferences: userProfile.preferences,
        created_at: userProfile.created_at,
      });

      return response;
    } catch (err: any) {
      setError(err.message || 'Login failed');
      localStorage.removeItem('access_token');
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    setIsLoading(true);
    setError(null);

    try {
      // POST /api/v1/auth/logout
      await apiClient.post<LogoutResponse>('/api/v1/auth/logout');
    } catch (err: any) {
      // Even if logout fails on backend, clear local state
      console.error('Logout error:', err);
    } finally {
      clearAuth();
      setIsLoading(false);
    }
  };

  return {
    register,
    login,
    logout,
    isLoading,
    error,
  };
}
