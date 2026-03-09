export interface Person {
  id: number
  name: string
  phone: string
  id_card: string | null
  gender: 'male' | 'female' | 'unknown'
  age: number | null
  city: string
  address: string | null
  source: 'boss' | 'kuaishou' | 'douyin' | '58' | 'referral' | 'other'
  remark: string | null
  reusable: boolean
  created_by: number
  created_at: string
  updated_at: string
}

export interface PersonCreate {
  name: string
  phone: string
  city: string
  id_card?: string
  gender?: 'male' | 'female' | 'unknown'
  age?: number
  address?: string
  source?: 'boss' | 'kuaishou' | 'douyin' | '58' | 'referral' | 'other'
  remark?: string
  reusable?: boolean
}

export interface PersonUpdate {
  name?: string
  phone?: string
  city?: string
  id_card?: string
  gender?: 'male' | 'female' | 'unknown'
  age?: number
  address?: string
  source?: 'boss' | 'kuaishou' | 'douyin' | '58' | 'referral' | 'other'
  remark?: string
  reusable?: boolean
}
