<script setup lang="ts">
import { computed } from 'vue'

import type { LoanCreateRequest } from '../types'

const props = defineProps<{
  modelValue: LoanCreateRequest
  busy: boolean
  isAuthenticated: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: LoanCreateRequest]
  submit: []
}>()

const form = computed<LoanCreateRequest>({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value),
})

function updateField<K extends keyof LoanCreateRequest>(key: K, value: LoanCreateRequest[K]): void {
  emit('update:modelValue', { ...form.value, [key]: value })
}
</script>

<template>
  <article class="card">
    <h2>Crear solicitud</h2>
    <label>Pais
      <select
        :value="form.country"
        @change="updateField('country', ($event.target as HTMLSelectElement).value as LoanCreateRequest['country'])"
      >
        <option value="MX">MX</option>
        <option value="CO">CO</option>
      </select>
    </label>
    <label>Nombre completo
      <input
        :value="form.full_name"
        type="text"
        placeholder="Nombre Apellido"
        @input="updateField('full_name', ($event.target as HTMLInputElement).value)"
      />
    </label>
    <label>Documento
      <input
        :value="form.document_id"
        type="text"
        placeholder="ABC123456"
        @input="updateField('document_id', ($event.target as HTMLInputElement).value)"
      />
    </label>
    <div class="grid two compact">
      <label>Monto solicitado
        <input
          :value="form.amount_requested"
          type="number"
          min="1"
          @input="updateField('amount_requested', Number(($event.target as HTMLInputElement).value))"
        />
      </label>
      <label>Ingreso mensual
        <input
          :value="form.monthly_income"
          type="number"
          min="1"
          @input="updateField('monthly_income', Number(($event.target as HTMLInputElement).value))"
        />
      </label>
    </div>
    <label>Fecha de solicitud
      <input
        :value="form.application_date"
        type="date"
        @input="updateField('application_date', ($event.target as HTMLInputElement).value)"
      />
    </label>
    <button :disabled="busy || !isAuthenticated" @click="emit('submit')">Crear solicitud</button>
  </article>
</template>
