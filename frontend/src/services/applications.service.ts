import type { ApplicationStatus, Filters, LoanCreateRequest, LoanDetail, LoanListResponse } from '../models'
import { authHeader, request } from './http'

export async function createApplication(
  token: string,
  payload: LoanCreateRequest,
  debugDebtLevel?: 'low' | 'medium' | 'high',
): Promise<LoanDetail> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...authHeader(token),
  }
  if (debugDebtLevel) {
    headers['X-Debug-Debt-Level'] = debugDebtLevel
  }

  return request<LoanDetail>('/applications', {
    method: 'POST',
    headers,
    body: JSON.stringify(payload),
  })
}

export async function listApplications(token: string, filters: Filters): Promise<LoanListResponse> {
  const params = new URLSearchParams()
  if (filters.country) params.set('country', filters.country)
  if (filters.status) params.set('status', filters.status)
  const query = params.toString() ? `?${params.toString()}` : ''

  return request<LoanListResponse>(`/applications${query}`, {
    method: 'GET',
    headers: {
      ...authHeader(token),
    },
  })
}

export async function getApplicationDetail(token: string, id: string): Promise<LoanDetail> {
  return request<LoanDetail>(`/applications/${id}`, {
    method: 'GET',
    headers: {
      ...authHeader(token),
    },
  })
}

export async function updateApplicationStatus(token: string, id: string, status: ApplicationStatus): Promise<LoanDetail> {
  return request<LoanDetail>(`/applications/${id}/status`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
      ...authHeader(token),
    },
    body: JSON.stringify({ status }),
  })
}

export async function getAvailableTransitions(token: string, applicationId: string): Promise<ApplicationStatus[]> {
  return request<ApplicationStatus[]>(`/applications/${applicationId}/available-transitions`, {
    method: 'GET',
    headers: {
      ...authHeader(token),
    },
  })
}
