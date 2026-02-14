/**
 * TypeScript types matching backend schemas
 * Reference: backend/README.md
 */

// ============================================
// User & Authentication Types
// ============================================

export interface User {
  id: string;
  email: string;
  full_name: string;
  phone: string | null;
  city: string | null;
  role: 'admin' | 'pet_owner';
  is_active: boolean;
  preferences: Record<string, any> | null;
  created_at: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  full_name: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface LogoutResponse {
  message: string;
}

// ============================================
// User Profile Types
// ============================================

export interface UserProfileResponse {
  id: string;
  full_name: string;
  email: string;
  phone: string | null;
  city: string | null;
  role: 'admin' | 'pet_owner';
  is_active: boolean;
  preferences: Record<string, any> | null;
  created_at: string;
}

export interface UserProfileUpdate {
  full_name?: string;
  email?: string;
  phone?: string;
  city?: string;
  preferences?: Record<string, any>;
}

// ============================================
// Pet Types
// ============================================

export interface Pet {
  id: string;
  name: string;
  species: string;
  breed: string | null;
  notes: string | null;
  date_of_birth: string | null;
  last_vaccination: string | null;
  medical_history: Record<string, any>;
  owner_id: string;
  created_at: string;
  updated_at: string;
}

export interface PetCreateRequest {
  name: string;
  species: string;
  breed?: string;
  notes?: string;
  date_of_birth?: string;
  last_vaccination?: string;
  medical_history?: Record<string, any>;
}

export interface PetUpdateRequest {
  name?: string;
  species?: string;
  breed?: string;
  notes?: string;
  date_of_birth?: string;
  last_vaccination?: string;
  medical_history?: Record<string, any>;
}

// ============================================
// Appointment Types
// ============================================

export type AppointmentStatus = 'pending' | 'confirmed' | 'cancelled' | 'completed';
export type ServiceType = 'vaccination' | 'routine' | 'surgery' | 'emergency';

export interface Appointment {
  id: string;
  pet_id: string;
  start_time: string;
  end_time: string;
  service_type: ServiceType;
  status: AppointmentStatus;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface AppointmentCreateRequest {
  pet_id: string;
  start_time: string;
  service_type: ServiceType;
  notes?: string;
}

export interface AppointmentUpdateStatusRequest {
  status: AppointmentStatus;
}

export interface AppointmentRescheduleRequest {
  start_time: string;
  end_time: string;
}

export interface AppointmentFilters {
  status?: AppointmentStatus;
  from_date?: string;
  to_date?: string;
}

// ============================================
// Clinic Status Types
// ============================================

export type ClinicStatusType = 'open' | 'close' | 'closing_soon';

export interface ClinicStatus {
  id: number;
  status: ClinicStatusType;
  updated_at: string;
}

export interface ClinicStatusUpdateRequest {
  status: ClinicStatusType;
}

// ============================================
// Error Response Types
// ============================================

export interface ErrorResponse {
  detail: string;
  error_type: string;
  timestamp: string;
}

export interface ValidationError {
  loc: (string | number)[];
  msg: string;
  type: string;
}

export interface HTTPValidationError {
  detail: ValidationError[];
}

// ============================================
// API Response Types
// ============================================

export interface ApiError {
  message: string;
  status: number;
  errors?: ValidationError[];
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}
