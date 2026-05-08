<template>
  <v-container>
    <v-row class="mb-4">
      <v-col cols="12">
        <h1 class="text-h4 font-weight-bold">История перемещений</h1>
      </v-col>
    </v-row>

    <!-- Фильтры -->
    <v-row class="mb-4">
      <v-col cols="12">
        <v-card>
          <v-card-title class="text-h6 d-flex align-center">
            <v-icon start>mdi-filter-variant</v-icon>
            Фильтры
          </v-card-title>
          <v-card-text>
            <v-row>
              <v-col cols="12" md="3">
                <v-text-field
                  v-model="filters.equipmentName"
                  label="Название оборудования"
                  prepend-inner-icon="mdi-magnify"
                  hide-details
                  clearable
                ></v-text-field>
              </v-col>
              <v-col cols="12" md="3">
                <v-select
                  v-model="filters.userId"
                  :items="equipmentStore.users"
                  item-title="full_name"
                  item-value="id"
                  label="Пользователь"
                  prepend-inner-icon="mdi-account"
                  hide-details
                  clearable
                ></v-select>
              </v-col>
              <v-col cols="12" md="3">
                <v-select
                  v-model="filters.departmentId"
                  :items="equipmentStore.departments"
                  item-title="name"
                  item-value="id"
                  label="Департамент"
                  prepend-inner-icon="mdi-office-building"
                  hide-details
                  clearable
                ></v-select>
              </v-col>
              <v-col cols="12" md="3">
                <v-btn color="primary" @click="applyFilters" block>
                  <v-icon start>mdi-check</v-icon>
                  Применить
                </v-btn>
              </v-col>
            </v-row>
            <v-row class="mt-2">
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="filters.startDate"
                  label="Дата начала"
                  type="date"
                  prepend-inner-icon="mdi-calendar-start"
                  hide-details
                  clearable
                ></v-text-field>
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="filters.endDate"
                  label="Дата окончания"
                  type="date"
                  prepend-inner-icon="mdi-calendar-end"
                  hide-details
                  clearable
                ></v-text-field>
              </v-col>
            </v-row>
            <v-row class="mt-2">
              <v-col cols="12">
                <v-btn text color="grey" @click="clearFilters">
                  <v-icon start>mdi-refresh</v-icon>
                  Сбросить фильтры
                </v-btn>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Таблица истории -->
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title class="text-h6">
            Записи истории ({{ history.length }})
          </v-card-title>
          <v-card-text>
            <v-data-table
              :headers="headers"
              :items="history"
              :loading="loading"
              density="compact"
              hover
              items-per-page="25"
            >
              <template v-slot:item.created_at="{ value }">
                {{ formatDate(value) }}
              </template>
              <template v-slot:item.status_id="{ item }">
                <v-chip size="small" :color="getStatusColor(item.status?.name)">
                  {{ item.status?.name }}
                </v-chip>
              </template>
              <template v-slot:item.department_id="{ item }">
                {{ item.department?.name || '-' }}
              </template>
              <template v-slot:item.user_id="{ item }">
                {{ item.user?.full_name }}
              </template>
              <template v-slot:item.comment="{ value }">
                <span v-if="value" class="text-truncate" style="max-width: 200px; display: inline-block;">
                  {{ value }}
                </span>
                <span v-else class="text-grey">-</span>
              </template>
            </v-data-table>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useHistoryStore, useEquipmentStore } from '@/stores'

const historyStore = useHistoryStore()
const equipmentStore = useEquipmentStore()

const loading = ref(false)
const filters = ref({
  equipmentName: null,
  userId: null,
  departmentId: null,
  startDate: null,
  endDate: null
})

const headers = [
  { title: 'Дата/Время', key: 'created_at', sortable: true },
  { title: 'Оборудование', key: 'equipment.name', sortable: true },
  { title: 'Штрих-код', key: 'equipment.barcode', sortable: true },
  { title: 'Статус', key: 'status_id', sortable: true },
  { title: 'Департамент', key: 'department_id', sortable: true },
  { title: 'Пользователь', key: 'user_id', sortable: true },
  { title: 'Комментарий', key: 'comment', sortable: false }
]

const history = computed(() => historyStore.history)

onMounted(async () => {
  await loadHistory()
})

const loadHistory = async () => {
  loading.value = true
  try {
    await historyStore.fetchHistory(filters.value)
  } catch (error) {
    console.error('Error loading history:', error)
  } finally {
    loading.value = false
  }
}

const applyFilters = () => {
  loadHistory()
}

const clearFilters = () => {
  filters.value = {
    equipmentName: null,
    userId: null,
    departmentId: null,
    startDate: null,
    endDate: null
  }
  loadHistory()
}

const formatDate = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleString('ru-RU', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const getStatusColor = (statusName) => {
  if (!statusName) return 'grey'
  const colors = {
    'МОЛ': 'success',
    'Заправка': 'warning',
    'Склад - на заправку': 'orange',
    'Склад - выдача': 'blue',
    'Склад': 'info',
    'Склад утилизация': 'error',
    'В ремонте': 'red',
    'ИТ отдел': 'purple',
    'Перемещение': 'amber'
  }
  return colors[statusName] || 'grey'
}
</script>
