import { useState, useEffect } from 'react'
import { Table, Card, Button, Space, Input, Select, Tag, Popconfirm, message } from 'antd'
import { PlusOutlined, SearchOutlined, ExportOutlined, UploadOutlined } from '@ant-design/icons'
import { personApi, type PersonQueryParams } from '../../services/person'
import type { Person } from '../../types/person'
import type { ColumnsType } from 'antd/es/table'

const PersonList: React.FC = () => {
  const [loading, setLoading] = useState(false)
  const [data, setData] = useState<Person[]>([])
  const [total, setTotal] = useState(0)
  const [params, setParams] = useState<PersonQueryParams>({
    skip: 0,
    limit: 20,
  })

  const fetchData = async () => {
    setLoading(true)
    try {
      const result = await personApi.getList(params)
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

  const columns: ColumnsType<Person> = [
    {
      title: 'ID',
      dataIndex: 'id',
      width: 60,
    },
    {
      title: '姓名',
      dataIndex: 'name',
      width: 100,
    },
    {
      title: '手机号',
      dataIndex: 'phone',
      width: 130,
    },
    {
      title: '城市',
      dataIndex: 'city',
      width: 100,
    },
    {
      title: '性别',
      dataIndex: 'gender',
      width: 80,
      render: (gender: string) => {
        const map: Record<string, string> = {
          male: '男',
          female: '女',
          unknown: '未知',
        }
        return map[gender] || gender
      },
    },
    {
      title: '年龄',
      dataIndex: 'age',
      width: 80,
    },
    {
      title: '来源',
      dataIndex: 'source',
      width: 100,
      render: (source: string) => {
        const map: Record<string, { label: string; color: string }> = {
          boss: { label: 'BOSS直聘', color: 'blue' },
          kuaishou: { label: '快手', color: 'orange' },
          douyin: { label: '抖音', color: 'purple' },
          '58': { label: '58同城', color: 'cyan' },
          referral: { label: '内推', color: 'green' },
          other: { label: '其他', color: 'default' },
        }
        const item = map[source] || map.other
        return <Tag color={item.color}>{item.label}</Tag>
      },
    },
    {
      title: '可复用',
      dataIndex: 'reusable',
      width: 80,
      render: (reusable: boolean) => (
        <Tag color={reusable ? 'green' : 'default'}>
          {reusable ? '是' : '否'}
        </Tag>
      ),
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
      width: 150,
      render: (_: unknown, record: Person) => (
        <Space size="small">
          <Button type="link" size="small">查看</Button>
          <Popconfirm
            title="确定删除？"
            onConfirm={async () => {
              await personApi.delete(record.id)
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
      <Card>
        <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between' }}>
          <Space>
            <Input
              placeholder="搜索姓名/手机号"
              prefix={<SearchOutlined />}
              style={{ width: 200 }}
              allowClear
              onChange={(e) => setParams({ ...params, search: e.target.value || undefined })}
            />
            <Select
              placeholder="城市"
              style={{ width: 120 }}
              allowClear
              onChange={(value) => setParams({ ...params, city: value || undefined })}
            />
          </Space>
          <Space>
            <Button icon={<UploadOutlined />}>导入</Button>
            <Button icon={<ExportOutlined />} onClick={() => personApi.exportExcel(params)}>
              导出
            </Button>
            <Button type="primary" icon={<PlusOutlined />}>
              新增人员
            </Button>
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
            showQuickJumper: true,
            onChange: (page, pageSize) => {
              setParams({ ...params, skip: (page - 1) * pageSize, limit: pageSize })
            },
          }}
        />
      </Card>
    </div>
  )
}

export default PersonList
