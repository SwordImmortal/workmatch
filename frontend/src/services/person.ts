import apiClient from '../api/client'
import type { ApiResponse, ListResponse } from '../types/common'
import type { Person, PersonCreate, PersonUpdate } from '../types/person'

export interface PersonQueryParams {
  skip?: number
  limit?: number
  city?: string
  source?: string
  reusable?: boolean
  search?: string
}

export const personApi = {
  getList: async (params: PersonQueryParams): Promise<ListResponse<Person>> => {
    const response = await apiClient.get<ListResponse<Person>>('/api/v1/persons/', { params })
    return response.data
  },

  getById: async (id: number): Promise<Person> => {
    const response = await apiClient.get<ApiResponse<Person>>(`/api/v1/persons/${id}`)
    return response.data.data
  },

  getWithProjects: async (id: number) => {
    const response = await apiClient.get<ApiResponse<Person & { projects: any[] }>>(`/api/v1/persons/${id}/projects`)
    return response.data.data
  },

  create: async (data: PersonCreate): Promise<Person> => {
    const response = await apiClient.post<ApiResponse<Person>>('/api/v1/persons/', data)
    return response.data.data
  },

  update: async (id: number, data: PersonUpdate): Promise<Person> => {
    const response = await apiClient.put<ApiResponse<Person>>(`/api/v1/persons/${id}`, data)
    return response.data.data
  },

  delete: async (id: number): Promise<void> => {
    await apiClient.delete(`/api/v1/persons/${id}`)
  },

  downloadTemplate: () => {
    window.open(`${apiClient.defaults.baseURL}/api/v1/persons/import/template`, '_blank')
  },

  importExcel: async (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    const response = await apiClient.post<ApiResponse<{
      success_count: number
      fail_count: number
      total: number
      errors: Array<{ row: number; field: string | null; message: string }>
    }>>('/api/v1/persons/import', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return response.data.data
  },

  exportExcel: (params?: PersonQueryParams) => {
    const query = new URLSearchParams()
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) query.append(key, String(value))
      })
    }
    window.open(`${apiClient.defaults.baseURL}/api/v1/persons/export?${query}`, '_blank')
  },
}
