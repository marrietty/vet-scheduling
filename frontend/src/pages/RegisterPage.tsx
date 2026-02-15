/**
 * Register Page
 */

import { Link } from '@tanstack/react-router';
import { RegisterForm } from '../components/auth/RegisterForm';
import { Card } from '../components/ui/Card';

export function RegisterPage() {
  return (
    <div className="flex items-center justify-center" style={{ minHeight: '100vh', padding: '1rem' }}>
      <div className="w-full max-w-md">
        <div className="text-center mb-4">
          <h1 className="text-3xl font-bold">Create Account</h1>
          <p className="text-gray-600" style={{ marginTop: '0.5rem' }}>Join our vet clinic community</p>
        </div>

        <Card>
          <RegisterForm />
          <div className="text-center text-sm" style={{ marginTop: '1rem' }}>
            <span className="text-gray-600">Already have an account? </span>
            <Link to="/login" className="font-medium" style={{ color: 'var(--color-primary)' }}>
              Sign in here
            </Link>
          </div>
        </Card>
      </div>
    </div>
  );
}
