<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'

import { authStore } from './stores/auth'

const router = useRouter()

const isAuthenticated = computed(() => authStore.isAuthenticated.value)
const isAdmin = computed(() => authStore.state.isAdmin)

function logout(): void {
  authStore.logout()
  void router.replace('/login')
}
</script>

<template>
  <main class="shell">
    <header class="hero">
      <div>
        <h1>Fintech Credit Console</h1>
        <p>MVP frontend para solicitudes de crédito multi-país.</p>
      </div>

      <nav class="actions">
        <span v-if="isAuthenticated" class="badge">{{ isAdmin ? 'Admin' : 'No admin' }}</span>
        <button v-if="isAuthenticated" class="logout-btn" @click="logout">Cerrar sesión</button>
        <a href="/docs" target="_blank" rel="noreferrer">API Docs</a>
      </nav>
    </header>

    <RouterView />
  </main>
</template>

<style>
* {
  box-sizing: border-box;
}

body {
  margin: 0;
  font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
  color: #0f172a;
  background:
    radial-gradient(circle at top right, #fef3c7, transparent 40%),
    radial-gradient(circle at top left, #dbeafe, transparent 45%),
    #f8fafc;
}

.shell {
  max-width: 1160px;
  margin: 0 auto;
  padding: 24px;
  display: grid;
  gap: 16px;
}

.hero {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: 18px;
  padding: 20px;
  box-shadow: 0 12px 30px rgba(15, 23, 42, 0.08);
}

.hero h1 {
  margin: 0;
  font-size: 1.7rem;
}

.hero p {
  margin: 4px 0 0;
  color: #475569;
}

.hero a {
  text-decoration: none;
  border: 1px solid #334155;
  color: #334155;
  border-radius: 999px;
  padding: 8px 12px;
  font-weight: 700;
  background: #ffffff;
}

.link-btn {
  text-decoration: none;
  border: 1px solid #334155;
  color: #334155;
  border-radius: 999px;
  padding: 8px 12px;
  font-weight: 700;
  background: #ffffff;
}

.badge {
  border: 1px solid #0f766e;
  color: #0f766e;
  border-radius: 999px;
  padding: 8px 12px;
  font-weight: 700;
  font-size: 0.9rem;
  background: #ecfeff;
}

.logout-btn {
  border: 1px solid #b91c1c;
  border-radius: 999px;
  padding: 8px 12px;
  font-weight: 700;
  color: #b91c1c;
  background: #ffffff;
}

.grid {
  display: grid;
  gap: 16px;
}

.grid.two {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.grid.two.compact {
  gap: 10px;
}

.card {
  background: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: 14px;
  padding: 16px;
  display: grid;
  gap: 10px;
}

h2 {
  margin: 0 0 4px;
  font-size: 1.1rem;
}

label {
  display: grid;
  gap: 6px;
  font-size: 0.9rem;
  color: #334155;
}

label.inline {
  display: flex;
  align-items: center;
  gap: 8px;
}

input,
select,
button {
  font: inherit;
}

input,
select {
  padding: 8px 10px;
  border-radius: 10px;
  border: 1px solid #94a3b8;
  background: #ffffff;
}

.actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

button {
  border: none;
  border-radius: 10px;
  padding: 9px 12px;
  font-weight: 700;
  cursor: pointer;
  background: #0f766e;
  color: #ffffff;
}

button.ghost {
  background: #ffffff;
  color: #0f172a;
  border: 1px solid #94a3b8;
}

button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
}

th,
td {
  border-bottom: 1px solid #e2e8f0;
  padding: 8px;
  text-align: left;
}

.detail p {
  margin: 0;
  font-size: 0.92rem;
}

.events {
  margin: 0;
  padding-left: 20px;
  display: grid;
  gap: 4px;
}

.events li {
  font-size: 0.9rem;
}

.events span {
  margin-left: 6px;
  color: #334155;
}

.events time {
  margin-left: 6px;
  color: #64748b;
}

.notice {
  border-radius: 10px;
  padding: 10px 12px;
  font-weight: 600;
}

.notice.success {
  background: #dcfce7;
  border: 1px solid #22c55e;
}

.notice.error {
  background: #fee2e2;
  border: 1px solid #ef4444;
}

@media (max-width: 900px) {
  .grid.two {
    grid-template-columns: 1fr;
  }

  .hero {
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>
