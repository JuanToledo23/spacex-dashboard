import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Overview',
    component: () => import('@/views/OverviewView.vue'),
  },
  {
    path: '/launches',
    name: 'Launches',
    component: () => import('@/views/LaunchesView.vue'),
  },
  {
    path: '/fleet',
    name: 'Fleet',
    component: () => import('@/views/FleetView.vue'),
  },
  {
    path: '/starlink',
    name: 'Starlink',
    component: () => import('@/views/StarlinkView.vue'),
  },
  {
    path: '/economics',
    name: 'Economics',
    component: () => import('@/views/EconomicsView.vue'),
  },
  {
    path: '/launches/:id',
    name: 'LaunchDetail',
    component: () => import('@/views/LaunchDetailView.vue'),
  },
  {
    path: '/rockets/:id',
    name: 'RocketDetail',
    component: () => import('@/views/RocketDetailView.vue'),
  },
  {
    path: '/history',
    name: 'History',
    component: () => import('@/views/HistoryView.vue'),
  },
  {
    path: '/landing',
    name: 'Landing',
    component: () => import('@/views/LandingView.vue'),
  },
  {
    path: '/starman',
    name: 'Starman',
    component: () => import('@/views/StarmanView.vue'),
  },
  {
    path: '/emissions',
    name: 'Emissions',
    component: () => import('@/views/EmissionsView.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
