export interface Project {
  id: number
  enterprise_id: number
  name: string
  job_title: string
  salary_range: string | null
  work_address: string | null
  requirement: string | null
  priority: number
  status: 'active' | 'paused' | 'closed'
  unit_price: number | null
  enterprise?: Enterprise
  created_at: string
}

export interface ProjectCreate {
  enterprise_id: number
  name: string
  job_title: string
  salary_range?: string
  work_address?: string
  requirement?: string
  priority?: number
  unit_price?: number
}

export interface ProjectUpdate {
  name?: string
  job_title?: string
  salary_range?: string
  work_address?: string
  requirement?: string
  priority?: number
  status?: 'active' | 'paused' | 'closed'
  unit_price?: number
}

export interface Enterprise {
  id: number
  name: string
  contact_name: string | null
  contact_phone: string | null
  address: string | null
  description: string | null
  status: 'active' | 'inactive'
  created_at: string
}

export interface EnterpriseCreate {
  name: string
  contact_name?: string
  contact_phone?: string
  address?: string
  description?: string
}

export interface EnterpriseUpdate {
  name?: string
  contact_name?: string
  contact_phone?: string
  address?: string
  description?: string
  status?: 'active' | 'inactive'
}
