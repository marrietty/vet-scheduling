/**
 * Dashboard Page
 */

import { useEffect } from 'react';
import { Link } from 'react-router-dom';
import { DashboardLayout } from '../layouts/DashboardLayout';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { useAuth } from '../contexts/AuthContext';
import { usePets } from '../hooks/usePets';
import { useAppointments } from '../hooks/useAppointments';
import { useClinicStatus } from '../hooks/useClinic';

export function DashboardPage() {
  const { user } = useAuth();
  const { pets } = usePets();
  const { appointments } = useAppointments();
  const { status } = useClinicStatus();

  const upcomingAppointments = appointments.filter(
    (apt) => new Date(apt.start_time) > new Date() && apt.status !== 'cancelled'
  );

  const getClinicStatusColor = () => {
    if (!status) return 'var(--color-gray-600)';
    switch (status.status) {
      case 'open':
        return 'var(--color-success)';
      case 'closing_soon':
        return 'var(--color-warning)';
      case 'closed':
        return 'var(--color-danger)';
      default:
        return 'var(--color-gray-600)';
    }
  };

  return (
    <DashboardLayout>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
        {/* Welcome Section */}
        <div>
          <h1 className="text-3xl font-bold">
            Welcome back, {user?.full_name}!
          </h1>
          <p className="text-gray-600" style={{ marginTop: '0.5rem' }}>
            {user?.role === 'admin' ? 'Admin Dashboard' : 'Manage your pets and appointments'}
          </p>
        </div>

        {/* Clinic Status */}
        {status && (
          <Card>
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold">Clinic Status</h3>
                <p className="text-2xl font-bold" style={{ color: getClinicStatusColor(), textTransform: 'capitalize' }}>
                  {status.status.replace('_', ' ')}
                </p>
              </div>
              <svg width="64" height="64" fill="none" viewBox="0 0 24 24" stroke="currentColor" style={{ color: 'var(--color-gray-300)' }}>
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
              </svg>
            </div>
          </Card>
        )}

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <Card>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Pets</p>
                <p className="text-3xl font-bold">{pets.length}</p>
              </div>
              <svg width="48" height="48" fill="none" viewBox="0 0 24 24" stroke="currentColor" style={{ color: 'var(--color-primary)' }}>
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 10h4.764a2 2 0 011.789 2.894l-3.5 7A2 2 0 0115.263 21h-4.017c-.163 0-.326-.02-.485-.06L7 20m7-10V5a2 2 0 00-2-2h-.095c-.5 0-.905.405-.905.905 0 .714-.211 1.412-.608 2.006L7 11v9m7-10h-2M7 20H5a2 2 0 01-2-2v-6a2 2 0 012-2h2.5" />
              </svg>
            </div>
            <Link to="/pets" style={{ marginTop: '1rem', display: 'block' }}>
              <Button size="sm" variant="secondary" className="w-full">
                Manage Pets
              </Button>
            </Link>
          </Card>

          <Card>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Upcoming Appointments</p>
                <p className="text-3xl font-bold">{upcomingAppointments.length}</p>
              </div>
              <svg width="48" height="48" fill="none" viewBox="0 0 24 24" stroke="currentColor" style={{ color: 'var(--color-success)' }}>
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            </div>
            <Link to="/appointments" style={{ marginTop: '1rem', display: 'block' }}>
              <Button size="sm" variant="secondary" className="w-full">
                View Appointments
              </Button>
            </Link>
          </Card>

          <Card>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Quick Actions</p>
                <p className="text-lg font-semibold">Book Now</p>
              </div>
              <svg width="48" height="48" fill="none" viewBox="0 0 24 24" stroke="currentColor" style={{ color: '#9333ea' }}>
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
            </div>
            <Link to="/appointments/new" style={{ marginTop: '1rem', display: 'block' }}>
              <Button size="sm" className="w-full">
                New Appointment
              </Button>
            </Link>
          </Card>
        </div>

        {/* Recent Activity */}
        {upcomingAppointments.length > 0 && (
          <Card title="Upcoming Appointments">
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              {upcomingAppointments.slice(0, 3).map((apt) => (
                <div key={apt.id} className="flex justify-between items-center" style={{ 
                  padding: '0.75rem', 
                  backgroundColor: 'var(--color-gray-50)', 
                  borderRadius: 'var(--radius-lg)' 
                }}>
                  <div>
                    <p className="font-medium">
                      {new Date(apt.start_time).toLocaleDateString()}
                    </p>
                    <p className="text-sm text-gray-600" style={{ textTransform: 'capitalize' }}>{apt.service_type}</p>
                  </div>
                  <span className="badge badge-primary">
                    {apt.status}
                  </span>
                </div>
              ))}
            </div>
          </Card>
        )}
      </div>
    </DashboardLayout>
  );
}
