/**
 * Register Form Component
 */

import { useState, FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { Input } from '../ui/Input';
import { Button } from '../ui/Button';
import { Alert } from '../ui/Alert';
import { useAuthActions } from '../../hooks/useAuth';

export function RegisterForm() {
  const navigate = useNavigate();
  const { register, isLoading, error } = useAuthActions();
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    full_name: '',
    confirmPassword: '',
  });
  const [validationError, setValidationError] = useState('');

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setValidationError('');

    // Validate password
    if (formData.password.length < 8) {
      setValidationError('Password must be at least 8 characters long');
      return;
    }

    if (formData.password !== formData.confirmPassword) {
      setValidationError('Passwords do not match');
      return;
    }

    try {
      await register({
        email: formData.email,
        password: formData.password,
        full_name: formData.full_name,
      });
      navigate('/dashboard');
    } catch (err) {
      // Error is handled by the hook
    }
  };

  return (
    <form onSubmit={handleSubmit} className="form">
      {(error || validationError) && (
        <Alert type="error" title="Registration Failed">
          {error || validationError}
        </Alert>
      )}

      <Input
        label="Full Name"
        type="text"
        value={formData.full_name}
        onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
        required
        placeholder="John Doe"
      />

      <Input
        label="Email"
        type="email"
        value={formData.email}
        onChange={(e) => setFormData({ ...formData, email: e.target.value })}
        required
        placeholder="john@example.com"
      />

      <Input
        label="Password"
        type="password"
        value={formData.password}
        onChange={(e) => setFormData({ ...formData, password: e.target.value })}
        required
        placeholder="At least 8 characters"
        helperText="Password must be at least 8 characters long"
      />

      <Input
        label="Confirm Password"
        type="password"
        value={formData.confirmPassword}
        onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
        required
        placeholder="Confirm your password"
      />

      <Button type="submit" isLoading={isLoading} className="w-full">
        Create Account
      </Button>
    </form>
  );
}
