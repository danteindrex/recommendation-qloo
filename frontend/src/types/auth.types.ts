export interface User {
  id: string
  email: string
  role: 'consumer' | 'enterprise' | 'admin'
  subscriptionTier: 'free' | 'premium' | 'enterprise'
  createdAt: string
  updatedAt: string
}

export interface AuthState {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
}

export interface LoginCredentials {
  email: string
  password?: string
  passkeyCredential?: string
}

export interface RegisterData {
  email: string
  password?: string
  role?: 'consumer' | 'enterprise'
}