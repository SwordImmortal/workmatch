import apiClient from '../api/client'
import type { ApiResponse } from '../types/common'
import type { Reminder, ReminderCreate, ReminderUpdate } from '../types/reminder'

export const reminderApi = {
  getByPersonProject: async (personProjectId: number): Promise<Reminder[]> => {
    const response = await apiClient.get<ApiResponse<Reminder[]>>(`/api/v1/person-projects/${personProjectId}/reminders`)
    return response.data.data || []
  },

  getByPerson: async (personId: number): Promise<Reminder[]> => {
    const response = await apiClient.get<ApiResponse<Reminder[]>>(`/api/v1/persons/${personId}/reminders`)
    return response.data.data || []
  },

  getByProject: async (projectId: number): Promise<Reminder[]> => {
    const response = await apiClient.get<ApiResponse<Reminder[]>>(`/api/v1/projects/${projectId}/reminders`)
    return response.data.data || []
  },

  getPending: async (): Promise<Reminder[]> => {
    const response = await apiClient.get<ApiResponse<Reminder[]>>('/api/v1/reminders/pending')
    return response.data.data || []
  },

  create: async (data: ReminderCreate): Promise<Reminder> => {
    const response = await apiClient.post<ApiResponse<Reminder>>('/api/v1/reminders', data)
    return response.data.data
  },

  update: async (id: number, data: ReminderUpdate): Promise<Reminder> => {
    const response = await apiClient.put<ApiResponse<Reminder>>(`/api/v1/reminders/${id}`, data)
    return response.data.data
  },

  complete: async (id: number): Promise<Reminder> => {
    const response = await apiClient.put<ApiResponse<Reminder>>(`/api/v1/reminders/${id}/complete`)
    return response.data.data
  },

  delete: async (id: number): Promise<void> => {
    await apiClient.delete(`/api/v1/reminders/${id}`)
  },
}
