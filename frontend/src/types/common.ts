// API 响应结构
export interface ApiResponse<T = unknown> {
  code: number
  message: string
  timestamp: number
  data: T
}

// 列表响应
export interface ListResponse<T> extends ApiResponse<T[]> {
  total: number
  skip: number
  limit: number
}

// 分页数据
export interface PaginatedData<T> {
  items: T[]
  total: number
  page: number
  page_size: number
}

// 分页响应
export interface PaginatedResponse<T> extends ApiResponse<PaginatedData<T>> {}
