<script setup lang="ts">
import { computed } from 'vue'

import type { RiskDecision } from '../models'
import ScoreGauge from './ScoreGauge.vue'

interface Props {
  decision?: RiskDecision
}

const props = defineProps<Props>()

const sortedFactors = computed(() => {
  if (!props.decision?.factors) return []
  return Object.entries(props.decision.factors)
    .sort((a, b) => b[1].weight - a[1].weight)
})

function getScoreClass(score: number): string {
  if (score >= 700) return 'good'
  if (score >= 500) return 'warning'
  return 'danger'
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleString('es-MX', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}
</script>

<template>
  <article class="risk-panel">
    <div class="panel-header">
      <h3 class="panel-title">Evaluacion de riesgo</h3>
      <span v-if="decision" class="evaluated-at">{{ formatDate(decision.created_at) }}</span>
    </div>

    <div v-if="!decision" class="no-evaluation">
      <p>No hay evaluacion de riesgo disponible para esta solicitud.</p>
      <small>La API actual aun no retorna latest_risk_decision en el detalle.</small>
    </div>

    <template v-else>
      <div class="panel-block">
        <ScoreGauge :score="decision.score" :decision="decision.decision" :factors="decision.factors" :show-factors="false" />
      </div>

      <div class="factors-section panel-block">
        <h4 class="section-title">Desglose de factores</h4>
        <div class="factors-table">
          <div v-for="[name, data] in sortedFactors" :key="name" class="factor-row">
            <div class="factor-info">
              <div class="factor-name">{{ data.description }}</div>
              <div class="factor-meta">
                <span class="weight-badge">{{ (data.weight * 100).toFixed(0) }}%</span>
                <span class="raw-score" :class="getScoreClass(data.raw_score)">{{ Math.round(data.raw_score) }}/1000</span>
              </div>
            </div>
            <div class="factor-contribution">
              <div class="contribution-bar">
                <div class="contribution-fill" :style="{ width: `${data.weighted_score / 10}%` }" :class="getScoreClass(data.raw_score)" />
              </div>
              <span class="contribution-value">+{{ data.weighted_score.toFixed(1) }}</span>
            </div>
          </div>
        </div>

        <div class="total-score">
          <span>Score total</span>
          <span class="total-value">{{ decision.score.toFixed(1) }} / 1000</span>
        </div>
      </div>

      <div class="decision-reason panel-block" :class="decision.decision">
        <h4 class="section-title">Decision del sistema</h4>
        <p class="reason-text">{{ decision.reason }}</p>
        <div class="evaluated-by">Evaluado por: {{ decision.evaluated_by === 'system' ? 'Sistema automatico' : decision.evaluated_by }}</div>
      </div>
    </template>
  </article>
</template>

<style scoped>
.risk-panel {
  background: #ffffff;
  border-radius: 1rem;
  border: 1px solid #e2e8f0;
  overflow: hidden;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.2rem;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border-bottom: 1px solid #e2e8f0;
}

.panel-title {
  margin: 0;
  font-size: 1.05rem;
  font-weight: 700;
  color: #1e293b;
}

.evaluated-at {
  font-size: 0.8rem;
  color: #64748b;
}

.panel-block {
  padding: 1.1rem 1.2rem;
  border-bottom: 1px solid #f1f5f9;
}

.panel-block:last-child {
  border-bottom: 0;
}

.no-evaluation {
  padding: 1.2rem;
  text-align: center;
  color: #64748b;
}

.no-evaluation p {
  margin: 0 0 0.25rem 0;
}

.factors-table {
  display: grid;
  gap: 0.75rem;
}

.section-title {
  margin: 0 0 0.8rem 0;
  font-size: 0.9rem;
  font-weight: 700;
  color: #334155;
}

.factor-row {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.factor-info {
  flex: 0 0 45%;
}

.factor-name {
  font-size: 0.88rem;
  color: #334155;
  margin-bottom: 0.2rem;
}

.factor-meta {
  display: flex;
  gap: 0.45rem;
  align-items: center;
}

.weight-badge {
  font-size: 0.72rem;
  padding: 0.1rem 0.45rem;
  background: #e2e8f0;
  color: #475569;
  border-radius: 999px;
}

.raw-score {
  font-size: 0.78rem;
  font-weight: 700;
}

.raw-score.good { color: #15803d; }
.raw-score.warning { color: #b45309; }
.raw-score.danger { color: #b91c1c; }

.factor-contribution {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 0.6rem;
}

.contribution-bar {
  flex: 1;
  height: 10px;
  background: #e2e8f0;
  border-radius: 5px;
  overflow: hidden;
}

.contribution-fill {
  height: 100%;
  border-radius: 5px;
}

.contribution-fill.good { background: linear-gradient(90deg, #16a34a, #4ade80); }
.contribution-fill.warning { background: linear-gradient(90deg, #d97706, #fbbf24); }
.contribution-fill.danger { background: linear-gradient(90deg, #dc2626, #f87171); }

.contribution-value {
  font-size: 0.85rem;
  font-weight: 700;
  color: #334155;
  min-width: 3.25rem;
  text-align: right;
}

.total-score {
  display: flex;
  justify-content: space-between;
  margin-top: 0.75rem;
  padding-top: 0.75rem;
  border-top: 1px solid #e2e8f0;
  font-weight: 700;
  color: #1e293b;
}

.decision-reason.approved_auto { background: #f0fdf4; }
.decision-reason.manual_review { background: #fffbeb; }
.decision-reason.rejected { background: #fef2f2; }

.reason-text {
  margin: 0 0 0.5rem 0;
  color: #334155;
  line-height: 1.45;
}

.evaluated-by {
  font-size: 0.82rem;
  color: #64748b;
}
</style>
