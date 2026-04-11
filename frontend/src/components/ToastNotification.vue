<script setup lang="ts">
import { onBeforeUnmount } from 'vue'

export interface ToastItem {
  id: string
  type: 'success' | 'error' | 'info'
  message: string
}

const props = defineProps<{
  toasts: ToastItem[]
  autoHideMs?: number
}>()

const emit = defineEmits<{
  close: [id: string]
}>()

const timers = new Map<string, number>()

function setupTimer(id: string): void {
  if (timers.has(id)) return

  const timeout = window.setTimeout(() => {
    emit('close', id)
    timers.delete(id)
  }, props.autoHideMs || 4500)

  timers.set(id, timeout)
}

function clearTimer(id: string): void {
  const timer = timers.get(id)
  if (timer) {
    clearTimeout(timer)
    timers.delete(id)
  }
}

onBeforeUnmount(() => {
  timers.forEach((timer) => clearTimeout(timer))
  timers.clear()
})
</script>

<template>
  <section class="toast-stack" aria-live="polite" aria-atomic="true">
    <TransitionGroup name="toast" tag="div" class="toast-group">
      <article
        v-for="toast in toasts"
        :key="toast.id"
        class="toast"
        :class="`type-${toast.type}`"
        @mouseenter="clearTimer(toast.id)"
        @mouseleave="setupTimer(toast.id)"
      >
        <div class="toast-body">
          <strong class="toast-title">{{ toast.type.toUpperCase() }}</strong>
          <p>{{ toast.message }}</p>
        </div>
        <button class="toast-close" type="button" @click="emit('close', toast.id)">X</button>
        {{ setupTimer(toast.id) && '' }}
      </article>
    </TransitionGroup>
  </section>
</template>

<style scoped>
.toast-stack {
  position: fixed;
  right: 16px;
  bottom: 16px;
  z-index: 150;
}

.toast-group {
  display: grid;
  gap: 10px;
}

.toast {
  min-width: 260px;
  max-width: 360px;
  border-radius: 0.75rem;
  border: 1px solid #e2e8f0;
  background: #ffffff;
  box-shadow: 0 16px 28px rgba(15, 23, 42, 0.18);
  display: flex;
  justify-content: space-between;
  gap: 12px;
  padding: 10px 12px;
}

.toast.type-success {
  border-color: #86efac;
  background: #f0fdf4;
}

.toast.type-error {
  border-color: #fca5a5;
  background: #fef2f2;
}

.toast.type-info {
  border-color: #93c5fd;
  background: #eff6ff;
}

.toast-title {
  display: block;
  font-size: 0.78rem;
  letter-spacing: 0.04em;
  margin-bottom: 2px;
}

.toast p {
  margin: 0;
  color: #334155;
  font-size: 0.86rem;
}

.toast-close {
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  background: #ffffff;
  color: #64748b;
  min-width: 28px;
  height: 28px;
  font-weight: 700;
  cursor: pointer;
}

.toast-enter-active,
.toast-leave-active {
  transition: all 0.25s ease;
}

.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateY(8px);
}

.toast-move {
  transition: transform 0.25s ease;
}
</style>
