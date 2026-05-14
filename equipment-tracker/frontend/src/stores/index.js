import { defineStore } from 'pinia'
import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api'

// Create axios instance with auth interceptor
const apiClient = axios.create({
  baseURL: API_BASE,
})

apiClient.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: localStorage.getItem('access_token') || null,
  }),

  getters: {
    isAuthenticated: (state) => !!state.token,
    isAdmin: (state) => state.user?.role?.name === 'admin',
    currentUser: (state) => state.user,
  },

  actions: {
    async login(login, password) {
      try {
        const response = await apiClient.post('/auth/login', { login, password })
        this.token = response.data.access_token
        this.user = response.data.user
        localStorage.setItem('access_token', this.token)
        return response.data
      } catch (error) {
        console.error('Login error:', error)
        throw error
      }
    },

    logout() {
      this.user = null
      this.token = null
      localStorage.removeItem('access_token')
    },

    async checkAuth() {
      if (!this.token) {
        return false
      }
      try {
        const response = await apiClient.get('/auth/me')
        this.user = response.data
        return true
      } catch (error) {
        this.logout()
        return false
      }
    },
  },
})

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
        const response = await apiClient.get('/equipment-types')
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
          ? `/statuses?equipment_type_id=${equipmentTypeId}`
          : '/statuses'
        const response = await apiClient.get(url)
        this.statuses = response.data
      } catch (error) {
        console.error('Error fetching statuses:', error)
      }
    },

    async fetchDepartments() {
      try {
        const response = await apiClient.get('/departments')
        this.departments = response.data
      } catch (error) {
        console.error('Error fetching departments:', error)
      }
    },

    async fetchUsers() {
      try {
        const response = await apiClient.get('/users')
        this.users = response.data
      } catch (error) {
        console.error('Error fetching users:', error)
      }
    },

    async fetchRoles() {
      try {
        const response = await apiClient.get('/roles')
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
        const response = await apiClient.get(`/equipment?${params}`)
        this.equipment = response.data
        return response.data
      } catch (error) {
        console.error('Error fetching equipment:', error)
        throw error
      }
    },

    async getEquipmentByBarcode(barcode) {
      try {
        const response = await apiClient.get(`/equipment/${barcode}`)
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
        const response = await apiClient.post('/movement/change-status', null, {
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
        const response = await apiClient.post('/equipment', null, {
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
        const response = await apiClient.get(`/movement-history?${params}`)
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
