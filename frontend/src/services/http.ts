const apiPrefix = '/api/v1'

export function authHeader(token: string): Record<string, string> {
  if (!token) return {}
  return { Authorization: `Bearer ${token}` }
}

function normalizeMessage(status: number, payload: Record<string, unknown>): string {
  const detail = payload.detail || payload.raw
  return String(detail || `HTTP ${status}`)
}

export async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${apiPrefix}${path}`, options)

  const raw = await response.text()
  let payload: Record<string, unknown> = {}

  if (raw) {
    try {
      payload = JSON.parse(raw) as Record<string, unknown>
    } catch {
      payload = { raw }
    }
  }

  if (!response.ok) {
    throw new Error(normalizeMessage(response.status, payload))
  }

  return payload as T
}
