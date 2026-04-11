import type { EventPayload } from '../models'
import { authHeader } from './http'

export type StreamStatus = 'connecting' | 'connected' | 'reconnecting' | 'disconnected'

function parseEventChunk(chunk: string, bufferState: string, onEvent: (payload: EventPayload) => void): string {
  const merged = `${bufferState}${chunk}`
  const parts = merged.split('\n\n')
  const pending = parts.pop() || ''

  for (const part of parts) {
    const dataLine = part
      .split('\n')
      .find((line) => line.startsWith('data: '))

    if (!dataLine) continue

    const jsonRaw = dataLine.slice(6)
    try {
      onEvent(JSON.parse(jsonRaw) as EventPayload)
    } catch {
      // Ignore malformed event payloads.
    }
  }

  return pending
}

export function startEventsStream(
  token: string,
  onEvent: (payload: EventPayload) => void,
  onStatus: (status: StreamStatus, attempt: number) => void,
  onError: (error: unknown) => void,
): () => void {
  let active = true
  let attempt = 0
  let reconnectTimer: number | null = null
  let currentController: AbortController | null = null

  const isAbortError = (error: unknown): boolean => {
    return error instanceof DOMException && error.name === 'AbortError'
  }

  const scheduleReconnect = (reason: unknown): void => {
    if (!active) return

    attempt += 1
    onStatus('reconnecting', attempt)

    if (attempt % 5 === 0) {
      onError(new Error('Realtime inestable. Reintentando conexion SSE...'))
    }

    const waitMs = Math.min(1000 * 2 ** (attempt - 1), 10000)
    reconnectTimer = window.setTimeout(() => {
      reconnectTimer = null
      void connectLoop()
    }, waitMs)
  }

  const connectLoop = async (): Promise<void> => {
    currentController = new AbortController()
    onStatus(attempt === 0 ? 'connecting' : 'reconnecting', attempt)

    try {
      const response = await fetch('/api/v1/events/stream', {
        method: 'GET',
        headers: {
          ...authHeader(token),
        },
        signal: currentController.signal,
      })

      if (!response.ok || !response.body) {
        throw new Error(`SSE no disponible (${response.status})`)
      }

      attempt = 0
      onStatus('connected', attempt)

      const reader = response.body.getReader()
      const decoder = new TextDecoder('utf-8')
      let pending = ''

      while (active) {
        const { done, value } = await reader.read()
        if (done) break
        if (!value) continue
        pending = parseEventChunk(decoder.decode(value, { stream: true }), pending, onEvent)
      }

      if (active) {
        scheduleReconnect(new Error('SSE stream finalizado'))
      }
    } catch (error) {
      if (!active || isAbortError(error)) return
      scheduleReconnect(error)
    }
  }

  void connectLoop()

  return () => {
    active = false
    onStatus('disconnected', attempt)
    if (currentController) {
      currentController.abort()
      currentController = null
    }
    if (reconnectTimer) {
      clearTimeout(reconnectTimer)
      reconnectTimer = null
    }
  }
}
