import { useState, useEffect } from 'react'
import { Table, Card, Button, Space, Modal, Form, Input, DatePicker, message, Empty, Tag } from 'antd'
import { PlusOutlined, MessageOutlined } from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import type { FollowUp } from '../../types/followUp'
import { followUpApi } from '../../services/followUp'

interface FollowUpListProps {
  personProjectId?: number
  personId?: number
  projectId?: number
}

const FollowUpList: React.FC<FollowUpListProps> = ({
  personProjectId,
  personId,
  projectId,
}) => {
  const [loading, setLoading] = useState(false)
  const [data, setData] = useState<FollowUp[]>([])
  const [modalOpen, setModalOpen] = useState(false)
  const [form] = Form.useForm()

  const fetchData = async () => {
    if (!personProjectId && !personId && !projectId) return
    setLoading(true)
    try {
      let data
      if (personProjectId) {
        data = await followUpApi.getByPersonProject(personProjectId)
      } else if (personId) {
        data = await followUpApi.getByPerson(personId)
      } else if (projectId) {
        data = await followUpApi.getByProject(projectId)
      }
      setData(data || [])
    } catch (error) {
      message.error('获取跟进记录失败')
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
      await followUpApi.create({
        ...values,
        person_project_id: personProjectId,
      })
      message.success('添加成功')
      setModalOpen(false)
      form.resetFields()
      fetchData()
    } catch (error) {
      message.error('添加失败')
    }
  }

  const columns: ColumnsType<FollowUp> = [
    {
      title: '跟进内容',
      dataIndex: 'content',
      ellipsis: true,
    },
    {
      title: '下次跟进时间',
      dataIndex: 'next_follow_time',
      width: 180,
      render: (date: string) => date ? new Date(date).toLocaleString() : '-',
    },
    {
      title: '创建人',
      dataIndex: 'created_by_name',
      width: 100,
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      width: 180,
      render: (date: string) => new Date(date).toLocaleString(),
    },
  ]

  return (
    <Card
      title="跟进记录"
      extra={
        personProjectId && (
          <Button
            type="primary"
            size="small"
            icon={<PlusOutlined />}
            onClick={() => setModalOpen(true)}
          >
            添加跟进
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
        locale={{ emptyText: '暂无跟进记录' }}
        size="small"
      />

      <Modal
        title="添加跟进记录"
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
            label="跟进内容"
            rules={[{ required: true, message: '请输入跟进内容' }]}
          >
            <Input.TextArea
              placeholder="请输入跟进内容"
              rows={3}
              maxLength={500}
            />
          </Form.Item>

          <Form.Item
            name="next_follow_time"
            label="下次跟进时间"
          >
            <DatePicker
              showTime
              style={{ width: '100%' }}
              placeholder="选择下次跟进时间"
            />
          </Form.Item>
        </Form>
      </Modal>
    </Card>
  )
}

export default FollowUpList
