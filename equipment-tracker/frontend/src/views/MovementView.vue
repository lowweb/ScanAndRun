<template>
  <v-container>
    <v-row class="mb-4">
      <v-col cols="12">
        <h1 class="text-h4 font-weight-bold">Перемещение оборудования</h1>
      </v-col>
    </v-row>

    <!-- Выбор типа оборудования -->
    <v-row class="mb-4">
      <v-col cols="12" md="6">
        <v-card>
          <v-card-title class="text-h6">Тип оборудования</v-card-title>
          <v-card-text>
            <v-btn-toggle
              v-model="selectedTypeIndex"
              mandatory
              color="primary"
              class="d-flex flex-wrap"
            >
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

    <v-row>
      <!-- Сканирование ШК -->
      <v-col cols="12" lg="6">
        <v-card>
          <v-card-title class="text-h6">Сканирование штрих-кодов</v-card-title>
          <v-card-text>
            <v-text-field
              v-model="barcodeInput"
              label="Штрих-код"
              placeholder="Отсканируйте или введите ШК"
              prepend-inner-icon="mdi-barcode-scan"
              @keyup.enter="addBarcode"
              clearable
              hide-details
              class="mb-3"
            ></v-text-field>

            <v-btn 
              color="primary" 
              block 
              @click="showScanner = !showScanner"
              class="mb-3"
            >
              <v-icon start>mdi-camera</v-icon>
              {{ showScanner ? 'Закрыть сканер' : 'Открыть сканер ШК' }}
            </v-btn>

            <!-- Компонент сканера -->
            <div v-if="showScanner" class="scanner-container mb-3">
              <QrcodeStream 
                @detect="onDetect"
                :track="defaultTrackFunction"
                class="scanner-video"
              />
            </div>

            <v-chip-group column v-if="scannedBarcodes.length > 0">
              <v-chip
                v-for="(barcode, index) in scannedBarcodes"
                :key="barcode"
                closable
                @click:close="removeBarcode(index)"
                color="primary"
                variant="tonal"
                class="mr-2 mb-2"
              >
                {{ barcode }}
              </v-chip>
            </v-chip-group>

            <v-alert
              v-if="scannedBarcodes.length === 0"
              type="info"
              variant="tonal"
              class="mt-3"
            >
              Отсканируйте один или несколько штрих-кодов
            </v-alert>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- Выбор статуса -->
      <v-col cols="12" lg="6">
        <v-card>
          <v-card-title class="text-h6">Выбор статуса</v-card-title>
          <v-card-text>
            <v-select
              v-model="selectedStatusId"
              :items="currentStatuses"
              item-title="name"
              item-value="id"
              label="Новый статус"
              prepend-inner-icon="mdi-tag"
              hide-details
              class="mb-3"
            ></v-select>

            <v-textarea
              v-model="comment"
              label="Комментарий"
              rows="3"
              prepend-inner-icon="mdi-comment-text"
              hide-details
              class="mb-3"
            ></v-textarea>

            <v-select
              v-if="isMoveStatus"
              v-model="targetUserId"
              :items="equipmentStore.users"
              item-title="full_name"
              item-value="id"
              label="Целевой пользователь (обязательно)"
              prepend-inner-icon="mdi-account"
              :rules="[v => !!v || 'Пользователь обязателен']"
              hide-details
              class="mb-3"
            ></v-select>

            <v-btn
              color="success"
              block
              size="large"
              @click="changeStatus"
              :disabled="!canChangeStatus"
              class="mt-2"
            >
              <v-icon start>mdi-check-circle</v-icon>
              Применить статус
            </v-btn>

            <v-alert
              v-if="lastResult"
              :type="lastResult.success ? 'success' : 'error'"
              variant="tonal"
              class="mt-3"
            >
              {{ lastResult.message }}
            </v-alert>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Список отсканированного оборудования -->
    <v-row v-if="scannedEquipment.length > 0" class="mt-4">
      <v-col cols="12">
        <v-card>
          <v-card-title class="text-h6">Отсканированное оборудование</v-card-title>
          <v-card-text>
            <v-table density="compact">
              <thead>
                <tr>
                  <th>Штрих-код</th>
                  <th>Название</th>
                  <th>Текущий статус</th>
                  <th>Департамент</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="eq in scannedEquipment" :key="eq.id">
                  <td>{{ eq.barcode }}</td>
                  <td>{{ eq.name }}</td>
                  <td>
                    <v-chip size="small" color="info">{{ eq.status?.name }}</v-chip>
                  </td>
                  <td>{{ eq.department?.name || '-' }}</td>
                </tr>
              </tbody>
            </v-table>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Диалог добавления нового оборудования -->
    <v-dialog v-model="showAddDialog" max-width="600">
      <v-card>
        <v-card-title class="text-h5">Добавить новое оборудование</v-card-title>
        <v-card-text>
          <v-text-field
            v-model="newEquipment.barcode"
            label="Штрих-код"
            readonly
            hide-details
            class="mb-3"
          ></v-text-field>
          <v-text-field
            v-model="newEquipment.name"
            label="Название"
            hide-details
            class="mb-3"
          ></v-text-field>
          <v-select
            v-model="newEquipment.departmentId"
            :items="equipmentStore.departments"
            item-title="name"
            item-value="id"
            label="Департамент"
            hide-details
            class="mb-3"
          ></v-select>
          <v-select
            v-model="newEquipment.statusId"
            :items="currentStatuses"
            item-title="name"
            item-value="id"
            label="Статус"
            hide-details
            class="mb-3"
          ></v-select>
          <v-textarea
            v-model="newEquipment.comment"
            label="Комментарий"
            rows="2"
            hide-details
          ></v-textarea>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text @click="showAddDialog = false">Отмена</v-btn>
          <v-btn color="primary" @click="addNewEquipment">Добавить</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useEquipmentStore } from '@/stores'
import { QrcodeStream } from 'vue-qrcode-reader'

const equipmentStore = useEquipmentStore()

const selectedTypeIndex = ref(0)
const barcodeInput = ref('')
const scannedBarcodes = ref([])
const scannedEquipment = ref([])
const selectedStatusId = ref(null)
const comment = ref('')
const targetUserId = ref(null)
const showScanner = ref(false)
const showAddDialog = ref(false)
const lastResult = ref(null)

const newEquipment = ref({
  barcode: '',
  name: '',
  departmentId: null,
  statusId: null,
  comment: ''
})

const currentType = computed(() => {
  return equipmentStore.equipmentTypes[selectedTypeIndex.value] || null
})

const currentStatuses = computed(() => {
  if (!currentType.value) return []
  return equipmentStore.getStatusesForType(currentType.value.id)
})

const isMoveStatus = computed(() => {
  const status = currentStatuses.value.find(s => s.id === selectedStatusId.value)
  return status?.name === 'Перемещение'
})

const canChangeStatus = computed(() => {
  if (scannedBarcodes.value.length === 0 || !selectedStatusId.value) return false
  if (isMoveStatus.value && !targetUserId.value) return false
  return true
})

watch(selectedTypeIndex, async () => {
  if (currentType.value) {
    equipmentStore.setCurrentEquipmentType(currentType.value)
  }
})

const addBarcode = async () => {
  if (!barcodeInput.value.trim()) return
  
  const barcode = barcodeInput.value.trim()
  
  // Проверяем, есть ли уже такой ШК
  if (scannedBarcodes.value.includes(barcode)) {
    barcodeInput.value = ''
    return
  }
  
  // Проверяем наличие в базе
  try {
    const equipment = await equipmentStore.getEquipmentByBarcode(barcode)
    if (equipment) {
      scannedBarcodes.value.push(barcode)
      scannedEquipment.value.push(equipment)
    } else {
      // Оборудование не найдено - предлагаем добавить
      newEquipment.value = {
        barcode: barcode,
        name: '',
        departmentId: null,
        statusId: selectedStatusId.value || null,
        comment: ''
      }
      showAddDialog.value = true
    }
  } catch (error) {
    console.error('Error checking barcode:', error)
  }
  
  barcodeInput.value = ''
}

const removeBarcode = (index) => {
  scannedBarcodes.value.splice(index, 1)
  scannedEquipment.value.splice(index, 1)
}

const onDetect = async (detectedCodes) => {
  if (detectedCodes && detectedCodes.length > 0) {
    const barcode = detectedCodes[0].rawValue
    barcodeInput.value = barcode
    await addBarcode()
  }
}

const defaultTrackFunction = {
  camera: 'auto',
  facingMode: 'environment'
}

const changeStatus = async () => {
  if (!canChangeStatus.value) return
  
  try {
    const currentUserId = equipmentStore.users[0]?.id || 1 // Default to first user
    
    const result = await equipmentStore.changeStatus(
      scannedBarcodes.value,
      selectedStatusId.value,
      currentUserId,
      comment.value,
      targetUserId.value
    )
    
    const successCount = result.results.filter(r => r.success).length
    const failCount = result.results.filter(r => !r.success).length
    
    lastResult.value = {
      success: true,
      message: `Успешно изменено: ${successCount}, Ошибок: ${failCount}`
    }
    
    // Очищаем после успешного изменения
    scannedBarcodes.value = []
    scannedEquipment.value = []
    comment.value = ''
    targetUserId.value = null
    
    setTimeout(() => {
      lastResult.value = null
    }, 5000)
  } catch (error) {
    lastResult.value = {
      success: false,
      message: 'Ошибка при изменении статуса: ' + error.message
    }
  }
}

const addNewEquipment = async () => {
  try {
    await equipmentStore.createEquipment({
      name: newEquipment.value.name,
      barcode: newEquipment.value.barcode,
      equipment_type_id: currentType.value.id,
      status_id: newEquipment.value.statusId || selectedStatusId.value,
      department_id: newEquipment.value.departmentId,
      comment: newEquipment.value.comment,
      created_by_id: equipmentStore.users[0]?.id || 1
    })
    
    showAddDialog.value = false
    scannedBarcodes.value.push(newEquipment.value.barcode)
    
    // Загружаем информацию о только что добавленном оборудовании
    const equipment = await equipmentStore.getEquipmentByBarcode(newEquipment.value.barcode)
    if (equipment) {
      scannedEquipment.value.push(equipment)
    }
  } catch (error) {
    alert('Ошибка при добавлении оборудования: ' + error.message)
  }
}
</script>

<style scoped>
.scanner-container {
  width: 100%;
  max-width: 400px;
  margin: 0 auto;
  border-radius: 8px;
  overflow: hidden;
}

.scanner-video {
  width: 100%;
  height: auto;
}
</style>
