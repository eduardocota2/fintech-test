<script setup lang="ts">
import { computed } from 'vue'

import type { ScoringFactor } from '../models'

interface Props {
  score: number
  decision?: 'approved_auto' | 'manual_review' | 'rejected'
  factors?: Record<string, ScoringFactor>
  showFactors?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  decision: undefined,
  factors: undefined,
  showFactors: true,
})

const safeScore = computed(() => Math.max(0, Math.min(1000, Number(props.score) || 0)))

const scoreClass = computed(() => {
  if (safeScore.value >= 750) return 'excellent'
  if (safeScore.value >= 550) return 'moderate'
  return 'poor'
})

const label = computed(() => {
  if (props.decision === 'approved_auto') return 'Aprobacion automatica'
  if (props.decision === 'manual_review') return 'Revision manual requerida'
  if (props.decision === 'rejected') return 'Solicitud rechazada'
  return 'Evaluacion pendiente'
})

const gaugeOffset = computed(() => {
  const maxOffset = 126.92
  return maxOffset - (safeScore.value / 1000) * maxOffset
})

const topFactors = computed(() => {
  if (!props.factors) return []
  return Object.entries(props.factors)
    .sort((a, b) => b[1].weight - a[1].weight)
    .slice(0, 3)
})

function formatName(name: string): string {
  const names: Record<string, string> = {
    debt_to_income: 'Deuda/Ingreso',
    amount_to_income: 'Monto/Ingreso',
    credit_score: 'Score crediticio',
    income_stability: 'Estabilidad',
    document_validity: 'Documento',
  }
  return names[name] || name.replace(/_/g, ' ')
}

function getFactorClass(score: number): string {
  if (score >= 700) return 'good'
  if (score >= 500) return 'warning'
  return 'danger'
}
</script>

<template>
  <section class="score-container">
    <div class="score-gauge" :class="scoreClass">
      <svg viewBox="0 0 100 50" class="gauge-svg" role="img" aria-label="Score gauge">
        <defs>
          <linearGradient id="gaugeGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" style="stop-color:#ef4444" />
            <stop offset="50%" style="stop-color:#f59e0b" />
            <stop offset="100%" style="stop-color:#10b981" />
          </linearGradient>
        </defs>
        <path class="gauge-bg" d="M 10 50 A 40 40 0 0 1 90 50" />
        <path class="gauge-fill" :style="{ strokeDashoffset: gaugeOffset }" d="M 10 50 A 40 40 0 0 1 90 50" />
      </svg>
      <div class="score-value">{{ Math.round(safeScore) }}</div>
      <div class="score-max">/ 1000</div>
    </div>

    <div class="score-label" :class="scoreClass">{{ label }}</div>

    <div v-if="factors && showFactors" class="factors-mini">
      <div v-for="[name, data] in topFactors" :key="name" class="factor-item">
        <div class="factor-header">
          <span class="factor-name">{{ formatName(name) }}</span>
          <span class="factor-score" :class="getFactorClass(data.raw_score)">{{ Math.round(data.raw_score) }}</span>
        </div>
        <div class="factor-bar">
          <div class="factor-fill" :style="{ width: `${data.raw_score / 10}%` }" :class="getFactorClass(data.raw_score)" />
        </div>
        <div class="factor-weight">Peso: {{ (data.weight * 100).toFixed(0) }}%</div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.score-container {
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border-radius: 1rem;
  padding: 1.2rem;
  border: 1px solid #e2e8f0;
}

.score-gauge {
  position: relative;
  width: 200px;
  margin: 0 auto;
}

.gauge-svg {
  width: 100%;
  height: 100px;
}

.gauge-bg {
  fill: none;
  stroke: #e2e8f0;
  stroke-width: 10;
  stroke-linecap: round;
}

.gauge-fill {
  fill: none;
  stroke: url(#gaugeGradient);
  stroke-width: 10;
  stroke-linecap: round;
  stroke-dasharray: 126.92;
  transition: stroke-dashoffset 0.9s cubic-bezier(0.4, 0, 0.2, 1);
}

.score-value {
  position: absolute;
  top: 52%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 2.6rem;
  font-weight: 800;
  color: #1e293b;
  line-height: 1;
}

.score-max {
  position: absolute;
  top: 70%;
  left: 62%;
  font-size: 0.83rem;
  color: #94a3b8;
  font-weight: 600;
}

.score-label {
  text-align: center;
  margin-top: 0.75rem;
  padding: 0.45rem 0.9rem;
  border-radius: 999px;
  font-weight: 700;
  font-size: 0.78rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.score-label.excellent {
  background: #dcfce7;
  color: #166534;
}

.score-label.moderate {
  background: #fef3c7;
  color: #92400e;
}

.score-label.poor {
  background: #fee2e2;
  color: #991b1b;
}

.factors-mini {
  margin-top: 1.2rem;
  padding-top: 1.2rem;
  border-top: 1px solid #e2e8f0;
}

.factor-item {
  margin-bottom: 0.8rem;
}

.factor-item:last-child {
  margin-bottom: 0;
}

.factor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.35rem;
}

.factor-name {
  font-size: 0.86rem;
  color: #475569;
  font-weight: 500;
}

.factor-score {
  font-size: 0.78rem;
  font-weight: 700;
  padding: 0.1rem 0.45rem;
  border-radius: 999px;
}

.factor-score.good {
  background: #dcfce7;
  color: #166534;
}

.factor-score.warning {
  background: #fef3c7;
  color: #92400e;
}

.factor-score.danger {
  background: #fee2e2;
  color: #991b1b;
}

.factor-bar {
  height: 8px;
  background: #e2e8f0;
  border-radius: 4px;
  overflow: hidden;
}

.factor-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.8s ease;
}

.factor-fill.good {
  background: linear-gradient(90deg, #16a34a, #4ade80);
}

.factor-fill.warning {
  background: linear-gradient(90deg, #d97706, #fbbf24);
}

.factor-fill.danger {
  background: linear-gradient(90deg, #dc2626, #f87171);
}

.factor-weight {
  font-size: 0.72rem;
  color: #94a3b8;
  margin-top: 0.25rem;
  text-align: right;
}
</style>
