<script setup lang="ts">
import { computed } from 'vue'

import type { Filters, LoanListItem } from '../models'
import StatusBadge from './StatusBadge.vue'

const props = defineProps<{
  items: LoanListItem[]
  filters: Filters
  loading: boolean
}>()

const emit = defineEmits<{
  'update:filters': [value: Filters]
  refresh: []
  select: [id: string]
}>()

const currentFilters = computed<Filters>({
  get: () => props.filters,
  set: (value) => emit('update:filters', value),
})

function updateCountry(value: Filters['country']): void {
  emit('update:filters', { ...currentFilters.value, country: value })
  emit('refresh')
}

function updateStatus(value: Filters['status']): void {
  emit('update:filters', { ...currentFilters.value, status: value })
  emit('refresh')
}
</script>

<template>
  <article class="card">
    <h2>Solicitudes</h2>
    <div class="grid two compact">
      <label>Filtro pais
        <select
          :value="currentFilters.country"
          @change="updateCountry(($event.target as HTMLSelectElement).value as Filters['country'])"
        >
          <option value="">Todos</option>
          <option value="MX">MX</option>
          <option value="CO">CO</option>
        </select>
      </label>
      <label>Filtro estado
        <select
          :value="currentFilters.status"
          @change="updateStatus(($event.target as HTMLSelectElement).value as Filters['status'])"
        >
          <option value="">Todos</option>
          <option value="submitted">submitted</option>
          <option value="evaluating">evaluating</option>
          <option value="pending_review">pending_review</option>
          <option value="approved">approved</option>
          <option value="rejected">rejected</option>
        </select>
      </label>
    </div>

    <table class="applications-table">
      <thead>
        <tr>
          <th>ID</th>
          <th>Pais</th>
          <th>Estado</th>
          <th>Monto</th>
          <th>Banco</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in items" :key="item.id">
          <td class="mono">{{ item.id.slice(0, 8) }}...</td>
          <td>{{ item.country }}</td>
          <td>
            <StatusBadge :status="item.status" size="sm" />
          </td>
          <td>{{ item.amount_requested.toLocaleString() }}</td>
          <td>{{ item.bank_name || '-' }}</td>
          <td><button class="ghost" @click="emit('select', item.id)">Detalle</button></td>
        </tr>
        <tr v-if="!items.length">
          <td colspan="6">{{ loading ? 'Cargando...' : 'Sin resultados' }}</td>
        </tr>
      </tbody>
    </table>
  </article>
</template>

<style scoped>
.applications-table .mono {
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
}

.applications-table th,
.applications-table td {
  vertical-align: middle;
}
</style>
