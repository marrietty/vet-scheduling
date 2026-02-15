/**
 * Router instance — created with the auto-generated route tree.
 * The context shape (auth) is passed from the React component tree via RouterProvider.
 */

import { createRouter } from '@tanstack/react-router'
import { routeTree } from './routeTree.gen'

export const router = createRouter({
    routeTree,
    context: {
        // auth will be passed from the React component tree
        auth: undefined!,
    },
    defaultPreload: 'intent',
})

// Register the router for type safety
declare module '@tanstack/react-router' {
    interface Register {
        router: typeof router
    }
}
