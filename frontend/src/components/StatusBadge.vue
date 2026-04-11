<script setup lang="ts">
import { computed } from 'vue'

import type { ApplicationStatus } from '../models'

interface Props {
  status: ApplicationStatus
  size?: 'sm' | 'md' | 'lg'
  showScore?: boolean
  score?: number | null
}

const props = withDefaults(defineProps<Props>(), {
  size: 'md',
  showScore: false,
  score: null,
})

const displayText = computed(() => {
  const labels: Record<ApplicationStatus, string> = {
    submitted: 'Enviado',
    evaluating: 'En evaluacion',
    pending_review: 'Pendiente revision',
    approved: 'Aprobado',
    rejected: 'Rechazado',
  }
  return labels[props.status]
})

const isActive = computed(() => props.status === 'evaluating' || props.status === 'pending_review')
</script>

<template>
  <span class="status-badge" :class="[`status-${status}`, `size-${size}`]">
    <span class="status-dot" :class="{ pulse: isActive }" />
    <span class="status-text">{{ displayText }}</span>
    <span v-if="showScore && typeof score === 'number'" class="status-score">({{ Math.round(score) }})</span>
  </span>
</template>

<style scoped>
.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  border-radius: 999px;
  font-weight: 700;
  white-space: nowrap;
}

.size-sm {
  padding: 0.2rem 0.55rem;
  font-size: 0.75rem;
}

.size-md {
  padding: 0.35rem 0.85rem;
  font-size: 0.85rem;
}

.size-lg {
  padding: 0.45rem 1rem;
  font-size: 0.95rem;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.status-dot.pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.7; transform: scale(1.1); }
}

.status-submitted {
  background: #dbeafe;
  color: #1e40af;
}

.status-submitted .status-dot { background: #3b82f6; }

.status-evaluating {
  background: #fef3c7;
  color: #92400e;
}

.status-evaluating .status-dot { background: #f59e0b; }

.status-pending_review {
  background: #fce7f3;
  color: #9d174d;
}

.status-pending_review .status-dot { background: #ec4899; }

.status-approved {
  background: #dcfce7;
  color: #166534;
}

.status-approved .status-dot { background: #16a34a; }

.status-rejected {
  background: #fee2e2;
  color: #991b1b;
}

.status-rejected .status-dot { background: #ef4444; }

.status-score {
  margin-left: 0.1rem;
}
</style>
