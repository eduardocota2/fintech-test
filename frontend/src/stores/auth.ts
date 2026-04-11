import { computed, reactive } from 'vue'

import type { SessionState } from '../models'

const TOKEN_KEY = 'bravo_token'
const TOKEN_TYPE_KEY = 'bravo_token_type'

const state = reactive<SessionState>({
  token: '',
  tokenType: 'bearer',
  isAdmin: false,
})

function decodeJwtPayload(token: string): Record<string, unknown> {
  const parts = token.split('.')
  if (parts.length < 2) return {}

  const normalized = parts[1].replace(/-/g, '+').replace(/_/g, '/')
  const base64 = normalized.padEnd(Math.ceil(normalized.length / 4) * 4, '=')

  try {
    return JSON.parse(window.atob(base64)) as Record<string, unknown>
  } catch {
    return {}
  }
}

function applyToken(token: string, tokenType = 'bearer'): void {
  state.token = token
  state.tokenType = tokenType

  const payload = decodeJwtPayload(token)
  state.isAdmin = Boolean(payload.is_admin)

  if (token) {
    localStorage.setItem(TOKEN_KEY, token)
    localStorage.setItem(TOKEN_TYPE_KEY, tokenType)
  }
}

function initialize(): void {
  const token = localStorage.getItem(TOKEN_KEY) || ''
  const tokenType = localStorage.getItem(TOKEN_TYPE_KEY) || 'bearer'

  if (token) {
    applyToken(token, tokenType)
  }
}

function clearSession(): void {
  state.token = ''
  state.tokenType = 'bearer'
  state.isAdmin = false
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem(TOKEN_TYPE_KEY)
}

initialize()

export const authStore = {
  state,
  isAuthenticated: computed(() => Boolean(state.token)),
  setSession(token: string, tokenType = 'bearer') {
    applyToken(token, tokenType)
  },
  logout() {
    clearSession()
  },
}
