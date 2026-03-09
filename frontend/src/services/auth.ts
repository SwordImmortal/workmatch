import apiClient from '../api/client'
import type { ApiResponse } from '../types'

export interface LoginRequest {
  username: string
  password: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  user: {
    id: number
    username: string
    name: string
    role: string
  }
}

export interface UserInfo {
  id: number
  username: string
  name: string
  role: string
}

export const authApi = {
  login: async (data: LoginRequest): Promise<LoginResponse> => {
    const formData = new FormData()
    formData.append('username', data.username)
    formData.append('password', data.password)
    const response = await apiClient.post<LoginResponse>('/api/v1/auth/login', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return response.data
  },

  getMe: async (): Promise<UserInfo> => {
    const response = await apiClient.get<ApiResponse<UserInfo>>('/api/v1/auth/me')
    return response.data.data
  },

  logout: async (): Promise<void> => {
    await apiClient.post('/api/v1/auth/logout')
  },
}
