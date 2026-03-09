export interface ProjectStatsItem {
  project_id: number
  project_name: string
  total: number
  passed: number
}

export interface OverviewStats {
  total_persons: number
  today_new: number
  week_new: number
  month_new: number
  status_breakdown: Record<string, number>
  conversion_rate: number
  pending_reminders: number
  project_stats: ProjectStatsItem[]
}

export interface FunnelItem {
  status: string
  count: number
  percentage: number
}

export interface DailyStats {
  date: string
  new_count: number
  passed_count: number
  failed_count: number
}

export interface FailReasonBreakdown {
  reason: string
  count: number
  percentage: number
}
