import apiClient from '../api/client'
import type { ApiResponse, ListResponse } from '../types/common'
import type { PersonProject, PersonProjectCreate, StatusChangeRequest, BatchStatusChangeRequest, ReassignRequest } from '../types/personProject'

export interface PersonProjectQueryParams {
  skip?: number
  limit?: number
  project_id?: number
  person_id?: number
  status?: string
  owner_id?: number
}

export const personProjectApi = {
  getList: async (params?: PersonProjectQueryParams): Promise<ListResponse<PersonProject>> => {
    const response = await apiClient.get<ListResponse<PersonProject>>('/api/v1/person-projects/', { params })
    return response.data
  },

  getByProject: async (projectId: number, params?: { status?: string }): Promise<PersonProject[]> => {
    const response = await apiClient.get<ListResponse<PersonProject>>(`/api/v1/person-projects/project/${projectId}`, { params })
    return response.data.data
  },

  create: async (data: PersonProjectCreate): Promise<PersonProject> => {
    const response = await apiClient.post<ApiResponse<PersonProject>>('/api/v1/person-projects/', data)
    return response.data.data
  },

  changeStatus: async (id: number, data: StatusChangeRequest): Promise<PersonProject> => {
    const response = await apiClient.post<ApiResponse<PersonProject>>(`/api/v1/person-projects/${id}/status`, data)
    return response.data.data
  },

  batchChangeStatus: async (data: BatchStatusChangeRequest): Promise<{
    success_count: number
    fail_count: number
    errors: Array<{ id: number; message: string }>
  }> => {
    const response = await apiClient.post<ApiResponse<{
      success_count: number
      fail_count: number
      errors: Array<{ id: number; message: string }>
    }>>('/api/v1/person-projects/batch-status', data)
    return response.data.data
  },

  reassign: async (id: number, data: ReassignRequest): Promise<PersonProject> => {
    const response = await apiClient.post<ApiResponse<PersonProject>>(`/api/v1/person-projects/${id}/reassign`, data)
    return response.data.data
  },
}
