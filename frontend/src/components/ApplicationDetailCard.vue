<script setup lang="ts">
import { computed } from 'vue'

import type { ApplicationStatus, LoanDetail } from '../models'
import RiskEvaluationPanel from './RiskEvaluationPanel.vue'
import StatusBadge from './StatusBadge.vue'
import StatusTimeline from './StatusTimeline.vue'
import StatusTransitionSelector from './StatusTransitionSelector.vue'

const props = defineProps<{
  selected: LoanDetail | null
  busy: boolean
  isAuthenticated: boolean
}>()

const emit = defineEmits<{
  submit: [status: ApplicationStatus]
}>()

const latestScore = computed(() => props.selected?.latest_risk_decision?.score ?? null)

function formatCurrency(amount: number, country: 'MX' | 'CO'): string {
  const currency = country === 'MX' ? 'MXN' : 'COP'
  const locale = country === 'MX' ? 'es-MX' : 'es-CO'
  return new Intl.NumberFormat(locale, {
    style: 'currency',
    currency,
    maximumFractionDigits: 0,
  }).format(amount)
}

function handleTransition(newStatus: ApplicationStatus): void {
  emit('submit', newStatus)
}
</script>

<template>
  <article class="card detail-card">
    <div class="detail-header">
      <h2>Detalle de solicitud</h2>
      <StatusBadge
        v-if="selected"
        :status="selected.status"
        :score="latestScore"
        :show-score="true"
        size="lg"
      />
    </div>

    <div v-if="selected" class="detail-content">
      <section class="info-section">
        <div class="info-grid">
          <div class="info-item">
            <span class="label">ID</span>
            <span class="value mono">{{ selected.id }}</span>
          </div>
          <div class="info-item">
            <span class="label">Cliente</span>
            <span class="value">{{ selected.full_name }}</span>
          </div>
          <div class="info-item">
            <span class="label">Pais</span>
            <span class="value">{{ selected.country }}</span>
          </div>
          <div class="info-item">
            <span class="label">Documento</span>
            <span class="value mono">{{ selected.document_id_masked }}</span>
          </div>
          <div class="info-item">
            <span class="label">Monto</span>
            <span class="value">{{ formatCurrency(selected.amount_requested, selected.country) }}</span>
          </div>
          <div class="info-item">
            <span class="label">Ingreso mensual</span>
            <span class="value">{{ formatCurrency(selected.monthly_income, selected.country) }}</span>
          </div>
          <div class="info-item">
            <span class="label">Banco</span>
            <span class="value">{{ selected.bank_name || '-' }} ({{ selected.bank_account_last4 || '----' }})</span>
          </div>
          <div class="info-item">
            <span class="label">Risk rating</span>
            <span class="value">{{ selected.risk_rating || '-' }}</span>
          </div>
        </div>
      </section>

      <StatusTimeline :current-status="selected.status" :country="selected.country" />

      <RiskEvaluationPanel :decision="selected.latest_risk_decision" />

      <section class="actions-section">
        <h4>Acciones</h4>
        <StatusTransitionSelector
          :current-status="selected.status"
          :application-id="selected.id"
          :score="latestScore"
          :class="{ disabled: busy || !isAuthenticated }"
          @transition="handleTransition"
        />
      </section>
    </div>

    <p v-else>Selecciona una solicitud del listado.</p>
  </article>
</template>

<style scoped>
.detail-card {
  gap: 12px;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
}

.detail-content {
  display: grid;
  gap: 12px;
}

.info-section {
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 12px;
  background: #fcfcfd;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px 12px;
}

.info-item {
  display: grid;
  gap: 2px;
}

.label {
  font-size: 0.75rem;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  font-weight: 700;
}

.value {
  color: #1e293b;
  font-size: 0.9rem;
}

.mono {
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  word-break: break-all;
}

.actions-section {
  display: grid;
  gap: 8px;
}

.actions-section h4 {
  margin: 0;
}

.actions-section :deep(.transition-selector.disabled) {
  pointer-events: none;
  opacity: 0.6;
}

@media (max-width: 760px) {
  .info-grid {
    grid-template-columns: 1fr;
  }
}
</style>
