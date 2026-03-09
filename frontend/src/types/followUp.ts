export interface FollowUp {
  id: number
  person_project_id: number
  content: string
  next_follow_time: string | null
  created_by: number
  created_by_name: string
  created_at: string
  updated_at: string
}

export interface FollowUpCreate {
  person_project_id: number
  content: string
  next_follow_time?: string | null
}
