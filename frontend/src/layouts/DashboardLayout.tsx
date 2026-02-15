/**
 * Dashboard Layout Component
 */

import type { ReactNode } from 'react';
import { Navbar } from './Navbar';

interface DashboardLayoutProps {
  children: ReactNode;
}

export function DashboardLayout({ children }: DashboardLayoutProps) {
  return (
    <div style={{ minHeight: '100vh' }}>
      <Navbar />
      <main className="container page">
        {children}
      </main>
    </div>
  );
}
