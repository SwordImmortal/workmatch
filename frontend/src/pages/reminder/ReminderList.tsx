import React, { useState, useEffect } from 'react'
import { Table, Card, Button, Space, Modal, Form, Input, DatePicker, message, Tag, Popconfirm } from 'antd'
import { PlusOutlined, BellOutlined, CheckOutlined, DeleteOutlined } from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import type { Reminder, ReminderCreate } from '../../types/reminder'
import { reminderApi } from '../../services/reminder'

interface ReminderListProps {
  personProjectId?: number
  personId?: number
  projectId?: number
}

const ReminderList: React.FC<ReminderListProps> = ({
  personProjectId,
  personId,
  projectId,
}) => {
  const [loading, setLoading] = useState(false)
  const [data, setData] = useState<Reminder[]>([])
  const [modalOpen, setModalOpen] = useState(false)
  const [form] = Form.useForm()

  const fetchData = async () => {
    if (!personProjectId && !personId && !projectId) return
    setLoading(true)
    try {
      let data
      if (personProjectId) {
        data = await reminderApi.getByPersonProject(personProjectId)
      } else if (personId) {
        data = await reminderApi.getByPerson(personId)
      } else if (projectId) {
        data = await reminderApi.getByProject(projectId)
      }
      setData(data || [])
    } catch (error) {
      message.error('获取提醒记录失败')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [personProjectId, personId, projectId])

  const handleCreate = async () => {
    try {
      const values = await form.validateFields()
      const createData: ReminderCreate = {
        person_project_id: personProjectId!,
        reminder_time: values.reminder_time.toISOString(),
        content: values.content,
      }
      await reminderApi.create(createData)
      message.success('添加成功')
      setModalOpen(false)
      form.resetFields()
      fetchData()
    } catch (error) {
      message.error('添加失败')
    }
  }

  const handleComplete = async (id: number) => {
    try {
      await reminderApi.complete(id)
      message.success('已标记完成')
      fetchData()
    } catch (error) {
      message.error('操作失败')
    }
  }

  const handleDelete = async (id: number) => {
    try {
      await reminderApi.delete(id)
      message.success('删除成功')
      fetchData()
    } catch (error) {
      message.error('删除失败')
    }
  }

  const columns: ColumnsType<Reminder> = [
    {
      title: '提醒内容',
      dataIndex: 'content',
      ellipsis: true,
    },
    {
      title: '提醒时间',
      dataIndex: 'reminder_time',
      width: 180,
      render: (date: string) => new Date(date).toLocaleString(),
    },
    {
      title: '状态',
      dataIndex: 'is_completed',
      width: 100,
      render: (completed: boolean) => (
        <Tag color={completed ? 'success' : 'processing'}>
          {completed ? '已完成' : '待处理'}
        </Tag>
      ),
    },
    {
      title: '创建人',
      dataIndex: 'created_by_name',
      width: 100,
    },
    {
      title: '操作',
      width: 120,
      render: (_, record) => (
        <Space size="small">
          {!record.is_completed && (
            <Button
              type="link"
              size="small"
              icon={<CheckOutlined />}
              onClick={() => handleComplete(record.id)}
            >
              完成
            </Button>
          )}
          <Popconfirm
            title="确定删除此提醒？"
            onConfirm={() => handleDelete(record.id)}
          >
            <Button type="link" size="small" danger icon={<DeleteOutlined />} />
          </Popconfirm>
        </Space>
      ),
    },
  ]

  return (
    <Card
      title="提醒记录"
      extra={
        personProjectId && (
          <Button
            type="primary"
            size="small"
            icon={<PlusOutlined />}
            onClick={() => setModalOpen(true)}
          >
            添加提醒
          </Button>
        )
      }
    >
      <Table
        columns={columns}
        dataSource={data}
        rowKey="id"
        loading={loading}
        pagination={false}
        locale={{ emptyText: '暂无提醒记录' }}
        size="small"
      />

      <Modal
        title="添加提醒"
        open={modalOpen}
        onCancel={() => {
          setModalOpen(false)
          form.resetFields()
        }}
        onOk={handleCreate}
      >
        <Form form={form} layout="vertical">
          <Form.Item
            name="content"
            label="提醒内容"
            rules={[{ required: true, message: '请输入提醒内容' }]}
          >
            <Input.TextArea
              placeholder="请输入提醒内容"
              rows={3}
              maxLength={500}
            />
          </Form.Item>

          <Form.Item
            name="reminder_time"
            label="提醒时间"
            rules={[{ required: true, message: '请选择提醒时间' }]}
          >
            <DatePicker
              showTime
              style={{ width: '100%' }}
              placeholder="选择提醒时间"
            />
          </Form.Item>
        </Form>
      </Modal>
    </Card>
  )
}

export default ReminderList
