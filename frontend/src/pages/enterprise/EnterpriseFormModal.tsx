import React, { useState, useEffect } from 'react'
import { Modal, Form, Input, message } from 'antd'
import { enterpriseApi } from '../../services/project'
import type { Enterprise, EnterpriseCreate, EnterpriseUpdate } from '../../types/project'

interface EnterpriseFormModalProps {
  open: boolean
  enterprise?: Enterprise
  onClose: () => void
  onSuccess: () => void
}

const EnterpriseFormModal: React.FC<EnterpriseFormModalProps> = ({
  open,
  enterprise,
  onClose,
  onSuccess,
}) => {
  const [form] = Form.useForm()
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (open && enterprise) {
      form.setFieldsValue({
        name: enterprise.name,
        contact_name: enterprise.contact_name,
        contact_phone: enterprise.contact_phone,
        address: enterprise.address,
        description: enterprise.description,
      })
    } else if (open) {
      form.resetFields()
    }
  }, [open, enterprise, form])

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields()
      setLoading(true)
      if (enterprise) {
        await enterpriseApi.update(enterprise.id, values as EnterpriseUpdate)
        message.success('更新成功')
      } else {
        await enterpriseApi.create(values as EnterpriseCreate)
        message.success('创建成功')
      }
      onSuccess()
    } catch (error) {
      message.error(enterprise ? '更新失败' : '创建失败')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Modal
      title={enterprise ? '编辑企业' : '新增企业'}
      open={open}
      onCancel={onClose}
      onOk={handleSubmit}
      confirmLoading={loading}
      width={500}
    >
      <Form form={form} layout="vertical">
        <Form.Item
          name="name"
          label="企业名称"
          rules={[{ required: true, message: '请输入企业名称' }]}
        >
          <Input placeholder="请输入企业名称" maxLength={100} />
        </Form.Item>

        <Form.Item name="contact_name" label="联系人">
          <Input placeholder="请输入联系人姓名" maxLength={50} />
        </Form.Item>

        <Form.Item name="contact_phone" label="联系电话">
          <Input placeholder="请输入联系电话" maxLength={20} />
        </Form.Item>

        <Form.Item name="address" label="企业地址">
          <Input placeholder="请输入企业地址" maxLength={200} />
        </Form.Item>

        <Form.Item name="description" label="企业描述">
          <Input.TextArea placeholder="请输入企业描述" rows={3} />
        </Form.Item>
      </Form>
    </Modal>
  )
}

export default EnterpriseFormModal
