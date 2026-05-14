<template>
  <v-container class="fill-height d-flex align-center justify-center">
    <v-card class="pa-6" max-width="400" elevation="8">
      <div class="text-center mb-6">
        <v-icon size="64" color="primary" class="mb-2">mdi-package-variant</v-icon>
        <h1 class="text-h4 font-weight-bold">Equipment Tracker</h1>
        <p class="text-subtitle-1 text-medium-emphasis">Система учета оборудования</p>
      </div>

      <v-form @submit.prevent="handleLogin" ref="formRef">
        <v-text-field
          v-model="login"
          label="Логин"
          prepend-inner-icon="mdi-account"
          variant="outlined"
          :rules="[rules.required]"
          :disabled="loading"
          class="mb-4"
        />

        <v-text-field
          v-model="password"
          label="Пароль"
          prepend-inner-icon="mdi-lock"
          :type="showPassword ? 'text' : 'password'"
          :append-inner-icon="showPassword ? 'mdi-eye-off' : 'mdi-eye'"
          @click:append-inner="showPassword = !showPassword"
          variant="outlined"
          :rules="[rules.required]"
          :disabled="loading"
          class="mb-4"
        />

        <v-alert
          v-if="error"
          type="error"
          variant="tonal"
          class="mb-4"
          closable
          @click:close="error = null"
        >
          {{ error }}
        </v-alert>

        <v-btn
          type="submit"
          color="primary"
          size="large"
          block
          :loading="loading"
          variant="elevated"
        >
          Войти
        </v-btn>
      </v-form>

      <div class="text-center mt-4 text-caption text-medium-emphasis">
        <p>Тестовые учетные данные:</p>
        <p><strong>admin / 123</strong> - Администратор</p>
        <p><strong>ivanov / 123</strong> - Пользователь</p>
      </div>
    </v-card>
  </v-container>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores'
import { storeToRefs } from 'pinia'

const router = useRouter()
const authStore = useAuthStore()
const { isAuthenticated } = storeToRefs(authStore)

const login = ref('')
const password = ref('')
const showPassword = ref(false)
const loading = ref(false)
const error = ref(null)
const formRef = ref(null)

const rules = {
  required: value => !!value || 'Обязательное поле'
}

const handleLogin = async () => {
  const { valid } = await formRef.value.validate()
  if (!valid) return

  loading.value = true
  error.value = null

  try {
    await authStore.login(login.value, password.value)
    router.push('/')
  } catch (err) {
    error.value = err.response?.data?.detail || 'Ошибка входа. Проверьте логин и пароль.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.v-card {
  border-radius: 16px;
}
</style>
