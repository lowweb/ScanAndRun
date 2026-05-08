import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/HomeView.vue')
  },
  {
    path: '/movement',
    name: 'Movement',
    component: () => import('@/views/MovementView.vue')
  },
  {
    path: '/history',
    name: 'History',
    component: () => import('@/views/HistoryView.vue')
  },
  {
    path: '/not-active',
    name: 'NotActive',
    component: () => import('@/views/NotActiveView.vue')
  },
  {
    path: '/equipment',
    name: 'Equipment',
    component: () => import('@/views/EquipmentView.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
