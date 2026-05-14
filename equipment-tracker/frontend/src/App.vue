<template>
  <v-app>
    <v-app-bar v-if="isAuthenticated" color="primary" dark>
      <v-app-bar-title>Equipment Tracker</v-app-bar-title>
      <v-spacer></v-spacer>
      <v-btn to="/" text>Главная</v-btn>
      <v-btn to="/movement" text>Перемещение</v-btn>
      <v-btn to="/history" text>История</v-btn>
      <v-btn to="/not-active" text>Вне работы</v-btn>
      <v-btn to="/equipment" text>Оборудование</v-btn>
      
      <v-menu location="bottom end">
        <template v-slot:activator="{ props }">
          <v-btn v-bind="props" icon>
            <v-icon>mdi-account-circle</v-icon>
          </v-btn>
        </template>
        <v-list>
          <v-list-item>
            <div class="pa-2">
              <div class="text-subtitle-2">{{ currentUser?.full_name }}</div>
              <div class="text-caption text-medium-emphasis">{{ currentUser?.role?.name }}</div>
              <div class="text-caption text-medium-emphasis">{{ currentUser?.department?.name }}</div>
            </div>
          </v-list-item>
          <v-divider></v-divider>
          <v-list-item @click="handleLogout" prepend-icon="mdi-logout">
            <v-list-item-title>Выйти</v-list-item-title>
          </v-list-item>
        </v-list>
      </v-menu>
    </v-app-bar>
  
    <v-main>
      <v-container fluid>
        <router-view />
      </v-container>
    </v-main>

    <v-footer v-if="isAuthenticated" color="grey lighten-3" padless>
      <v-container class="py-4">
        <div class="text-center grey--text text-body-2">
          © {{ new Date().getFullYear() }} Equipment Tracker. Система учета оборудования.
        </div>
      </v-container>
    </v-footer>
  </v-app>
</template>

<script setup>
import { onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useEquipmentStore, useAuthStore } from '@/stores'
import { storeToRefs } from 'pinia'

const router = useRouter()
const equipmentStore = useEquipmentStore()
const authStore = useAuthStore()
const { isAuthenticated, currentUser } = storeToRefs(authStore)

onMounted(async () => {
  // Check authentication first
  if (authStore.token && !authStore.user) {
    await authStore.checkAuth()
  }
  
  // Load initial data only if authenticated
  if (isAuthenticated.value) {
    await equipmentStore.fetchEquipmentTypes()
    await equipmentStore.fetchDepartments()
    await equipmentStore.fetchUsers()
    await equipmentStore.fetchRoles()
    if (equipmentStore.currentEquipmentType) {
      await equipmentStore.fetchStatuses(equipmentStore.currentEquipmentType.id)
    }
  }
})

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}
</script>

<style>
.v-application {
  background-color: #f5f5f5 !important;
}
</style>
