import { useState, useEffect } from 'react'
import { Table, Card, Button, Space, Input, Select, Tag, Popconfirm, message, Drawer } from 'antd'
import { PlusOutlined, SearchOutlined, ExportOutlined, UploadOutlined, EyeOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons'
import { personApi, type PersonQueryParams } from '../../services/person'
import type { Person } from '../../types/person'
import type { ColumnsType } from 'antd/es/table'
import PersonFormModal from './PersonFormModal'
import PersonDetailDrawer from './PersonDetailDrawer'

const sourceOptions = [
  { value: 'boss', label: 'BOSS直聘' },
  { value: 'kuaishou', label: '快手' },
  { value: 'douyin', label: '抖音' },
  { value: '58', label: '58同城' },
  { value: 'referral', label: '内推' },
  { value: 'other', label: '其他' },
]

const genderOptions = [
  { value: 'male', label: '男' },
  { value: 'female', label: '女' },
  { value: 'unknown', label: '未知' },
]

const PersonList: React.FC = () => {
  const [loading, setLoading] = useState(false)
  const [data, setData] = useState<Person[]>([])
  const [total, setTotal] = useState(0)
  const [params, setParams] = useState<PersonQueryParams>({
    skip: 0,
    limit: 20,
  })

  // Modal 状态
  const [modalOpen, setModalOpen] = useState(false)
  const [editingPerson, setEditingPerson] = useState<Person | undefined>()

  // Drawer 状态
  const [drawerOpen, setDrawerOpen] = useState(false)
  const [selectedPersonId, setSelectedPersonId] = useState<number | null>(null)

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

  const handleCreate = () => {
    setEditingPerson(undefined)
    setModalOpen(true)
  }

  const handleEdit = (person: Person) => {
    setEditingPerson(person)
    setModalOpen(true)
  }

  const handleView = (id: number) => {
    setSelectedPersonId(id)
    setDrawerOpen(true)
  }

  const handleDelete = async (id: number) => {
    try {
      await personApi.delete(id)
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
        const option = genderOptions.find(o => o.value === gender)
        return option?.label || gender
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
        const option = sourceOptions.find(o => o.value === source)
        return <Tag color="blue">{option?.label || source}</Tag>
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
      width: 200,
      fixed: 'right',
      render: (_: unknown, record: Person) => (
        <Space size="small">
          <Button
            type="link"
            size="small"
            icon={<EyeOutlined />}
            onClick={() => handleView(record.id)}
          >
            查看
          </Button>
          <Button
            type="link"
            size="small"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
          >
            编辑
          </Button>
          <Popconfirm
            title="确定删除？"
            onConfirm={() => handleDelete(record.id)}
          >
            <Button type="link" size="small" danger icon={<DeleteOutlined />}>
              删除
            </Button>
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
              onChange={(e) => setParams({ ...params, search: e.target.value || undefined, skip: 0 })}
            />
            <Select
              placeholder="城市"
              style={{ width: 120 }}
              allowClear
              options={[]}
              onChange={(value) => setParams({ ...params, city: value || undefined, skip: 0 })}
            />
            <Select
              placeholder="来源"
              style={{ width: 120 }}
              allowClear
              options={sourceOptions}
              onChange={(value) => setParams({ ...params, source: value || undefined, skip: 0 })}
            />
          </Space>
          <Space>
            <Button icon={<UploadOutlined />}>导入</Button>
            <Button icon={<ExportOutlined />} onClick={() => personApi.exportExcel(params)}>
              导出
            </Button>
            <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>
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

      <PersonFormModal
        open={modalOpen}
        person={editingPerson}
        onClose={() => setModalOpen(false)}
        onSuccess={handleModalSuccess}
      />

      <PersonDetailDrawer
        open={drawerOpen}
        personId={selectedPersonId}
        onClose={() => {
          setDrawerOpen(false)
          setSelectedPersonId(null)
        }}
      />
    </div>
  )
}

export default PersonList
