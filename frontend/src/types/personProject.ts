import type { PersonProjectStatus, FailReason } from '.'

export interface PersonProject {
  id: number
  person_id: number
  project_id: number
  owner_id: number
  status: PersonProjectStatus
  fail_reason: FailReason | null
  fail_remark: string | null
  attended_training: boolean | null
  purchased_package: boolean | null
  completed_rooms: number | null
  created_at: string
  updated_at: string
  // 关联数据
  person_name?: string
  person_phone?: string
  project_name?: string
  enterprise_name?: string
  owner_name?: string
}

export interface PersonProjectCreate {
  person_id: number
  project_id: number
  owner_id: number
}

export interface StatusChangeRequest {
  status: PersonProjectStatus
  fail_reason?: FailReason
  fail_remark?: string
}

export interface BatchStatusChangeRequest {
  person_project_ids: number[]
  status: PersonProjectStatus
  fail_reason?: FailReason
  fail_remark?: string
}

export interface ReassignRequest {
  project_id: number
  owner_id: number
}
