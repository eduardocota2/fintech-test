<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

import type { AuthForm } from '../models'
import { registerUser } from '../services/auth.service'

const router = useRouter()

const form = reactive<AuthForm>({
  email: '',
  password: '',
  is_admin: false,
})

const busy = ref(false)
const message = ref('')
const error = ref('')

function errorMessage(exc: unknown): string {
  return exc instanceof Error ? exc.message : String(exc)
}

async function submitRegister(): Promise<void> {
  busy.value = true
  message.value = ''
  error.value = ''

  try {
    await registerUser({
      email: form.email,
      password: form.password,
      is_admin: form.is_admin,
    })
    message.value = 'Registro exitoso. Ahora inicia sesion.'
    setTimeout(() => {
      void router.push('/login')
    }, 500)
  } catch (exc) {
    error.value = `Registro fallido: ${errorMessage(exc)}`
  } finally {
    busy.value = false
  }
}
</script>

<template>
  <section class="card auth-card">
    <h2>Crear cuenta</h2>
    <label>Email
      <input v-model="form.email" type="email" placeholder="admin@example.com" />
    </label>
    <label>Password
      <input v-model="form.password" type="password" placeholder="Password123!" />
    </label>
    <label class="inline">
      <input v-model="form.is_admin" type="checkbox" />
      Registrar como admin
    </label>

    <div class="actions">
      <button :disabled="busy" @click="submitRegister">Crear cuenta</button>
      <RouterLink class="link-btn" to="/login">Ir a login</RouterLink>
    </div>

    <p v-if="message" class="notice success">{{ message }}</p>
    <p v-if="error" class="notice error">{{ error }}</p>
  </section>
</template>

<style scoped>
.auth-card {
  max-width: 520px;
  margin: 0 auto;
}
</style>
