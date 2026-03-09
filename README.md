# WorkMatch

蓝领 RPO 招聘管理系统

## 项目结构

```
workmatch/
├── backend/                # Python 后端
│   ├── app/
│   │   ├── api/v1/       # API 路由
│   │   ├── models/        # SQLAlchemy 模型
│   │   ├── schemas/       # Pydantic 验证模型
│   │   ├── services/      # 业务逻辑
│   │   └── utils/         # 工具函数
│   ├── tests/
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/               # React 前端
│   ├── src/
│   │   ├── api/           # API 客户端
│   │   ├── components/    # UI 组件
│   │   ├── pages/         # 页面
│   │   ├── store/         # Zustand 状态
│   │   ├── types/         # TypeScript 类型
│   │   └── utils/         # 工具函数
│   ├── package.json
│   └── .env.example
│
├── docs/
│   └── 系统需求设计文档.md
│
└── README.md
```

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | FastAPI + SQLAlchemy + MySQL |
| 前端 | React + Vite + TypeScript + Ant Design |
| 状态管理 | Zustand |
| 认证 | JWT |

## 快速开始

### 环境要求

- Python 3.11+
- Node.js 18+
- MySQL 8.0

### 后端启动

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 复制环境变量
cp .env.example .env
# 编辑 .env 配置数据库连接

# 启动服务
uvicorn app.main:app --reload --port 8000
```

### 前端启动

```bash
cd frontend

# 安装依赖
npm install

# 复制环境变量
cp .env.example .env

# 启动开发服务
npm run dev
```

## 访问地址

| 服务 | 地址 |
|------|------|
| 前端 | http://localhost:5173 |
| 后端 API | http://localhost:8000 |
| API 文档 | http://localhost:8000/docs |

## 开发阶段

| 阶段 | 内容 | 状态 |
|------|------|:----:|
| Phase 0 | 项目初始化 | ✅ 完成 |
| Phase 1 | 数据库设计 + 后端基础架构 | 待开始 |
| Phase 2 | 用户认证 + 权限 | 待开始 |
| Phase 3 | 人员管理 | 待开始 |
| Phase 4 | 项目/企业管理 | 待开始 |
| Phase 5 | 人员-项目关联 + 状态流转 | 待开始 |
| Phase 6 | 跟进提醒模块 | 待开始 |
| Phase 7 | 统计模块 | 待开始 |
| Phase 8 | 集成测试 | 待开始 |
| Phase 9 | 部署上线 | 待开始 |
