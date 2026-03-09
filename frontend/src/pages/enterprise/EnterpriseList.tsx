import { useState, useEffect } from 'react'
import { Table, Card, Button, Space, Tag, Popconfirm, message } from 'antd'
import { PlusOutlined, TeamOutlined } from '@ant-design/icons'
import { enterpriseApi } from '../../services/project'
import type { Enterprise } from '../../types/project'
import type { ColumnsType } from 'antd/es/table'

const EnterpriseList: React.FC = () => {
  const [loading, setLoading] = useState(false)
  const [data, setData] = useState<Enterprise[]>([])
  const [total, setTotal] = useState(0)
  const [params, setParams] = useState({ skip: 0, limit: 20 })

  const fetchData = async () => {
    setLoading(true)
    try {
      const result = await enterpriseApi.getList(params)
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

  const columns: ColumnsType<Enterprise> = [
    {
      title: 'ID',
      dataIndex: 'id',
      width: 60,
    },
    {
      title: '企业名称',
      dataIndex: 'name',
      width: 200,
    },
    {
      title: '联系人',
      dataIndex: 'contact_name',
      width: 120,
    },
    {
      title: '联系电话',
      dataIndex: 'contact_phone',
      width: 140,
    },
    {
      title: '地址',
      dataIndex: 'address',
      ellipsis: true,
    },
    {
      title: '状态',
      dataIndex: 'status',
      width: 80,
      render: (status: string) => (
        <Tag color={status === 'active' ? 'green' : 'default'}>
          {status === 'active' ? '活跃' : '停用'}
        </Tag>
      ),
    },
    {
      title: '操作',
      key: 'action',
      width: 120,
      render: (_: unknown, record: Enterprise) => (
        <Space size="small">
          <Button type="link" size="small">编辑</Button>
          <Popconfirm
            title="确定删除？"
            onConfirm={async () => {
              await enterpriseApi.delete(record.id)
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
        title="企业管理"
        extra={
          <Button type="primary" icon={<PlusOutlined />}>
            新增企业
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

export default EnterpriseList
