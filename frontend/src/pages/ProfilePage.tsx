/**
 * User Profile Page
 */

import { useState } from 'react';
import { useRouter, useNavigate } from '@tanstack/react-router';
import { Card } from '../components/ui/Card';
import { ProfileForm } from '../components/profile/ProfileForm';
import { useUserProfile } from '../hooks/useUsers';
import { useAuthActions } from '../hooks/useAuth';
import { apiClient } from '../lib/api-client';
import { format } from 'date-fns';
import type { UserProfileResponse } from '../types';

interface ProfilePageProps {
  profile: UserProfileResponse;
}

export function ProfilePage({ profile }: ProfilePageProps) {
  const router = useRouter();
  const navigate = useNavigate();
  const { updateProfile, error } = useUserProfile();
  const { logout } = useAuthActions();

  // Delete account state
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [deletePassword, setDeletePassword] = useState('');
  const [deleteError, setDeleteError] = useState<string | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  const handleUpdate = async (data: any) => {
    await updateProfile(data);
    router.invalidate();
  };

  const handleDeleteAccount = async () => {
    if (!deletePassword.trim()) return;

    setIsDeleting(true);
    setDeleteError(null);

    try {
      await apiClient.post('/api/v1/users/profile/delete', {
        password: deletePassword,
      });

      // Account deleted — log out and go home
      await logout();
      navigate({ to: '/' });
    } catch (err: any) {
      setDeleteError(err.message || 'Failed to delete account. Please check your password.');
    } finally {
      setIsDeleting(false);
    }
  };

  const closeDeleteModal = () => {
    setShowDeleteModal(false);
    setDeletePassword('');
    setDeleteError(null);
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

      {/* Danger Zone */}
      <div className="danger-zone">
        <h2 className="danger-zone-title">Danger Zone</h2>
        <p className="danger-zone-description">
          Deleting your account will permanently remove all your pet profiles, medical history, and upcoming appointments.
        </p>
        <button
          className="danger-zone-btn"
          onClick={() => setShowDeleteModal(true)}
        >
          Delete My Account
        </button>
      </div>

      {/* Delete Confirmation Modal */}
      {showDeleteModal && (
        <div className="modal-overlay" onClick={closeDeleteModal}>
          <div className="modal-content danger-modal" onClick={(e) => e.stopPropagation()}>
            <h2 className="danger-modal-header">Are you absolutely sure?</h2>
            <p className="danger-modal-warning">
              This action is irreversible. All data related to your pets and scheduled appointments will be lost.
            </p>

            <div className="danger-modal-field">
              <label htmlFor="delete-password" className="danger-modal-label">
                Please enter your password to confirm
              </label>
              <input
                id="delete-password"
                type="password"
                className="danger-modal-input"
                value={deletePassword}
                onChange={(e) => setDeletePassword(e.target.value)}
                placeholder="Enter your password"
                autoFocus
              />
            </div>

            {deleteError && (
              <p className="danger-modal-error">{deleteError}</p>
            )}

            <div className="danger-modal-actions">
              <button
                className="danger-modal-cancel"
                onClick={closeDeleteModal}
                disabled={isDeleting}
              >
                Cancel
              </button>
              <button
                className="danger-modal-confirm"
                onClick={handleDeleteAccount}
                disabled={!deletePassword.trim() || isDeleting}
              >
                {isDeleting ? 'Deleting...' : 'Confirm Permanent Deletion'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
