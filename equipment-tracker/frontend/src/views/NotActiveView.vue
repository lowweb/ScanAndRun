<template>
  <v-container>
    <v-row class="mb-4">
      <v-col cols="12">
        <h1 class="text-h4 font-weight-bold">Оборудование вне работы</h1>
        <p class="text-body-1 text-grey mt-2">
          Оборудование, которое не находится в статусе "МОЛ" (в работе)
        </p>
      </v-col>
    </v-row>

    <!-- Переключатель типа оборудования -->
    <v-row class="mb-4">
      <v-col cols="12" md="6">
        <v-card>
          <v-card-text>
            <v-btn-toggle
              v-model="selectedTypeIndex"
              mandatory
              color="primary"
              class="d-flex flex-wrap"
            >
              <v-btn :value="null" variant="tonal">Все типы</v-btn>
              <v-btn
                v-for="(type, index) in equipmentStore.equipmentTypes"
                :key="type.id"
                :value="index"
                variant="tonal"
              >
                {{ type.name }}
              </v-btn>
            </v-btn-toggle>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Таблица оборудования -->
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title class="text-h6 d-flex align-center">
            <v-icon start>mdi-alert-circle</v-icon>
            Оборудование вне работы ({{ notActiveEquipment.length }})
          </v-card-title>
          <v-card-text>
            <v-data-table
              :headers="headers"
              :items="notActiveEquipment"
              :loading="loading"
              hover
              items-per-page="25"
            >
              <template v-slot:item.barcode="{ value }">
                <v-chip size="small" color="primary">{{ value }}</v-chip>
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
                {{ item.user?.full_name || '-' }}
              </template>
              <template v-slot:item.updated_at="{ value }">
                {{ formatDate(value) }}
              </template>
              <template v-slot:item.actions="{ item }">
                <v-btn
                  icon="mdi-eye"
                  size="small"
                  variant="text"
                  @click="showDetails(item)"
                ></v-btn>
              </template>
            </v-data-table>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Диалог деталей -->
    <v-dialog v-model="showDetailsDialog" max-width="600">
      <v-card v-if="selectedEquipment">
        <v-card-title class="text-h5">{{ selectedEquipment.name }}</v-card-title>
        <v-card-text>
          <v-list density="compact">
            <v-list-item>
              <v-list-item-title class="text-grey">Штрих-код</v-list-item-title>
              <v-list-item-subtitle>{{ selectedEquipment.barcode }}</v-list-item-subtitle>
            </v-list-item>
            <v-list-item>
              <v-list-item-title class="text-grey">Тип</v-list-item-title>
              <v-list-item-subtitle>{{ selectedEquipment.equipment_type?.name }}</v-list-item-subtitle>
            </v-list-item>
            <v-list-item>
              <v-list-item-title class="text-grey">Статус</v-list-item-title>
              <v-list-item-subtitle>
                <v-chip size="small" :color="getStatusColor(selectedEquipment.status?.name)">
                  {{ selectedEquipment.status?.name }}
                </v-chip>
              </v-list-item-subtitle>
            </v-list-item>
            <v-list-item>
              <v-list-item-title class="text-grey">Департамент</v-list-item-title>
              <v-list-item-subtitle>{{ selectedEquipment.department?.name || '-' }}</v-list-item-subtitle>
            </v-list-item>
            <v-list-item>
              <v-list-item-title class="text-grey">Пользователь</v-list-item-title>
              <v-list-item-subtitle>{{ selectedEquipment.user?.full_name || '-' }}</v-list-item-subtitle>
            </v-list-item>
            <v-list-item>
              <v-list-item-title class="text-grey">Комментарий</v-list-item-title>
              <v-list-item-subtitle>{{ selectedEquipment.comment || '-' }}</v-list-item-subtitle>
            </v-list-item>
            <v-list-item>
              <v-list-item-title class="text-grey">Обновлено</v-list-item-title>
              <v-list-item-subtitle>{{ formatDate(selectedEquipment.updated_at) }}</v-list-item-subtitle>
            </v-list-item>
          </v-list>

          <v-divider class="my-3"></v-divider>

          <v-card-title class="text-h6">История перемещений</v-card-title>
          <v-timeline density="compact" side="end">
            <v-timeline-item
              v-for="history in selectedEquipment.movement_history"
              :key="history.id"
              dot-color="primary"
              size="small"
            >
              <div class="d-flex justify-space-between align-center mb-1">
                <strong>{{ history.status?.name }}</strong>
                <small class="text-grey">{{ formatDate(history.created_at) }}</small>
              </div>
              <div class="text-body-2">{{ history.comment }}</div>
            </v-timeline-item>
          </v-timeline>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text @click="showDetailsDialog = false">Закрыть</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import axios from 'axios'
import { useEquipmentStore } from '@/stores'

const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api'

const equipmentStore = useEquipmentStore()

const loading = ref(false)
const notActiveEquipment = ref([])
const selectedTypeIndex = ref(null)
const showDetailsDialog = ref(false)
const selectedEquipment = ref(null)

const headers = [
  { title: 'Штрих-код', key: 'barcode', sortable: true },
  { title: 'Название', key: 'name', sortable: true },
  { title: 'Тип', key: 'equipment_type.name', sortable: true },
  { title: 'Статус', key: 'status_id', sortable: true },
  { title: 'Департамент', key: 'department_id', sortable: true },
  { title: 'Пользователь', key: 'user_id', sortable: true },
  { title: 'Обновлено', key: 'updated_at', sortable: true },
  { title: 'Действия', key: 'actions', sortable: false }
]

const currentTypeId = computed(() => {
  if (selectedTypeIndex.value === null) return null
  return equipmentStore.equipmentTypes[selectedTypeIndex.value]?.id || null
})

onMounted(async () => {
  await loadNotActiveEquipment()
})

watch(currentTypeId, () => {
  loadNotActiveEquipment()
})

const loadNotActiveEquipment = async () => {
  loading.value = true
  try {
    const params = {}
    if (currentTypeId.value) {
      params.equipment_type_id = currentTypeId.value
    }
    
    const response = await axios.get(`${API_BASE}/equipment/not-active`, { params })
    notActiveEquipment.value = response.data
  } catch (error) {
    console.error('Error loading not active equipment:', error)
  } finally {
    loading.value = false
  }
}

const showDetails = async (equipment) => {
  selectedEquipment.value = equipment
  showDetailsDialog.value = true
  
  // Загружаем полную историю для этого оборудования
  try {
    const response = await axios.get(`${API_BASE}/movement-history`, {
      params: { equipment_id: equipment.id }
    })
    selectedEquipment.value.movement_history = response.data
  } catch (error) {
    console.error('Error loading history:', error)
  }
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
