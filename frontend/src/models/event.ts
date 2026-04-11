export interface EventPayload {
  action: string
  application_id: string
  details: Record<string, unknown>
  created_at: string
}
