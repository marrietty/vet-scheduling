/**
 * Login Page
 */

import { Link } from '@tanstack/react-router';
import { LoginForm } from '../components/auth/LoginForm';
import { Card } from '../components/ui/Card';

export function LoginPage() {
  return (
    <div className="flex items-center justify-center" style={{ minHeight: '100vh', padding: '1rem' }}>
      <div className="w-full max-w-md">
        <div className="text-center mb-4">
          <h1 className="text-3xl font-bold">Welcome Back</h1>
          <p className="text-gray-600" style={{ marginTop: '0.5rem' }}>Sign in to your account</p>
        </div>

        <Card>
          <LoginForm />
          <div className="text-center text-sm" style={{ marginTop: '1rem' }}>
            <span className="text-gray-600">Don't have an account? </span>
            <Link to="/register" className="font-medium" style={{ color: 'var(--color-primary)' }}>
              Register here
            </Link>
          </div>
        </Card>
      </div>
    </div>
  );
}
