import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', component: () => import('@/views/DashboardView.vue') },
  { path: '/MPU6050', component: () => import('@/views/Mpu6050View.vue') },
  { path: '/MAX30102', component: () => import('@/views/Max30102View.vue') },
  { path: '/LDR', component: () => import('@/views/LdrView.vue') },
  { path: '/TableView', component: () => import('@/views/TableView.vue') },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: routes,
})

export default router
