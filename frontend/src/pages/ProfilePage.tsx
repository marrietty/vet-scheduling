/**
 * User Profile Page
 */

import { useRouter } from '@tanstack/react-router';
import { Card } from '../components/ui/Card';
import { ProfileForm } from '../components/profile/ProfileForm';
import { useUserProfile } from '../hooks/useUsers';
import { format } from 'date-fns';
import type { UserProfileResponse } from '../types';

interface ProfilePageProps {
  profile: UserProfileResponse;
}

export function ProfilePage({ profile }: ProfilePageProps) {
  const router = useRouter();
  const { updateProfile, error } = useUserProfile();

  const handleUpdate = async (data: any) => {
    await updateProfile(data);
    router.invalidate();
  };

  return (
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
              onSubmit={handleUpdate}
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
  );
}
