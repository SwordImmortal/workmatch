import apiClient from '../api/client'
import type { ApiResponse } from '../types/common'
import type { FollowUp, FollowUpCreate } from '../types/followUp'

export const followUpApi = {
  getByPersonProject: async (personProjectId: number): Promise<FollowUp[]> => {
    const response = await apiClient.get<ApiResponse<FollowUp[]>>(`/api/v1/person-projects/${personProjectId}/follow-ups`)
    return response.data.data || []
  },

  getByPerson: async (personId: number): Promise<FollowUp[]> => {
    const response = await apiClient.get<ApiResponse<FollowUp[]>>(`/api/v1/persons/${personId}/follow-ups`)
    return response.data.data || []
  },

  getByProject: async (projectId: number): Promise<FollowUp[]> => {
    const response = await apiClient.get<ApiResponse<FollowUp[]>>(`/api/v1/projects/${projectId}/follow-ups`)
    return response.data.data || []
  },

  create: async (data: FollowUpCreate): Promise<FollowUp> => {
    const response = await apiClient.post<ApiResponse<FollowUp>>('/api/v1/follow-ups', data)
    return response.data.data
  },

  delete: async (id: number): Promise<void> => {
    await apiClient.delete(`/api/v1/follow-ups/${id}`)
  },
}
