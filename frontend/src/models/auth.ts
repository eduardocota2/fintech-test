export interface AuthForm {
  email: string
  password: string
  is_admin: boolean
}

export interface LoginResponse {
  access_token: string
  token_type: string
}

export interface RegisterRequest {
  email: string
  password: string
  is_admin: boolean
}

export interface SessionState {
  token: string
  tokenType: string
  isAdmin: boolean
}
