<template>
  <v-app>
    <v-app-bar color="primary" dark>
      <v-app-bar-title>Equipment Tracker</v-app-bar-title>
      <v-spacer></v-spacer>
      <v-btn to="/" text>Главная</v-btn>
      <v-btn to="/movement" text>Перемещение</v-btn>
      <v-btn to="/history" text>История</v-btn>
      <v-btn to="/not-active" text>Вне работы</v-btn>
      <v-btn to="/equipment" text>Оборудование</v-btn>
    </v-app-bar>

    <v-main>
      <v-container fluid>
        <router-view />
      </v-container>
    </v-main>

    <v-footer color="grey lighten-3" padless>
      <v-container class="py-4">
        <div class="text-center grey--text text-body-2">
          © {{ new Date().getFullYear() }} Equipment Tracker. Система учета оборудования.
        </div>
      </v-container>
    </v-footer>
  </v-app>
</template>

<script setup>
import { onMounted } from 'vue'
import { useEquipmentStore } from '@/stores'

const equipmentStore = useEquipmentStore()

onMounted(async () => {
  await equipmentStore.fetchEquipmentTypes()
  await equipmentStore.fetchDepartments()
  await equipmentStore.fetchUsers()
  await equipmentStore.fetchRoles()
  if (equipmentStore.currentEquipmentType) {
    await equipmentStore.fetchStatuses(equipmentStore.currentEquipmentType.id)
  }
})
</script>

<style>
.v-application {
  background-color: #f5f5f5 !important;
}
</style>
