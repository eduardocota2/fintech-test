import type { NavigationGuardNext, RouteLocationNormalized } from 'vue-router'

import { authStore } from '../stores/auth'

function redirectToLogin(to: RouteLocationNormalized, next: NavigationGuardNext): void {
  next({
    name: 'login',
    query: { redirect: to.fullPath },
  })
}

export function authGuard(to: RouteLocationNormalized, _from: RouteLocationNormalized, next: NavigationGuardNext): void {
  const requiresAuth = Boolean(to.meta.requiresAuth)
  const requiresAdmin = Boolean(to.meta.requiresAdmin)
  const guestOnly = Boolean(to.meta.guestOnly)

  if (guestOnly && authStore.isAuthenticated.value) {
    next({ name: 'applications' })
    return
  }

  if (requiresAuth && !authStore.isAuthenticated.value) {
    redirectToLogin(to, next)
    return
  }

  if (requiresAdmin && !authStore.state.isAdmin) {
    next({ name: 'forbidden' })
    return
  }

  next()
}
