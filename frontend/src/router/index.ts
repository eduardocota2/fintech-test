import { createRouter, createWebHistory } from 'vue-router'

import { authGuard } from './guards'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: '/applications',
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginView.vue'),
      meta: { guestOnly: true },
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('../views/RegisterView.vue'),
      meta: { guestOnly: true },
    },
    {
      path: '/applications',
      name: 'applications',
      component: () => import('../views/ApplicationsView.vue'),
      meta: { requiresAuth: true, requiresAdmin: true },
    },
    {
      path: '/forbidden',
      name: 'forbidden',
      component: () => import('../views/ForbiddenView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/:pathMatch(.*)*',
      redirect: '/applications',
    },
  ],
})

router.beforeEach(authGuard)

export default router
