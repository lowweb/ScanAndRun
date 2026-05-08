<template>
  <v-container>
    <v-row class="mb-6">
      <v-col cols="12">
        <h1 class="text-h4 font-weight-bold">Система учета оборудования</h1>
        <p class="text-body-1 text-grey mt-2">
          Добро пожаловать в систему учета движения оборудования. Выберите действие в меню или используйте быстрые ссылки ниже.
        </p>
      </v-col>
    </v-row>

    <v-row>
      <v-col cols="12" md="6" lg="3" v-for="card in cards" :key="card.title">
        <v-card 
          class="pa-4 text-center hover-card cursor-pointer"
          @click="$router.push(card.route)"
          height="200"
        >
          <v-card-text>
            <v-icon size="64" color="primary" class="mb-4">{{ card.icon }}</v-icon>
            <div class="text-h6 font-weight-bold">{{ card.title }}</div>
            <div class="text-body-2 text-grey mt-2">{{ card.description }}</div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <v-row class="mt-8">
      <v-col cols="12">
        <v-card>
          <v-card-title class="text-h5">Статистика</v-card-title>
          <v-card-text>
            <v-row>
              <v-col cols="6" md="3">
                <div class="text-center">
                  <div class="text-h4 text-primary">{{ equipmentStore.equipmentTypes.length }}</div>
                  <div class="text-body-2 text-grey">Типов оборудования</div>
                </div>
              </v-col>
              <v-col cols="6" md="3">
                <div class="text-center">
                  <div class="text-h4 text-success">{{ equipmentStore.departments.length }}</div>
                  <div class="text-body-2 text-grey">Департаментов</div>
                </div>
              </v-col>
              <v-col cols="6" md="3">
                <div class="text-center">
                  <div class="text-h4 text-info">{{ equipmentStore.users.length }}</div>
                  <div class="text-body-2 text-grey">Пользователей</div>
                </div>
              </v-col>
              <v-col cols="6" md="3">
                <div class="text-center">
                  <div class="text-h4 text-warning">{{ equipmentStore.statuses.length }}</div>
                  <div class="text-body-2 text-grey">Статусов</div>
                </div>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { computed } from 'vue'
import { useEquipmentStore } from '@/stores'

const equipmentStore = useEquipmentStore()

const cards = [
  {
    title: 'Перемещение',
    description: 'Изменение статуса оборудования по штрих-коду',
    icon: 'mdi-swap-horizontal-circle',
    route: '/movement'
  },
  {
    title: 'История перемещений',
    description: 'Просмотр истории с фильтрацией',
    icon: 'mdi-history',
    route: '/history'
  },
  {
    title: 'Вне работы',
    description: 'Оборудование не в статусе "В работе"',
    icon: 'mdi-alert-circle',
    route: '/not-active'
  },
  {
    title: 'Оборудование',
    description: 'Добавление и просмотр оборудования',
    icon: 'mdi-desktop-classic',
    route: '/equipment'
  }
]
</script>

<style scoped>
.hover-card {
  transition: transform 0.2s, box-shadow 0.2s;
}

.hover-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
}

.cursor-pointer {
  cursor: pointer;
}
</style>
