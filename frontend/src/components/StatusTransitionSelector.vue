<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'

import type { ApplicationStatus } from '../models'
import { getAvailableTransitions } from '../services/applications.service'
import { authStore } from '../stores/auth'
import StatusBadge from './StatusBadge.vue'

interface Props {
  currentStatus: ApplicationStatus
  applicationId: string
  score?: number | null
}

const props = withDefaults(defineProps<Props>(), {
  score: null,
})

const emit = defineEmits<{
  transition: [toStatus: ApplicationStatus]
}>()

const availableTransitions = ref<ApplicationStatus[]>([])
const loading = ref(false)
const error = ref<string | null>(null)
const selectedTransition = ref<ApplicationStatus | null>(null)

const isFinalState = computed(() => props.currentStatus === 'approved' || props.currentStatus === 'rejected')

async function loadTransitions(): Promise<void> {
  if (!props.applicationId) return

  loading.value = true
  error.value = null

  try {
    const token = authStore.state.token
    availableTransitions.value = await getAvailableTransitions(token, props.applicationId)
  } catch {
    error.value = 'No se pudieron cargar las transiciones disponibles'
    availableTransitions.value = []
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  void loadTransitions()
})

watch(
  () => [props.applicationId, props.currentStatus],
  () => {
    void loadTransitions()
  },
)

function selectTransition(transition: ApplicationStatus): void {
  selectedTransition.value = transition
}

function cancelTransition(): void {
  selectedTransition.value = null
}

function confirmTransition(): void {
  if (!selectedTransition.value) return
  emit('transition', selectedTransition.value)
  selectedTransition.value = null
}

function formatTransition(status: ApplicationStatus): string {
  const labels: Record<ApplicationStatus, string> = {
    submitted: 'Enviado',
    evaluating: 'En evaluacion',
    pending_review: 'Revision manual',
    approved: 'Aprobar',
    rejected: 'Rechazar',
  }
  return labels[status]
}

function getLabel(status: ApplicationStatus): string {
  const labels: Record<ApplicationStatus, string> = {
    submitted: 'SUB',
    evaluating: 'EVA',
    pending_review: 'REV',
    approved: 'OK',
    rejected: 'NO',
  }
  return labels[status]
}
</script>

<template>
  <section class="transition-selector">
    <div class="current-status-section">
      <span class="label">Estado actual</span>
      <StatusBadge :status="currentStatus" size="lg" :score="score" show-score />
    </div>

    <div v-if="loading" class="loading-state">
      <span class="spinner" />
      Cargando transiciones...
    </div>

    <div v-else-if="error" class="error-state">
      {{ error }}
    </div>

    <div v-else-if="availableTransitions.length > 0" class="transitions-section">
      <span class="label">Cambiar a:</span>
      <div class="transition-buttons">
        <button
          v-for="transition in availableTransitions"
          :key="transition"
          class="transition-btn"
          :class="`to-${transition}`"
          @click="selectTransition(transition)"
        >
          <span class="btn-icon">{{ getLabel(transition) }}</span>
          <span class="btn-text">{{ formatTransition(transition) }}</span>
          <span class="btn-arrow">></span>
        </button>
      </div>
    </div>

    <div v-else-if="isFinalState" class="final-state">
      <div class="final-icon">OK</div>
      <p class="final-text">Estado final</p>
      <p class="final-subtext">No hay transiciones disponibles.</p>
    </div>

    <div v-else class="no-transitions">
      <p>No hay transiciones disponibles desde este estado.</p>
    </div>

    <Transition name="fade">
      <div v-if="selectedTransition" class="confirmation-modal" role="dialog" aria-modal="true">
        <div class="modal-content">
          <h4>Confirmar cambio de estado</h4>
          <p>
            Estas por cambiar el estado a
            <strong>{{ formatTransition(selectedTransition) }}</strong>.
          </p>
          <div class="modal-actions">
            <button class="btn-secondary" @click="cancelTransition">Cancelar</button>
            <button class="btn-primary" :class="`to-${selectedTransition}`" @click="confirmTransition">Confirmar</button>
          </div>
        </div>
      </div>
    </Transition>
  </section>
</template>

<style scoped>
.transition-selector {
  background: #ffffff;
  border-radius: 0.75rem;
  padding: 1.1rem;
  border: 1px solid #e2e8f0;
}

.current-status-section {
  margin-bottom: 1rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e2e8f0;
}

.label {
  display: block;
  font-size: 0.84rem;
  font-weight: 600;
  color: #64748b;
  margin-bottom: 0.45rem;
}

.loading-state {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #64748b;
  padding: 0.8rem;
}

.spinner {
  width: 14px;
  height: 14px;
  border: 2px solid #e2e8f0;
  border-top-color: #0f766e;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-state {
  border-radius: 0.5rem;
  border: 1px solid #fecaca;
  background: #fef2f2;
  color: #991b1b;
  padding: 0.7rem 0.85rem;
  font-size: 0.86rem;
}

.transition-buttons {
  display: grid;
  gap: 0.45rem;
}

.transition-btn {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  padding: 0.65rem 0.85rem;
  border: 2px solid #e2e8f0;
  border-radius: 0.6rem;
  background: #ffffff;
  cursor: pointer;
  text-align: left;
  transition: all 0.2s;
}

.transition-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(15, 23, 42, 0.08);
}

.btn-icon {
  min-width: 34px;
  min-height: 24px;
  border-radius: 0.45rem;
  font-size: 0.68rem;
  display: grid;
  place-items: center;
  font-weight: 800;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
}

.btn-text {
  flex: 1;
  font-weight: 700;
  color: #334155;
}

.btn-arrow {
  color: #94a3b8;
  font-weight: 700;
}

.transition-btn.to-approved {
  border-color: #16a34a;
}

.transition-btn.to-rejected {
  border-color: #dc2626;
}

.transition-btn.to-pending_review {
  border-color: #db2777;
}

.transition-btn.to-evaluating {
  border-color: #d97706;
}

.final-state,
.no-transitions {
  text-align: center;
  padding: 1rem;
  color: #64748b;
}

.final-icon {
  width: 52px;
  height: 52px;
  margin: 0 auto 0.7rem;
  background: #dcfce7;
  color: #166534;
  border-radius: 50%;
  display: grid;
  place-items: center;
  font-weight: 800;
}

.final-text {
  font-size: 1rem;
  font-weight: 700;
  color: #334155;
  margin: 0;
}

.final-subtext {
  font-size: 0.82rem;
  margin: 0.2rem 0 0;
}

.confirmation-modal {
  position: fixed;
  inset: 0;
  background: rgba(2, 6, 23, 0.55);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 120;
  padding: 1rem;
}

.modal-content {
  background: #ffffff;
  border-radius: 0.95rem;
  padding: 1.2rem;
  max-width: 420px;
  width: 100%;
}

.modal-content h4 {
  margin: 0 0 0.65rem 0;
  font-size: 1.05rem;
}

.modal-content p {
  margin: 0 0 1rem 0;
  color: #475569;
}

.modal-actions {
  display: flex;
  gap: 0.6rem;
  justify-content: flex-end;
}

.btn-secondary,
.btn-primary {
  border-radius: 0.45rem;
  padding: 0.48rem 0.9rem;
  font-weight: 700;
}

.btn-secondary {
  border: 1px solid #cbd5e1;
  background: #ffffff;
  color: #475569;
}

.btn-primary {
  border: none;
  color: #ffffff;
  background: #0f766e;
}

.btn-primary.to-approved {
  background: #15803d;
}

.btn-primary.to-rejected {
  background: #b91c1c;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
