import { defineStore } from 'pinia'
import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api'

export const useEquipmentStore = defineStore('equipment', {
  state: () => ({
    equipmentTypes: [],
    statuses: [],
    departments: [],
    users: [],
    roles: [],
    equipment: [],
    currentEquipmentType: null
  }),

  getters: {
    getStatusesForType: (state) => (typeId) => {
      return state.statuses.filter(s => s.equipment_type_id === typeId)
    },
    getEquipmentByBarcode: (state) => (barcode) => {
      return state.equipment.find(e => e.barcode === barcode)
    }
  },

  actions: {
    async fetchEquipmentTypes() {
      try {
        const response = await axios.get(`${API_BASE}/equipment-types`)
        this.equipmentTypes = response.data
        if (!this.currentEquipmentType && this.equipmentTypes.length > 0) {
          this.currentEquipmentType = this.equipmentTypes[0]
        }
      } catch (error) {
        console.error('Error fetching equipment types:', error)
      }
    },

    async fetchStatuses(equipmentTypeId = null) {
      try {
        const url = equipmentTypeId 
          ? `${API_BASE}/statuses?equipment_type_id=${equipmentTypeId}`
          : `${API_BASE}/statuses`
        const response = await axios.get(url)
        this.statuses = response.data
      } catch (error) {
        console.error('Error fetching statuses:', error)
      }
    },

    async fetchDepartments() {
      try {
        const response = await axios.get(`${API_BASE}/departments`)
        this.departments = response.data
      } catch (error) {
        console.error('Error fetching departments:', error)
      }
    },

    async fetchUsers() {
      try {
        const response = await axios.get(`${API_BASE}/users`)
        this.users = response.data
      } catch (error) {
        console.error('Error fetching users:', error)
      }
    },

    async fetchRoles() {
      try {
        const response = await axios.get(`${API_BASE}/roles`)
        this.roles = response.data
      } catch (error) {
        console.error('Error fetching roles:', error)
      }
    },

    async fetchEquipment(filters = {}) {
      try {
        const params = new URLSearchParams()
        Object.keys(filters).forEach(key => {
          if (filters[key] !== null && filters[key] !== undefined) {
            params.append(key, filters[key])
          }
        })
        const response = await axios.get(`${API_BASE}/equipment?${params}`)
        this.equipment = response.data
        return response.data
      } catch (error) {
        console.error('Error fetching equipment:', error)
        throw error
      }
    },

    async getEquipmentByBarcode(barcode) {
      try {
        const response = await axios.get(`${API_BASE}/equipment/${barcode}`)
        return response.data
      } catch (error) {
        if (error.response?.status === 404) {
          return null
        }
        throw error
      }
    },

    setCurrentEquipmentType(type) {
      this.currentEquipmentType = type
      this.fetchStatuses(type.id)
    },

    async changeStatus(barcodes, statusId, userId, comment = null, targetUserId = null) {
      try {
        const response = await axios.post(`${API_BASE}/movement/change-status`, null, {
          params: {
            barcodes,
            status_id: statusId,
            user_id: userId,
            comment,
            target_user_id: targetUserId
          }
        })
        return response.data
      } catch (error) {
        console.error('Error changing status:', error)
        throw error
      }
    },

    async createEquipment(equipmentData) {
      try {
        const response = await axios.post(`${API_BASE}/equipment`, null, {
          params: equipmentData
        })
        return response.data
      } catch (error) {
        console.error('Error creating equipment:', error)
        throw error
      }
    }
  }
})

export const useHistoryStore = defineStore('history', {
  state: () => ({
    history: [],
    filters: {
      equipmentId: null,
      userId: null,
      departmentId: null,
      startDate: null,
      endDate: null,
      equipmentName: null
    }
  }),

  actions: {
    async fetchHistory(filters = {}) {
      try {
        const params = new URLSearchParams()
        Object.keys(filters).forEach(key => {
          if (filters[key] !== null && filters[key] !== undefined) {
            if (filters[key] instanceof Date) {
              params.append(key, filters[key].toISOString())
            } else {
              params.append(key, filters[key])
            }
          }
        })
        const response = await axios.get(`${API_BASE}/movement-history?${params}`)
        this.history = response.data
        return response.data
      } catch (error) {
        console.error('Error fetching history:', error)
        throw error
      }
    },

    setFilters(filters) {
      this.filters = { ...this.filters, ...filters }
    },

    clearFilters() {
      this.filters = {
        equipmentId: null,
        userId: null,
        departmentId: null,
        startDate: null,
        endDate: null,
        equipmentName: null
      }
    }
  }
})
