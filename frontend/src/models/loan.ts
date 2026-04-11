export type CountryCode = 'MX' | 'CO'

export type ApplicationStatus = 'submitted' | 'evaluating' | 'pending_review' | 'approved' | 'rejected'

export interface ScoringFactor {
  weight: number
  raw_score: number
  weighted_score: number
  description: string
}

export interface RiskDecision {
  id: string
  loan_application_id: string
  country_code: CountryCode
  decision: 'approved_auto' | 'manual_review' | 'rejected'
  score: number
  max_possible_score: number
  confidence: number
  factors: Record<string, ScoringFactor>
  thresholds: {
    auto_approve: number
    manual_review: number
  }
  reason: string
  evaluated_by: string
  created_at: string
}

export interface AvailableTransition {
  from_status: ApplicationStatus
  to_status: ApplicationStatus
  description: string
}

export interface LoanCreateRequest {
  country: CountryCode
  full_name: string
  document_id: string
  amount_requested: number
  monthly_income: number
  application_date: string
}

export interface LoanListItem {
  id: string
  country: CountryCode
  full_name: string
  amount_requested: number
  status: ApplicationStatus
  application_date: string
  bank_name: string | null
  bank_account_last4: string | null
  created_at: string
}

export interface LoanListResponse {
  items: LoanListItem[]
}

export interface LoanDetail {
  id: string
  user_id: string
  country: CountryCode
  full_name: string
  document_id_masked: string
  amount_requested: number
  monthly_income: number
  application_date: string
  status: ApplicationStatus
  risk_rating: string | null
  bank_name: string | null
  bank_account_last4: string | null
  created_at: string
  updated_at: string
  risk_decisions?: RiskDecision[]
  latest_risk_decision?: RiskDecision
}

export interface Filters {
  country: '' | CountryCode
  status: '' | ApplicationStatus
}
