import apiClient from '../api/client'
import type { ApiResponse, ListResponse } from '../types/common'
import type { Project, ProjectCreate, ProjectUpdate, Enterprise, EnterpriseCreate, EnterpriseUpdate } from '../types/project'

export interface ProjectQueryParams {
  skip?: number
  limit?: number
  enterprise_id?: number
  status?: string
  search?: string
}

export const projectApi = {
  getProjects: async (params?: ProjectQueryParams): Promise<ListResponse<Project>> => {
    const response = await apiClient.get<ListResponse<Project>>('/api/v1/projects/', { params })
    return response.data
  },

  getProject: async (id: number): Promise<Project> => {
    const response = await apiClient.get<ApiResponse<Project>>(`/api/v1/projects/${id}`)
    return response.data.data
  },

  createProject: async (data: ProjectCreate): Promise<Project> => {
    const response = await apiClient.post<ApiResponse<Project>>('/api/v1/projects/', data)
    return response.data.data
  },

  updateProject: async (id: number, data: ProjectUpdate): Promise<Project> => {
    const response = await apiClient.put<ApiResponse<Project>>(`/api/v1/projects/${id}`, data)
    return response.data.data
  },

  deleteProject: async (id: number): Promise<void> => {
    await apiClient.delete(`/api/v1/projects/${id}`)
  },
}

export const enterpriseApi = {
  getList: async (params?: { skip?: number; limit?: number; status?: string }): Promise<ListResponse<Enterprise>> => {
    const response = await apiClient.get<ListResponse<Enterprise>>('/api/v1/enterprises/', { params })
    return response.data
  },

  getById: async (id: number): Promise<Enterprise> => {
    const response = await apiClient.get<ApiResponse<Enterprise>>(`/api/v1/enterprises/${id}`)
    return response.data.data
  },

  create: async (data: EnterpriseCreate): Promise<Enterprise> => {
    const response = await apiClient.post<ApiResponse<Enterprise>>('/api/v1/enterprises/', data)
    return response.data.data
  },

  update: async (id: number, data: EnterpriseUpdate): Promise<Enterprise> => {
    const response = await apiClient.put<ApiResponse<Enterprise>>(`/api/v1/enterprises/${id}`, data)
    return response.data.data
  },

  delete: async (id: number): Promise<void> => {
    await apiClient.delete(`/api/v1/enterprises/${id}`)
  },
}
