import React, { useState, useEffect } from 'react'
import { Modal, Form, Input, InputNumber, Select, message } from 'antd'
import { projectApi, enterpriseApi } from '../../services/project'
import type { Project, ProjectCreate,
 ProjectUpdate } from '../../types/project'

interface ProjectFormModalProps {
  open: boolean
  project?: Project
  onClose: () => void
  onSuccess: () => void
}

const ProjectFormModal: React.FC<ProjectFormModalProps> = ({
  open,
  project,
  onClose,
  onSuccess,
}) => {
  const [form] = Form.useForm()
  const [loading, setLoading] = useState(false)
  const [enterprises, setEnterprises] = useState<{ id: number; name: string }[]>([])

  useEffect(() => {
    if (open) {
      enterpriseApi.getList({ limit: 100 }).then(res => {
        setEnterprises(res.data)
      })
    }
  }, [open])

  useEffect(() => {
    if (open && project) {
      form.setFieldsValue({
        enterprise_id: project.enterprise_id,
        name: project.name,
        job_title: project.job_title,
        salary_range: project.salary_range,
        work_address: project.work_address,
        requirement: project.requirement,
        priority: project.priority,
        unit_price: project.unit_price,
      })
    } else if (open) {
      form.resetFields()
    }
  }, [open, project, form])

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields()
      setLoading(true)
      if (project) {
        await projectApi.updateProject(project.id, values as ProjectUpdate)
        message.success('更新成功')
      } else {
        await projectApi.createProject(values as ProjectCreate)
        message.success('创建成功')
      }
      onSuccess()
    } catch (error) {
      message.error(project ? '更新失败' : '创建失败')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Modal
      title={project ? '编辑项目' : '新增项目'}
      open={open}
      onCancel={onClose}
      onOk={handleSubmit}
      confirmLoading={loading}
      width={600}
    >
      <Form form={form} layout="vertical">
        <Form.Item
          name="enterprise_id"
          label="所属企业"
          rules={[{ required: true, message: '请选择企业' }]}
        >
          <Select
            placeholder="请选择企业"
            options={enterprises.map(e => ({ value: e.id, label: e.name }))}
          />
        </Form.Item>

        <Form.Item
          name="name"
          label="项目名称"
          rules={[{ required: true, message: '请输入项目名称' }]}
        >
          <Input placeholder="请输入项目名称" maxLength={100} />
        </Form.Item>

        <Form.Item
          name="job_title"
          label="招聘岗位"
          rules={[{ required: true, message: '请输入招聘岗位' }]}
        >
          <Input placeholder="请输入招聘岗位" maxLength={100} />
        </Form.Item>

        <Form.Item name="salary_range" label="薪资范围">
          <Input placeholder="如: 8000-12000" maxLength={50} />
        </Form.Item>

        <Form.Item name="work_address" label="工作地点">
          <Input placeholder="请输入工作地点" maxLength={200} />
        </Form.Item>

        <Form.Item name="requirement" label="招聘要求">
          <Input.TextArea placeholder="请输入招聘要求" rows={3} maxLength={500} />
        </Form.Item>

        <Form.Item name="priority" label="优先级" initialValue={0}>
          <InputNumber min={0} max={100} style={{ width: '100%' }} />
        </Form.Item>

        <Form.Item name="unit_price" label="单价（元/间）">
          <InputNumber min={0} precision={2} style={{ width: '100%' }} />
        </Form.Item>
      </Form>
    </Modal>
  )
}

export default ProjectFormModal
