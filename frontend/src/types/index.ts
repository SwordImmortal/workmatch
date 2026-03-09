// 状态枚举
export enum PersonProjectStatus {
  SIGNED_UP = 'signed_up',           // 已报名
  INVITED = 'invited',               // 已邀约
  INTERVIEW_PENDING = 'interview_pending', // 待面试
  INTERVIEWED = 'interviewed',       // 已面试
  IN_TRIAL = 'in_trial',             // 试工中
  TRIAL_PASSED = 'trial_passed',     // 试工通过
  FAILED = 'failed',                 // 失败
  UNREACHABLE = 'unreachable',       // 联系不上
}

// 失败原因枚举
export enum FailReason {
  NO_SHOW = 'no_show',               // 爽约
  REJECTED = 'rejected',             // 拒绝
  NO_PACKAGE = 'no_package',         // 未购包（京东）
  NO_TRAINING = 'no_training',       // 未到训
  RESCHEDULED = 'rescheduled',       // 改约
  ABANDONED = 'abandoned',           // 放弃
  NOT_QUALIFIED = 'not_qualified',   // 不符合要求
  OTHER = 'other',                   // 其他
}

// 来源渠道枚举
export enum Source {
  BOSS = 'boss',                     // BOSS直聘
  KUAISHOU = 'kuaishou',             // 快手
  DOUYIN = 'douyin',                 // 抖音
  FIVE_EIGHT = '58',                 // 58同城
  REFERRAL = 'referral',             // 内推
  OTHER = 'other',                   // 其他
}

// 性别枚举
export enum Gender {
  MALE = 'male',                     // 男
  FEMALE = 'female',                 // 女
  UNKNOWN = 'unknown',               // 未知
}

// API 响应结构
export interface ApiResponse<T> {
  code: number
  message: string
  data: T
  timestamp: number
}

// 分页响应
export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
}
