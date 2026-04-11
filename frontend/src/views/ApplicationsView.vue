<script setup lang="ts">
import { onBeforeUnmount, ref } from 'vue'

import ApplicationDetailCard from '../components/ApplicationDetailCard.vue'
import ApplicationsListCard from '../components/ApplicationsListCard.vue'
import CreateApplicationCard from '../components/CreateApplicationCard.vue'
import RealtimeEventsCard from '../components/RealtimeEventsCard.vue'
import ToastNotification from '../components/ToastNotification.vue'
import type { ApplicationStatus, EventPayload, Filters, LoanCreateRequest, LoanDetail, LoanListItem } from '../models'
import { createApplication, getApplicationDetail, listApplications, updateApplicationStatus } from '../services/applications.service'
import { startEventsStream } from '../services/events.service'
import { authStore } from '../stores/auth'

type ToastItem = {
  id: string
  type: 'success' | 'error' | 'info'
  message: string
}

const createForm = ref<LoanCreateRequest>({
  country: 'MX',
  full_name: '',
  document_id: '',
  amount_requested: 15000,
  monthly_income: 32000,
  application_date: new Date().toISOString().slice(0, 10),
})

const filters = ref<Filters>({ country: '', status: '' })
const applications = ref<LoanListItem[]>([])
const selected = ref<LoanDetail | null>(null)
const events = ref<EventPayload[]>([])
const toasts = ref<ToastItem[]>([])

const busy = ref(false)
const loadingList = ref(false)
const message = ref('')
const error = ref('')
const sseStatus = ref<'connecting' | 'connected' | 'reconnecting' | 'disconnected'>('connecting')
const reconnectAttempts = ref(0)

let stopStream: (() => void) | null = null
let refreshTimer: number | null = null

function errorMessage(exc: unknown): string {
  return exc instanceof Error ? exc.message : String(exc)
}

function setMessage(text: string): void {
  message.value = text
  error.value = ''
  pushToast('success', text)
}

function setError(text: string): void {
  error.value = text
  message.value = ''
  pushToast('error', text)
}

function pushToast(type: ToastItem['type'], text: string): void {
  toasts.value.unshift({
    id: `${Date.now()}-${Math.random().toString(16).slice(2, 8)}`,
    type,
    message: text,
  })
  if (toasts.value.length > 6) {
    toasts.value.length = 6
  }
}

function dismissToast(id: string): void {
  toasts.value = toasts.value.filter((toast) => toast.id !== id)
}

function currentToken(): string {
  return authStore.state.token
}

async function loadApplications(): Promise<void> {
  loadingList.value = true
  try {
    const payload = await listApplications(currentToken(), filters.value)
    applications.value = payload.items || []
  } catch (exc) {
    setError(`No se pudo cargar el listado: ${errorMessage(exc)}`)
  } finally {
    loadingList.value = false
  }
}

async function loadDetail(id: string): Promise<void> {
  try {
    selected.value = await getApplicationDetail(currentToken(), id)
  } catch (exc) {
    setError(`No se pudo cargar el detalle: ${errorMessage(exc)}`)
  }
}

async function submitCreateApplication(debugDebtLevel?: 'low' | 'medium' | 'high'): Promise<void> {
  busy.value = true
  try {
    const payload = await createApplication(currentToken(), createForm.value, debugDebtLevel)
    setMessage(`Solicitud creada: ${payload.id}`)
    await loadApplications()
    await loadDetail(payload.id)
  } catch (exc) {
    setError(`No se pudo crear la solicitud: ${errorMessage(exc)}`)
  } finally {
    busy.value = false
  }
}

async function submitStatusUpdate(newStatus: ApplicationStatus): Promise<void> {
  if (!selected.value) {
    setError('No hay una solicitud seleccionada para actualizar.')
    return
  }

  busy.value = true
  try {
    const payload = await updateApplicationStatus(currentToken(), selected.value.id, newStatus)
    selected.value = payload
    setMessage(`Estado actualizado a ${payload.status}`)
    await loadApplications()
  } catch (exc) {
    setError(`No se pudo actualizar estado: ${errorMessage(exc)}`)
  } finally {
    busy.value = false
  }
}

function scheduleRefresh(): void {
  if (refreshTimer) return

  refreshTimer = window.setTimeout(async () => {
    refreshTimer = null
    await loadApplications()
    if (selected.value) {
      await loadDetail(selected.value.id)
    }
  }, 400)
}

function startRealtime(): void {
  stopRealtime()
  stopStream = startEventsStream(
    currentToken(),
    (payload) => {
      events.value.unshift(payload)
      if (events.value.length > 30) {
        events.value.length = 30
      }
      scheduleRefresh()
    },
    (status, attempt) => {
      sseStatus.value = status
      reconnectAttempts.value = attempt
    },
    (exc) => {
      setError(`Realtime inestable: ${errorMessage(exc)}`)
    },
  )
}

function stopRealtime(): void {
  if (stopStream) {
    stopStream()
    stopStream = null
  }
  sseStatus.value = 'disconnected'
}

void loadApplications().then(() => {
  startRealtime()
})

onBeforeUnmount(() => {
  stopRealtime()
  if (refreshTimer) {
    clearTimeout(refreshTimer)
    refreshTimer = null
  }
})
</script>

<template>
  <section class="workspace-header card">
    <div>
      <h2>Panel operativo</h2>
      <p>Gestiona solicitudes, detalle y eventos en un solo flujo de trabajo.</p>
    </div>
    <div class="status-row">
      <span class="status-pill" :class="`state-${sseStatus}`">SSE: {{ sseStatus }}</span>
      <span v-if="reconnectAttempts > 0" class="status-pill neutral">reintentos: {{ reconnectAttempts }}</span>
    </div>
  </section>

  <section class="workspace-grid">
    <div class="workspace-column">
      <CreateApplicationCard
        v-model="createForm"
        :busy="busy"
        :is-authenticated="true"
        @submit="submitCreateApplication"
      />

      <ApplicationsListCard
        :items="applications"
        :filters="filters"
        :loading="loadingList"
        @update:filters="filters = $event"
        @refresh="loadApplications"
        @select="loadDetail"
      />
    </div>

    <div class="workspace-column">
      <ApplicationDetailCard
        :selected="selected"
        :busy="busy"
        :is-authenticated="true"
        @submit="submitStatusUpdate"
      />

      <RealtimeEventsCard :events="events" :stream-status="sseStatus" />
    </div>
  </section>

  <section v-if="message" class="notice success">{{ message }}</section>
  <section v-if="error" class="notice error">{{ error }}</section>
  <ToastNotification :toasts="toasts" @close="dismissToast" />
</template>

<style scoped>
.workspace-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.workspace-header p {
  margin: 2px 0 0;
  color: #64748b;
}

.workspace-grid {
  display: grid;
  grid-template-columns: 1.2fr 1fr;
  gap: 16px;
}

.workspace-column {
  display: grid;
  gap: 16px;
  align-content: start;
}

.status-row {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.status-pill {
  border-radius: 999px;
  padding: 6px 10px;
  font-size: 0.78rem;
  font-weight: 700;
  text-transform: uppercase;
}

.status-pill.neutral {
  background: #f1f5f9;
  color: #334155;
}

.status-pill.state-connected {
  background: #dcfce7;
  color: #166534;
}

.status-pill.state-connecting,
.status-pill.state-reconnecting {
  background: #fef3c7;
  color: #92400e;
}

.status-pill.state-disconnected {
  background: #fee2e2;
  color: #991b1b;
}

@media (max-width: 980px) {
  .workspace-grid {
    grid-template-columns: 1fr;
  }

  .workspace-header {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
