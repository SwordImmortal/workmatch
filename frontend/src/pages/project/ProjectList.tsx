import { useState, useEffect } from 'react'
import { Table, Card, Button, Space, Input, Select, Tag, Popconfirm, message } from 'antd'
import { PlusOutlined, SearchOutlined, BarChartOutlined } from '@ant-design/icons'
import { projectApi, type ProjectQueryParams } from '../../services/project'
import type { Project } from '../../types/project'
import type { ColumnsType } from 'antd/es/table'
import ProjectFormModal from './ProjectFormModal'

const statusOptions = [
  { value: 'active', label: '进行中' },
  { value: 'paused', label: '已暂停' },
  { value: 'closed', label: '已关闭' },
]

const ProjectList: React.FC = () => {
  const [loading, setLoading] = useState(false)
  const [data, setData] = useState<Project[]>([])
  const [total, setTotal] = useState(0)
  const [params, setParams] = useState<ProjectQueryParams>({
    skip: 0,
    limit: 20,
  })

  // Modal 状态
  const [modalOpen, setModalOpen] = useState(false)
  const [editingProject, setEditingProject] = useState<Project | undefined>()

  const fetchData = async () => {
    setLoading(true)
    try {
      const result = await projectApi.getProjects(params)
      setData(result.data)
      setTotal(result.total)
    } catch (error) {
      message.error('获取数据失败')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [params])

  const handleCreate = () => {
    setEditingProject(undefined)
    setModalOpen(true)
  }

  const handleEdit = (project: Project) => {
    setEditingProject(project)
    setModalOpen(true)
  }

  const handleDelete = async (id: number) => {
    try {
      await projectApi.deleteProject(id)
      message.success('删除成功')
      fetchData()
    } catch (error) {
      message.error('删除失败')
    }
  }

  const handleModalSuccess = () => {
    setModalOpen(false)
    fetchData()
  }

  const columns: ColumnsType<Project> = [
    {
      title: 'ID',
      dataIndex: 'id',
      width: 60,
    },
    {
      title: '项目名称',
      dataIndex: 'name',
      width: 150,
    },
    {
      title: '招聘岗位',
      dataIndex: 'job_title',
      width: 120,
    },
    {
      title: '薪资范围',
      dataIndex: 'salary_range',
      width: 120,
    },
    {
      title: '优先级',
      dataIndex: 'priority',
      width: 80,
      render: (priority: number) => (
        <Tag color={priority >= 80 ? 'red' : priority >= 50 ? 'orange' : 'default'}>
          {priority}
        </Tag>
      ),
    },
    {
      title: '状态',
      dataIndex: 'status',
      width: 100,
      render: (status: string) => {
        const option = statusOptions.find(o => o.value === status)
        const colorMap: Record<string, string> = {
          active: 'green',
          paused: 'orange',
          closed: 'default',
        }
        return (
          <Tag color={colorMap[status] || 'default'}>
            {option?.label || status}
          </Tag>
        )
      },
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      width: 180,
      render: (date: string) => new Date(date).toLocaleString(),
    },
    {
      title: '操作',
      key: 'action',
      width: 200,
      fixed: 'right',
      render: (_: unknown, record: Project) => (
        <Space size="small">
          <Button type="link" size="small" icon={<BarChartOutlined />}>
            统计
          </Button>
          <Button type="link" size="small" onClick={() => handleEdit(record)}>
            编辑
          </Button>
          <Popconfirm
            title="确定删除？"
            onConfirm={() => handleDelete(record.id)}
          >
            <Button type="link" size="small" danger>
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ]

  return (
    <div>
      <Card
        title="项目管理"
        extra={
          <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>
            新增项目
          </Button>
        }
      >
        <div style={{ marginBottom: 16 }}>
          <Space>
            <Input
              placeholder="搜索项目名称"
              prefix={<SearchOutlined />}
              style={{ width: 200 }}
              allowClear
              onChange={(e) => setParams({ ...params, search: e.target.value || undefined, skip: 0 })}
            />
            <Select
              placeholder="状态"
              style={{ width: 120 }}
              allowClear
              options={statusOptions}
              onChange={(value) => setParams({ ...params, status: value || undefined, skip: 0 })}
            />
          </Space>
        </div>
        <Table
          columns={columns}
          dataSource={data}
          rowKey="id"
          loading={loading}
          pagination={{
            current: Math.floor((params.skip || 0) / (params.limit || 20)) + 1,
            pageSize: params.limit,
            total,
            showSizeChanger: true,
            onChange: (page, pageSize) => {
              setParams({ ...params, skip: (page - 1) * pageSize, limit: pageSize })
            },
          }}
        />
      </Card>

      <ProjectFormModal
        open={modalOpen}
        project={editingProject}
        onClose={() => setModalOpen(false)}
        onSuccess={handleModalSuccess}
      />
    </div>
  )
}

export default ProjectList
