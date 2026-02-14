/**
 * User Profile Page
 */

import { useEffect } from 'react';
import { DashboardLayout } from '../layouts/DashboardLayout';
import { Card } from '../components/ui/Card';
import { ProfileForm } from '../components/profile/ProfileForm';
import { useUserProfile } from '../hooks/useUsers';
import { useAuth } from '../contexts/AuthContext';
import { format } from 'date-fns';

export function ProfilePage() {
  const { user } = useAuth();
  const { profile, fetchProfile, updateProfile, isLoading, error } = useUserProfile();

  useEffect(() => {
    fetchProfile();
  }, [fetchProfile]);

  if (!profile) {
    return (
      <DashboardLayout>
        <div className="flex justify-center items-center" style={{ height: '16rem' }}>
          <svg className="spinner" width="48" height="48" fill="none" viewBox="0 0 24 24">
            <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" opacity="0.25" style={{ color: 'var(--color-primary)' }} />
            <path fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" opacity="0.75" style={{ color: 'var(--color-primary)' }} />
          </svg>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
        <div>
          <h1 className="text-3xl font-bold">Profile Settings</h1>
          <p className="text-gray-600" style={{ marginTop: '0.5rem' }}>Manage your account information</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div style={{ gridColumn: 'span 2 / span 2' }}>
            <Card title="Personal Information">
              <ProfileForm
                profile={profile}
                onSubmit={updateProfile}
                isLoading={isLoading}
                error={error}
              />
            </Card>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            <Card title="Account Details">
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                <div>
                  <p className="text-sm text-gray-600">Role</p>
                  <p className="font-medium" style={{ textTransform: 'capitalize' }}>{profile.role.replace('_', ' ')}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Account Status</p>
                  <p className="font-medium">
                    {profile.is_active ? (
                      <span style={{ color: 'var(--color-success)' }}>Active</span>
                    ) : (
                      <span style={{ color: 'var(--color-danger)' }}>Inactive</span>
                    )}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Member Since</p>
                  <p className="font-medium">
                    {format(new Date(profile.created_at), 'MMM dd, yyyy')}
                  </p>
                </div>
              </div>
            </Card>

            {profile.preferences && Object.keys(profile.preferences).length > 0 && (
              <Card title="Preferences">
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                  {Object.entries(profile.preferences).map(([key, value]) => (
                    <div key={key} className="flex justify-between">
                      <span className="text-sm text-gray-600" style={{ textTransform: 'capitalize' }}>{key}:</span>
                      <span className="text-sm font-medium">
                        {typeof value === 'boolean' ? (value ? 'Yes' : 'No') : String(value)}
                      </span>
                    </div>
                  ))}
                </div>
              </Card>
            )}
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
