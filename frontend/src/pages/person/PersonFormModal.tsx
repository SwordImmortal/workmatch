import { useState } from 'react'
import { Modal, Form, Input, Select, InputNumber, Switch, message } from 'antd'
import type { FormProps } from 'antd'
import { personApi } from '../../services/person'
import type { Person, PersonCreate, PersonUpdate } from '../../types/person'
import type { Gender,
 Source } from '../../types'

interface PersonFormModalProps {
  open: boolean
  person?: Person
  onClose: () => void
  onSuccess: () => void
}

const PersonFormModal: React.FC<PersonFormModalProps> = ({
  open,
  person,
  onClose,
  onSuccess,
}) => {
  const [loading, setLoading] = useState(false)
  const [form] = Form.useForm()
  const isEdit = !!person

  const handleSubmit = async (values: PersonCreate | PersonUpdate) => {
    setLoading(true)
    try {
      if (isEdit) {
        await personApi.update(person.id, values)
        message.success('更新成功')
      } else {
        await personApi.create(values as PersonCreate)
        message.success('创建成功')
      }
      onSuccess()
      onClose()
    } catch (error: any) {
        message.error(error.response?.data?.message || '操作失败')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Modal
      title={isEdit ? '编辑人员' : '新增人员'}
      open={open}
      onCancel={onClose}
      onOk={() => form.submit()}
      confirmLoading={loading}
      width={600}
    >
      <Form
        form={form}
        layout="vertical"
        onFinish={handleSubmit}
        initialValues={{
          gender: 'unknown',
          source: 'other',
          reusable: true,
          ...person,
        }}
      >
        <Form.Item
          name="name"
          label="姓名"
          rules={[{ required: true, message: '请输入姓名' }]}
        >
          <Input placeholder="请输入姓名" maxLength={50} />
        </Form.Item>

        <Form.Item
          name="phone"
          label="手机号"
          rules={[
            { required: true, message: '请输入手机号' },
            { pattern: /^1[3-9]\d{9}$/, message: '手机号格式不正确' },
          ]}
        >
          <Input placeholder="请输入11位手机号" maxLength={11} />
        </Form.Item>

        <Form.Item name="city" label="城市" rules={[{ required: true, message: '请输入城市' }]}>
          <Input placeholder="请输入城市" maxLength={50} />
        </Form.Item>

        <Form.Item name="id_card" label="身份证号">
          <Input placeholder="请输入18位身份证号" maxLength={18} />
        </Form.Item>

        <Form.Item name="gender" label="性别">
          <Select
            options={[
              { value: 'male', label: '男' },
              { value: 'female', label: '女' },
              { value: 'unknown', label: '未知' },
            ]}
          />
        </Form.Item>

        <Form.Item name="age" label="年龄">
          <InputNumber min={0} max={150} placeholder="请输入年龄" style={{ width: '100%' }} />
        </Form.Item>

        <Form.Item name="source" label="来源渠道">
          <Select
            options={[
              { value: 'boss', label: 'BOSS直聘' },
              { value: 'kuaishou', label: '快手' },
              { value: 'douyin', label: '抖音' },
              { value: '58', label: '58同城' },
              { value: 'referral', label: '内推' },
              { value: 'other', label: '其他' },
            ]}
          />
        </Form.Item>

        <Form.Item name="address" label="详细地址">
          <Input.TextArea placeholder="请输入详细地址" rows={2} maxLength={200} />
        </Form.Item>

        <Form.Item name="remark" label="备注">
          <Input.TextArea placeholder="请输入备注" rows={2} />
        </Form.Item>

        <Form.Item name="reusable" label="可复用" valuePropName="checked">
          <Switch checkedChildren="是" unCheckedChildren="否" />
        </Form.Item>
      </Form>
    </Modal>
  )
}

export default PersonFormModal
