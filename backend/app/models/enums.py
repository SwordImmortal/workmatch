"""枚举定义模块。"""

import enum


class UserRole(str, enum.Enum):
    """用户角色。"""

    ADMIN = "admin"  # 系统管理员
    MANAGER = "manager"  # 招聘主管
    RECRUITER = "recruiter"  # 招聘专员


class ProjectStatus(str, enum.Enum):
    """项目状态。"""

    ACTIVE = "active"
    PAUSED = "paused"
    CLOSED = "closed"


class EnterpriseStatus(str, enum.Enum):
    """企业状态。"""

    ACTIVE = "active"
    INACTIVE = "inactive"


class PersonProjectStatus(str, enum.Enum):
    """人员项目状态（8 个核心状态）。"""

    SIGNED_UP = "signed_up"  # 已报名
    INVITED = "invited"  # 已邀约
    INTERVIEW_PENDING = "interview_pending"  # 待面试
    INTERVIEWED = "interviewed"  # 已面试
    IN_TRIAL = "in_trial"  # 试工中
    TRIAL_PASSED = "trial_passed"  # 试工通过
    FAILED = "failed"  # 失败
    UNREACHABLE = "unreachable"  # 联系不上


class FailReason(str, enum.Enum):
    """失败原因标签。"""

    NO_SHOW = "no_show"  # 爽约
    REJECTED = "rejected"  # 拒绝
    NO_PACKAGE = "no_package"  # 未购包（京东）
    NO_TRAINING = "no_training"  # 未到训
    RESCHEDULED = "rescheduled"  # 改约
    ABANDONED = "abandoned"  # 放弃
    NOT_QUALIFIED = "not_qualified"  # 不符合要求
    OTHER = "other"  # 其他


class Source(str, enum.Enum):
    """来源渠道。"""

    BOSS = "boss"  # BOSS直聘
    KUAISHOU = "kuaishou"  # 快手
    DOUYIN = "douyin"  # 抖音
    FIVE_EIGHT = "58"  # 58同城
    REFERRAL = "referral"  # 内推
    OTHER = "other"  # 其他


class Gender(str, enum.Enum):
    """性别。"""

    MALE = "male"
    FEMALE = "female"
    UNKNOWN = "unknown"


class ReminderStatus(str, enum.Enum):
    """提醒状态。"""

    PENDING = "pending"
    COMPLETED = "completed"
    IGNORED = "ignored"
