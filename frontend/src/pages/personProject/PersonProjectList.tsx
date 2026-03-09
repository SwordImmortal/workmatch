import React, { useState, useEffect } from 'react'
import {
  Table,
  Card,
  Button,
  Space,
  Input,
  Select,
  Tag,
  Popconfirm,
  message,
  Drawer,
} from 'antd'
import {
  PlusOutlined,
  SearchOutlined,
  EditOutlined,
  DeleteOutlined,
  UserSwitchOutlined,
} from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import type { PersonProject } from '../../types/personProject'
import { PersonProjectStatus, FailReason } from '../../types'
import type { PersonProjectQueryParams } from '../../services/personProject'
import { personProjectApi } from '../../services/personProject'
import BatchStatusModal from './BatchStatusModal'

const statusOptions: { value: PersonProjectStatus; label: string }[] = [
  { value: PersonProjectStatus.SIGNED_UP, label: '已报名' },
  { value: PersonProjectStatus.INVITED, label: '已邀约' },
  { value: PersonProjectStatus.INTERVIEW_PENDING, label: '待面试' },
  { value: PersonProjectStatus.INTERVIEWED, label: '已面试' },
  { value: PersonProjectStatus.IN_TRIAL, label: '试工中' },
  { value: PersonProjectStatus.TRIAL_PASSED, label: '试工通过' },
  { value: PersonProjectStatus.FAILED, label: '失败' },
  { value: PersonProjectStatus.UNREACHABLE, label: '联系不上' },
]

const failReasonOptions: { value: FailReason; label: string }[] = [
  { value: FailReason.NO_SHOW, label: '爽约' },
  { value: FailReason.REJECTED, label: '拒绝' },
  { value: FailReason.NO_PACKAGE, label: '未购包' },
  { value: FailReason.NO_TRAINING, label: '未到训' },
  { value: FailReason.RESCHEDULED, label: '改约' },
  { value: FailReason.ABANDONED, label: '放弃' },
  { value: FailReason.NOT_QUALIFIED, label: '不符合要求' },
  { value: FailReason.OTHER, label: '其他' },
]

const PersonProjectList: React.FC = () => {
  const [loading, setLoading] = useState(false)
  const [data, setData] = useState<PersonProject[]>([])
  const [total, setTotal] = useState(0)
  const [params, setParams] = useState<PersonProjectQueryParams>({
    skip: 0,
    limit: 20,
  })

  const [selectedRowKeys, setSelectedRowKeys] = useState<React.Key[]>([])
  const [statusModalOpen, setStatusModalOpen] = useState(false)
  const [statusDetailDrawerOpen, setStatusDetailDrawerOpen] = useState(false)
  const [selectedRecord, setSelectedRecord] = useState<PersonProject | null>(null)

  const fetchData = async () => {
    setLoading(true)
    try {
      const result = await personProjectApi.getList(params)
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

  // Handle row selection
  const onSelectChange = (newSelectedRowKeys: React.Key[]) => {
    setSelectedRowKeys(newSelectedRowKeys)
  }

  // Get column definition
  const columns: ColumnsType<PersonProject> = [
    {
      title: 'ID',
      dataIndex: 'id',
      width: 60,
    },
    {
      title: '姓名',
      dataIndex: 'person_name',
      width: 100,
    },
    {
      title: '手机号',
      dataIndex: 'person_phone',
      width: 130,
    },
    {
      title: '项目',
      dataIndex: 'project_name',
      width: 150,
      ellipsis: true,
    },
    {
      title: '状态',
      dataIndex: 'status',
      width: 100,
      render: (status: PersonProjectStatus) => {
        const option = statusOptions.find((o) => o.value === status)
        const color = status === 'trial_passed' ? 'success' :
                     status === 'failed' ? 'error' : undefined
        return <Tag color={color}>{option?.label || status}</Tag>
      },
    },
    {
      title: '更新时间',
      dataIndex: 'updated_at',
      width: 180,
      render: (date: string) => new Date(date).toLocaleString(),
    },
    {
      title: '操作',
      key: 'action',
      width: 200,
      fixed: 'right',
      render: (_: unknown, record: PersonProject) => (
        <Space size="small">
          <Button
            type="link"
            size="small"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
          >
            编辑
          </Button>
          <Button
            type="link"
            size="small"
            onClick={() => handleViewDetail(record)}
          >
            详情
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

  // Handlers
  const handleEdit = (record: PersonProject) => {
    setSelectedRecord(record)
    setStatusModalOpen(true)
  }

  const handleViewDetail = (record: PersonProject) => {
    setSelectedRecord(record)
    setStatusDetailDrawerOpen(true)
  }

  const handleDelete = async (id: number) => {
    try {
      await personProjectApi.delete(id)
      message.success('删除成功')
      fetchData()
    } catch (error) {
      message.error('删除失败')
    }
  }

  const handleBatchStatus = () => {
    if (selectedRowKeys.length === 0) {
      message.warning('请先选择要批量操作的记录')
      return
    }
    setStatusModalOpen(true)
  }

  const handleStatusModalSuccess = () => {
    setStatusModalOpen(false)
    setSelectedRowKeys([])
    fetchData()
  }

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
              placeholder="项目"
              style={{ width: 200 }}
              allowClear
              onChange={(value) => setParams({ ...params, project_id: value ? Number(value) : undefined, skip: 0 })}
            />
            <Select
              placeholder="状态"
              style={{ width: 120 }}
              allowClear
              options={statusOptions}
              onChange={(value) => setParams({ ...params, status: value || undefined, skip: 0 })}
            />
          </Space>
          <Space>
            {selectedRowKeys.length > 0 && (
              <Button onClick={handleBatchStatus}>
                批量状态变更
              </Button>
            )}
            <Button type="primary" icon={<PlusOutlined />}>
              新增人员项目
            </Button>
          </Space>
        </div>

        <Table
          columns={columns}
          dataSource={data}
          rowKey="id"
          loading={loading}
          rowSelection={{
            selectedRowKeys,
            onChange: onSelectChange,
          }}
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

      <BatchStatusModal
        open={statusModalOpen}
        selectedIds={selectedRowKeys as number[]}
        onClose={() => setStatusModalOpen(false)}
        onSuccess={handleStatusModalSuccess}
      />

      <Drawer
        title="状态变更详情"
        placement="right"
        width={600}
        open={statusDetailDrawerOpen}
        onClose={() => setStatusDetailDrawerOpen(false)}
      >
        {selectedRecord && (
          <div>
            <p><strong>人员:</strong> {selectedRecord.person_name}</p>
            <p><strong>手机号:</strong> {selectedRecord.person_phone}</p>
            <p><strong>项目:</strong> {selectedRecord.project_name}</p>
            <p><strong>当前状态:</strong>{' '}
              <Tag color={statusOptions.find(o => o.value === selectedRecord.status) ? 'success' : undefined}>
                {statusOptions.find(o => o.value === selectedRecord.status)?.label || '未知'}
              </Tag>
            </p>
            <p><strong>失败原因:</strong> {selectedRecord.fail_reason || '-'}</p>
            <p><strong>备注:</strong> {selectedRecord.fail_remark || '-'}</p>
          </div>
        )}
      </Drawer>
    </div>
  )
}

export default PersonProjectList
