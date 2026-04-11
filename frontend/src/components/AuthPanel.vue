<script setup lang="ts">
import { computed } from 'vue'

import type { AuthForm } from '../types'

const props = defineProps<{
  modelValue: AuthForm
  busy: boolean
  isAuthenticated: boolean
  tokenType: string
}>()

const emit = defineEmits<{
  'update:modelValue': [value: AuthForm]
  register: []
  login: []
  logout: []
}>()

const form = computed<AuthForm>({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value),
})

function updateField<K extends keyof AuthForm>(key: K, value: AuthForm[K]): void {
  emit('update:modelValue', { ...form.value, [key]: value })
}
</script>

<template>
  <article class="card">
    <h2>Autenticacion</h2>
    <label>Email
      <input
        :value="form.email"
        type="email"
        placeholder="admin@example.com"
        @input="updateField('email', ($event.target as HTMLInputElement).value)"
      />
    </label>
    <label>Password
      <input
        :value="form.password"
        type="password"
        placeholder="Password123!"
        @input="updateField('password', ($event.target as HTMLInputElement).value)"
      />
    </label>
    <label class="inline">
      <input
        :checked="form.is_admin"
        type="checkbox"
        @change="updateField('is_admin', ($event.target as HTMLInputElement).checked)"
      />
      Registrar como admin
    </label>
    <div class="actions">
      <button :disabled="busy" @click="emit('register')">Register</button>
      <button :disabled="busy" @click="emit('login')">Login</button>
      <button :disabled="!isAuthenticated" class="ghost" @click="emit('logout')">Logout</button>
    </div>
    <small v-if="isAuthenticated">Sesion activa ({{ tokenType }})</small>
  </article>
</template>
