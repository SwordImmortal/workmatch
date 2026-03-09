import apiClient from '../api/client'
import type { ApiResponse } from '../types/common'
import type { OverviewStats, FunnelItem, DailyStats, FailReasonBreakdown } from '../types/statistics'

export const statisticsApi = {
  getOverview: async (projectId?: number): Promise<OverviewStats> => {
    const params = projectId ? { project_id: projectId } : {}
    const response = await apiClient.get<ApiResponse<OverviewStats>>('/api/v1/statistics/overview', { params })
    return response.data.data
  },

  getProjectFunnel: async (projectId: number): Promise<FunnelItem[]> => {
    const response = await apiClient.get<ApiResponse<FunnelItem[]>>(`/api/v1/statistics/funnel/${projectId}`)
    return response.data.data
  },

  getDailyStatistics: async (projectId?: number, days?: number): Promise<DailyStats[]> => {
    const params: Record<string, unknown> = {}
    if (projectId) params.project_id = projectId
    if (days) params.days = days
    const response = await apiClient.get<ApiResponse<DailyStats[]>>('/api/v1/statistics/daily', { params })
    return response.data.data
  },

  getRangeStatistics: async (startDate: string, endDate: string, projectId?: number): Promise<DailyStats[]> => {
    const params: Record<string, unknown> = { start_date: startDate, end_date: endDate }
    if (projectId) params.project_id = projectId
    const response = await apiClient.get<ApiResponse<DailyStats[]>>('/api/v1/statistics/range', { params })
    return response.data.data
  },

  getFailReasonBreakdown: async (projectId?: number): Promise<FailReasonBreakdown[]> => {
    const params = projectId ? { project_id: projectId } : {}
    const response = await apiClient.get<ApiResponse<FailReasonBreakdown[]>>('/api/v1/statistics/fail-reasons', { params })
    return response.data.data
  },

  exportStatistics: async (projectId: number): Promise<void> => {
    window.open(`${apiClient.defaults.baseURL}/api/v1/statistics/export/${projectId}`, '_blank')
  },
}
