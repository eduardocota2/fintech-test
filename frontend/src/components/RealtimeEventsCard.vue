<script setup lang="ts">
import { computed } from 'vue'

import type { EventPayload } from '../types'

const props = defineProps<{
  events: EventPayload[]
  streamStatus: 'connecting' | 'connected' | 'reconnecting' | 'disconnected'
}>()

const enriched = computed(() => {
  return props.events.map((evt) => {
    const details = evt.details || {}
    return {
      ...evt,
      status: String(details.status || '-'),
      country: String(details.country || '-'),
      riskRating: String(details.risk_rating || '-'),
      userId: String(details.user_id || '-'),
      at: new Date(evt.created_at).toLocaleString(),
    }
  })
})
</script>

<template>
  <section class="card">
    <div class="heading">
      <h2>Eventos realtime (SSE)</h2>
      <span class="status" :class="`state-${streamStatus}`">{{ streamStatus }}</span>
    </div>
    <ul class="events">
      <li v-for="evt in enriched" :key="`${evt.created_at}-${evt.action}-${evt.application_id}`" class="event-item">
        <div class="event-top">
          <strong>{{ evt.action }}</strong>
          <time>{{ evt.at }}</time>
        </div>
        <div class="event-grid">
          <span>app: {{ evt.application_id.slice(0, 8) }}...</span>
          <span>status: {{ evt.status }}</span>
          <span>pais: {{ evt.country }}</span>
          <span>riesgo: {{ evt.riskRating }}</span>
        </div>
      </li>
      <li v-if="!events.length">Sin eventos aun. Crea o actualiza una solicitud para ver actividad.</li>
    </ul>
  </section>
</template>

<style scoped>
.heading {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
}

.status {
  border-radius: 999px;
  padding: 4px 10px;
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
}

.status.state-connected {
  background: #dcfce7;
  color: #166534;
}

.status.state-connecting,
.status.state-reconnecting {
  background: #fef3c7;
  color: #92400e;
}

.status.state-disconnected {
  background: #fee2e2;
  color: #991b1b;
}

.event-item {
  list-style: none;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 8px;
}

.event-top {
  display: flex;
  justify-content: space-between;
  gap: 8px;
}

.event-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 4px 8px;
  margin-top: 4px;
  font-size: 0.82rem;
  color: #475569;
}

.event-top time {
  color: #64748b;
  font-size: 0.78rem;
}
</style>
