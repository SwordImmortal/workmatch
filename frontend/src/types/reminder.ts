export interface Reminder {
  id: number
  person_project_id: number
  reminder_time: string
  content: string
  is_completed: boolean
  created_by: number
  created_by_name: string
  created_at: string
  updated_at: string
}

export interface ReminderCreate {
  person_project_id: number
  reminder_time: string
  content: string
}

export interface ReminderUpdate {
  reminder_time?: string
  content?: string
  is_completed?: boolean
}
