/**
 * User Profile Form Component
 */

import { useState, useEffect } from 'react';
import type { FormEvent } from 'react';
import { Input } from '../ui/Input';
import { Button } from '../ui/Button';
import { Alert } from '../ui/Alert';
import type { UserProfileResponse, UserProfileUpdate } from '../../types';

interface ProfileFormProps {
  profile: UserProfileResponse;
  onSubmit: (data: UserProfileUpdate) => Promise<void>;
  error: string | null;
}

export function ProfileForm({ profile, onSubmit, error }: ProfileFormProps) {
  const [formData, setFormData] = useState({
    full_name: profile.full_name,
    email: profile.email,
    phone: profile.phone || '',
    city: profile.city || '',
  });
  const [success, setSuccess] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [phoneError, setPhoneError] = useState<string | null>(null);

  useEffect(() => {
    setFormData({
      full_name: profile.full_name,
      email: profile.email,
      phone: profile.phone || '',
      city: profile.city || '',
    });
  }, [profile]);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setSuccess(false);
    setSubmitError(null);
    setPhoneError(null);

    // Client-side phone validation
    if (formData.phone && !/^\+?[\d\s\-()]{7,20}$/.test(formData.phone)) {
      setPhoneError('Please enter a valid phone number (e.g. +1-555-0123)');
      return;
    }

    const updates: UserProfileUpdate = {};
    if (formData.full_name !== profile.full_name) updates.full_name = formData.full_name;
    if (formData.email !== profile.email) updates.email = formData.email;
    if (formData.phone !== (profile.phone || '')) updates.phone = formData.phone || undefined;
    if (formData.city !== (profile.city || '')) updates.city = formData.city || undefined;

    if (Object.keys(updates).length === 0) {
      return;
    }

    setIsSubmitting(true);

    try {
      await onSubmit(updates);
      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
    } catch (err: any) {
      setSubmitError(err.message || 'Failed to update profile');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="form">
      {success && (
        <Alert type="success" title="Success">
          Profile updated successfully!
        </Alert>
      )}

      {(error || submitError) && (
        <Alert type="error" title="Error">
          {submitError || error}
        </Alert>
      )}

      <Input
        label="Full Name"
        type="text"
        value={formData.full_name}
        onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
        required
      />

      <Input
        label="Email"
        type="email"
        value={formData.email}
        onChange={(e) => setFormData({ ...formData, email: e.target.value })}
        required
      />

      <Input
        label="Phone"
        type="tel"
        value={formData.phone}
        onChange={(e) => {
          setFormData({ ...formData, phone: e.target.value });
          setPhoneError(null);
        }}
        placeholder="+1-555-0123"
        error={phoneError || undefined}
      />

      <Input
        label="City"
        type="text"
        value={formData.city}
        onChange={(e) => setFormData({ ...formData, city: e.target.value })}
        placeholder="San Francisco"
      />

      <div style={{ paddingTop: '1rem' }}>
        <Button type="submit" isLoading={isSubmitting} disabled={isSubmitting}>
          Update Profile
        </Button>
      </div>
    </form>
  );
}
