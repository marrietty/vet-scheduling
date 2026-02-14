/**
 * Navigation Bar Component
 */

import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useAuthActions } from '../hooks/useAuth';
import { Button } from '../components/ui/Button';

export function Navbar() {
  const { user, isAuthenticated } = useAuth();
  const { logout } = useAuthActions();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-brand">
          <svg width="32" height="32" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
          </svg>
          <span style={{ marginLeft: '0.5rem' }}>Vet Clinic</span>
        </Link>

        <ul className="navbar-nav">
          {isAuthenticated ? (
            <>
              <li><Link to="/dashboard" className="navbar-link">Dashboard</Link></li>
              <li><Link to="/pets" className="navbar-link">My Pets</Link></li>
              <li><Link to="/appointments" className="navbar-link">Appointments</Link></li>
              {user?.role === 'admin' && (
                <li><Link to="/admin" className="navbar-link">Admin</Link></li>
              )}
              <li><Link to="/profile" className="navbar-link">Profile</Link></li>
              <li>
                <Button size="sm" variant="secondary" onClick={handleLogout}>
                  Logout
                </Button>
              </li>
            </>
          ) : (
            <>
              <li>
                <Link to="/login">
                  <Button size="sm" variant="secondary">Login</Button>
                </Link>
              </li>
              <li>
                <Link to="/register">
                  <Button size="sm">Register</Button>
                </Link>
              </li>
            </>
          )}
        </ul>
      </div>
    </nav>
  );
}
