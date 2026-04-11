<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import type { AuthForm } from '../models'
import { loginUser } from '../services/auth.service'
import { authStore } from '../stores/auth'

const router = useRouter()
const route = useRoute()

const form = reactive<AuthForm>({
  email: '',
  password: '',
  is_admin: false,
})

const busy = ref(false)
const error = ref('')

function errorMessage(exc: unknown): string {
  return exc instanceof Error ? exc.message : String(exc)
}

async function submitLogin(): Promise<void> {
  busy.value = true
  error.value = ''

  try {
    const payload = await loginUser(form.email, form.password)
    authStore.setSession(payload.access_token, payload.token_type || 'bearer')

    const target = typeof route.query.redirect === 'string' ? route.query.redirect : '/applications'
    await router.replace(target)
  } catch (exc) {
    error.value = `Login fallido: ${errorMessage(exc)}`
  } finally {
    busy.value = false
  }
}
</script>

<template>
  <section class="card auth-card">
    <h2>Iniciar sesion</h2>
    <label>Email
      <input v-model="form.email" type="email" placeholder="admin@example.com" />
    </label>
    <label>Password
      <input v-model="form.password" type="password" placeholder="Password123!" />
    </label>

    <div class="actions">
      <button :disabled="busy" @click="submitLogin">Entrar</button>
      <RouterLink class="link-btn" to="/register">Ir a registro</RouterLink>
    </div>

    <p v-if="error" class="notice error">{{ error }}</p>
  </section>
</template>

<style scoped>
.auth-card {
  max-width: 520px;
  margin: 0 auto;
}
</style>
