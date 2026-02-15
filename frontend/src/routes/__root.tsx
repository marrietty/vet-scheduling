/**
 * Root Route — wraps all routes in the application.
 * Uses createRootRouteWithContext to pass auth state down to all child routes.
 */

import { createRootRouteWithContext, Outlet } from '@tanstack/react-router'
import type { AuthContextType } from '../contexts/AuthContext'

interface RouterContext {
    auth: AuthContextType
}

export const Route = createRootRouteWithContext<RouterContext>()({
    component: RootComponent,
})

function RootComponent() {
    return <Outlet />
}
