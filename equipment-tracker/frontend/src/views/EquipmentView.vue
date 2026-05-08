<template>
  <v-container>
    <v-row class="mb-4">
      <v-col cols="12" md="6">
        <h1 class="text-h4 font-weight-bold">Оборудование</h1>
      </v-col>
      <v-col cols="12" md="6" class="d-flex justify-end align-center">
        <v-btn color="primary" @click="showAddDialog = true">
          <v-icon start>mdi-plus</v-icon>
          Добавить оборудование
        </v-btn>
      </v-col>
    </v-row>

    <!-- Фильтры -->
    <v-row class="mb-4">
      <v-col cols="12">
        <v-card>
          <v-card-text>
            <v-row>
              <v-col cols="12" md="3">
                <v-select
                  v-model="filters.equipmentTypeId"
                  :items="equipmentStore.equipmentTypes"
                  item-title="name"
                  item-value="id"
                  label="Тип оборудования"
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
                  hide-details
                  clearable
                ></v-select>
              </v-col>
              <v-col cols="12" md="3">
                <v-text-field
                  v-model="filters.barcode"
                  label="Штрих-код"
                  hide-details
                  clearable
                  @keyup.enter="applyFilters"
                ></v-text-field>
              </v-col>
              <v-col cols="12" md="3">
                <v-btn color="primary" @click="applyFilters" block>
                  <v-icon start>mdi-magnify</v-icon>
                  Поиск
                </v-btn>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Таблица оборудования -->
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title class="text-h6">
            Все оборудование ({{ equipment.length }})
          </v-card-title>
          <v-card-text>
            <v-data-table
              :headers="headers"
              :items="equipment"
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
              <template v-slot:item.actions="{ item }">
                <v-btn
                  icon="mdi-pencil"
                  size="small"
                  variant="text"
                  @click="editEquipment(item)"
                ></v-btn>
              </template>
            </v-data-table>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Диалог добавления/редактирования -->
    <v-dialog v-model="showAddDialog" max-width="600">
      <v-card>
        <v-card-title class="text-h5">
          {{ editMode ? 'Редактировать' : 'Добавить' }} оборудование
        </v-card-title>
        <v-card-text>
          <v-text-field
            v-model="formData.name"
            label="Название"
            hide-details
            class="mb-3"
          ></v-text-field>
          <v-text-field
            v-model="formData.barcode"
            label="Штрих-код"
            :readonly="editMode"
            hide-details
            class="mb-3"
          ></v-text-field>
          <v-select
            v-model="formData.equipmentTypeId"
            :items="equipmentStore.equipmentTypes"
            item-title="name"
            item-value="id"
            label="Тип оборудования"
            hide-details
            class="mb-3"
          ></v-select>
          <v-select
            v-model="formData.statusId"
            :items="currentStatuses"
            item-title="name"
            item-value="id"
            label="Статус"
            hide-details
            class="mb-3"
          ></v-select>
          <v-select
            v-model="formData.departmentId"
            :items="equipmentStore.departments"
            item-title="name"
            item-value="id"
            label="Департамент"
            hide-details
            class="mb-3"
            clearable
          ></v-select>
          <v-select
            v-model="formData.userId"
            :items="equipmentStore.users"
            item-title="full_name"
            item-value="id"
            label="Пользователь"
            hide-details
            class="mb-3"
            clearable
          ></v-select>
          <v-textarea
            v-model="formData.comment"
            label="Комментарий"
            rows="3"
            hide-details
          ></v-textarea>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text @click="closeDialog">Отмена</v-btn>
          <v-btn color="primary" @click="saveEquipment">Сохранить</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import { useEquipmentStore } from '@/stores'

const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api'

const equipmentStore = useEquipmentStore()

const loading = ref(false)
const equipment = ref([])
const showAddDialog = ref(false)
const editMode = ref(false)

const filters = ref({
  equipmentTypeId: null,
  departmentId: null,
  barcode: null
})

const formData = ref({
  id: null,
  name: '',
  barcode: '',
  equipmentTypeId: null,
  statusId: null,
  departmentId: null,
  userId: null,
  comment: ''
})

const headers = [
  { title: 'Штрих-код', key: 'barcode', sortable: true },
  { title: 'Название', key: 'name', sortable: true },
  { title: 'Тип', key: 'equipment_type.name', sortable: true },
  { title: 'Статус', key: 'status_id', sortable: true },
  { title: 'Департамент', key: 'department_id', sortable: true },
  { title: 'Пользователь', key: 'user_id', sortable: true },
  { title: 'Действия', key: 'actions', sortable: false }
]

const currentStatuses = computed(() => {
  if (!formData.value.equipmentTypeId) return []
  return equipmentStore.getStatusesForType(formData.value.equipmentTypeId)
})

onMounted(async () => {
  await loadEquipment()
})

const loadEquipment = async () => {
  loading.value = true
  try {
    const params = {}
    if (filters.value.equipmentTypeId) params.equipment_type_id = filters.value.equipmentTypeId
    if (filters.value.departmentId) params.department_id = filters.value.departmentId
    if (filters.value.barcode) params.barcode = filters.value.barcode
    
    const response = await axios.get(`${API_BASE}/equipment`, { params })
    equipment.value = response.data
  } catch (error) {
    console.error('Error loading equipment:', error)
  } finally {
    loading.value = false
  }
}

const applyFilters = () => {
  loadEquipment()
}

const editEquipment = (item) => {
  editMode.value = true
  formData.value = {
    id: item.id,
    name: item.name,
    barcode: item.barcode,
    equipmentTypeId: item.equipment_type_id,
    statusId: item.status_id,
    departmentId: item.department_id,
    userId: item.user_id,
    comment: item.comment || ''
  }
  showAddDialog.value = true
}

const closeDialog = () => {
  showAddDialog.value = false
  editMode.value = false
  resetForm()
}

const resetForm = () => {
  formData.value = {
    id: null,
    name: '',
    barcode: '',
    equipmentTypeId: equipmentStore.equipmentTypes[0]?.id || null,
    statusId: null,
    departmentId: null,
    userId: null,
    comment: ''
  }
}

const saveEquipment = async () => {
  try {
    if (editMode.value) {
      // Update existing
      await axios.put(`${API_BASE}/equipment/${formData.value.id}`, null, {
        params: {
          name: formData.value.name,
          status_id: formData.value.statusId,
          department_id: formData.value.departmentId,
          user_id: formData.value.userId,
          comment: formData.value.comment
        }
      })
    } else {
      // Create new
      await axios.post(`${API_BASE}/equipment`, null, {
        params: {
          name: formData.value.name,
          barcode: formData.value.barcode,
          equipment_type_id: formData.value.equipmentTypeId,
          status_id: formData.value.statusId,
          department_id: formData.value.departmentId,
          user_id: formData.value.userId,
          comment: formData.value.comment,
          created_by_id: equipmentStore.users[0]?.id || 1
        }
      })
    }
    
    closeDialog()
    await loadEquipment()
  } catch (error) {
    alert('Ошибка при сохранении: ' + error.message)
  }
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
