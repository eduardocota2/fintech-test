<script setup lang="ts">
import { computed } from 'vue'

import type { ApplicationStatus, CountryCode } from '../models'

interface Props {
  currentStatus: ApplicationStatus
  country: CountryCode
}

const props = defineProps<Props>()

const stateFlow = computed((): ApplicationStatus[] => {
  const flows: Record<CountryCode, ApplicationStatus[]> = {
    MX: ['submitted', 'evaluating', 'pending_review', 'approved'],
    CO: ['submitted', 'evaluating', 'pending_review', 'approved'],
  }

  if (props.currentStatus === 'rejected') {
    return ['submitted', 'evaluating', 'rejected']
  }

  return flows[props.country]
})

const currentIndex = computed(() => stateFlow.value.indexOf(props.currentStatus))

function isCompleted(state: ApplicationStatus): boolean {
  return stateFlow.value.indexOf(state) < currentIndex.value
}

function formatState(state: ApplicationStatus): string {
  const labels: Record<ApplicationStatus, string> = {
    submitted: 'Solicitud enviada',
    evaluating: 'En evaluacion',
    pending_review: 'Revision manual',
    approved: 'Aprobado',
    rejected: 'Rechazado',
  }
  return labels[state]
}
</script>

<template>
  <section class="timeline-container">
    <h4 class="timeline-title">Flujo de estados</h4>
    <div class="timeline">
      <div
        v-for="(state, index) in stateFlow"
        :key="state"
        class="timeline-item"
        :class="{
          completed: isCompleted(state),
          current: state === currentStatus,
          pending: stateFlow.indexOf(state) > currentIndex,
        }"
      >
        <div class="timeline-marker">
          <span v-if="isCompleted(state)" class="marker-check">OK</span>
          <span v-else-if="state === currentStatus" class="current-dot" />
          <span v-else class="pending-number">{{ index + 1 }}</span>
        </div>

        <div class="timeline-content">
          <div class="timeline-state">{{ formatState(state) }}</div>
          <div v-if="state === currentStatus" class="timeline-current">Estado actual</div>
          <div v-else-if="isCompleted(state)" class="timeline-completed">Completado</div>
        </div>

        <div v-if="index < stateFlow.length - 1" class="timeline-connector">
          <div class="connector-line" :class="{ active: isCompleted(state) }" />
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.timeline-container {
  background: #ffffff;
  border-radius: 0.75rem;
  padding: 1.15rem;
  border: 1px solid #e2e8f0;
}

.timeline-title {
  margin: 0 0 1rem 0;
  font-size: 0.95rem;
  font-weight: 700;
  color: #1e293b;
}

.timeline-item {
  display: flex;
  align-items: flex-start;
  gap: 0.8rem;
  position: relative;
  padding-bottom: 1.2rem;
}

.timeline-item:last-child {
  padding-bottom: 0;
}

.timeline-marker {
  width: 1.8rem;
  height: 1.8rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  z-index: 1;
}

.marker-check {
  color: #ffffff;
  font-size: 0.65rem;
  font-weight: 700;
}

.current-dot {
  width: 11px;
  height: 11px;
  border-radius: 50%;
  background: #ffffff;
  animation: pulse-ring 2s cubic-bezier(0.215, 0.61, 0.355, 1) infinite;
}

@keyframes pulse-ring {
  0% { transform: scale(0.8); opacity: 1; }
  100% { transform: scale(1.35); opacity: 0; }
}

.pending-number {
  font-size: 0.8rem;
  font-weight: 700;
}

.timeline-content {
  flex: 1;
  padding-top: 0.2rem;
}

.timeline-state {
  font-weight: 600;
  color: #334155;
  font-size: 0.9rem;
}

.timeline-current {
  font-size: 0.75rem;
  color: #0369a1;
  margin-top: 0.2rem;
}

.timeline-completed {
  font-size: 0.75rem;
  color: #15803d;
  margin-top: 0.2rem;
}

.timeline-connector {
  position: absolute;
  left: 0.9rem;
  top: 1.8rem;
  bottom: 0;
  width: 2px;
  transform: translateX(-50%);
}

.connector-line {
  width: 100%;
  height: 100%;
  background: #e2e8f0;
}

.connector-line.active {
  background: #22c55e;
}

.timeline-item.completed .timeline-marker {
  background: #16a34a;
}

.timeline-item.current .timeline-marker {
  background: #0284c7;
  box-shadow: 0 0 0 4px rgba(2, 132, 199, 0.18);
}

.timeline-item.pending .timeline-marker {
  background: #f1f5f9;
  color: #94a3b8;
  border: 2px solid #e2e8f0;
}

.timeline-item.pending .timeline-state {
  color: #94a3b8;
}
</style>
