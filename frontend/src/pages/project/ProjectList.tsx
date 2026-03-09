import { useState, useEffect } from 'react'
import { Table, Card, Button, Space, Tag, Popconfirm, message } from 'antd'
import { PlusOutlined, BarChartOutlined } from '@ant-design/icons'
import { projectApi, type ProjectQueryParams } from '../../services/project'
import type { Project } from '../../types/project'
import type { ColumnsType } from 'antd/es/table'

const ProjectList: React.FC = () => {
  const [loading, setLoading] = useState(false)
  const [data, setData] = useState<Project[]>([])
  const [total, setTotal] = useState(0)
  const [params, setParams] = useState<ProjectQueryParams>({
    skip: 0,
    limit: 20,
  })

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

  const statusMap: Record<string, { label: string; color: string }> = {
    active: { label: '进行中', color: 'green' },
    paused: { label: '已暂停', color: 'orange' },
    closed: { label: '已关闭', color: 'default' },
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
      width: 200,
    },
    {
      title: '招聘岗位',
      dataIndex: 'job_title',
      width: 150,
    },
    {
      title: '薪资范围',
      dataIndex: 'salary_range',
      width: 150,
    },
    {
      title: '工作地点',
      dataIndex: 'work_address',
      width: 200,
      ellipsis: true,
    },
    {
      title: '优先级',
      dataIndex: 'priority',
      width: 80,
      sorter: true,
    },
    {
      title: '状态',
      dataIndex: 'status',
      width: 100,
      render: (status: string) => {
        const item = statusMap[status] || statusMap.active
        return <Tag color={item.color}>{item.label}</Tag>
      },
    },
    {
      title: '单价',
      dataIndex: 'unit_price',
      width: 100,
      render: (price: number) => (price ? `¥${price}` : '-'),
    },
    {
      title: '操作',
      key: 'action',
      width: 180,
      render: (_: unknown, record: Project) => (
        <Space size="small">
          <Button type="link" size="small" icon={<BarChartOutlined />}>
            统计
          </Button>
          <Button type="link" size="small">编辑</Button>
          <Popconfirm
            title="确定删除？"
            onConfirm={async () => {
              await projectApi.deleteProject(record.id)
              message.success('删除成功')
              fetchData()
            }}
          >
            <Button type="link" size="small" danger>删除</Button>
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
          <Button type="primary" icon={<PlusOutlined />}>
            新增项目
          </Button>
        }
      >
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
    </div>
  )
}

export default ProjectList
