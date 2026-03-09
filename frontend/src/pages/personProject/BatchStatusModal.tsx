import { useState } from 'react'
import { Modal, Form, Select, Input, Alert, message } from 'antd'
import type { PersonProjectStatus, FailReason } from '../../types'
import { personProjectApi } from '../../services/personProject'

interface BatchStatusModalProps {
  open: boolean
  selectedIds: number[]
  onClose: () => void
  onSuccess: () => void
}

const statusOptions: { value: PersonProjectStatus; label: string }[] = [
  { value: 'signed_up' as PersonProjectStatus.SIGNED_UP, label: '已报名' },
  { value: 'invited' as PersonProjectStatus.INVITED, label: '已邀约' },
  { value: 'interview_pending' as PersonProjectStatus.INTERVIEW_PENDING, label: '待面试' },
  { value: 'interviewed' as PersonProjectStatus.INTERVIEWED, label: '已面试' },
  { value: 'in_trial' as PersonProjectStatus.IN_TRIAL, label: '试工中' },
  { value: 'trial_passed' as PersonProjectStatus.TRIAL_PASSED, label: '试工通过' },
  { value: 'failed' as PersonProjectStatus.FAILED, label: '失败' },
  { value: 'unreachable' as PersonProjectStatus.UNREACHABLE, label: '联系不上' },
]

const failReasonOptions: { value: FailReason; label: string }[] = [
  { value: 'no_show' as FailReason.NO_SHOW, label: '爽约' },
  { value: 'rejected' as FailReason.REJECTED, label: '拒绝' },
  { value: 'no_package' as FailReason.NO_PACKAGE, label: '未购包' },
  { value: 'no_training' as FailReason.NO_TRAINING, label: '未到训' },
  { value: 'rescheduled' as FailReason.RESCHEDULED, label: '改约' },
  { value: 'abandoned' as FailReason.ABANDONED, label: '放弃' },
  { value: 'not_qualified' as FailReason.NOT_QUALIFIED, label: '不符合要求' },
  { value: 'other' as FailReason.OTHER, label: '其他' },
]

const BatchStatusModal: React.FC<BatchStatusModalProps> = ({
  open,
  selectedIds,
  onClose,
  onSuccess,
}) => {
  const [form] = Form.useForm()
  const [loading, setLoading] = useState(false)
  const [targetStatus, setTargetStatus] = useState<PersonProjectStatus | null>(null)

  const handleStatusChange = (status: PersonProjectStatus) => {
    setTargetStatus(status)
    form.setFieldsValue({ status })
    if (status !== 'failed') {
      form.setFieldsValue({ fail_reason: undefined, fail_remark: undefined })
    }
  }

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields()
      setLoading(true)
      const result = await personProjectApi.batchChangeStatus({
        person_project_ids: selectedIds,
        status: values.status,
        fail_reason: values.fail_reason,
        fail_remark: values.fail_remark,
      })
      message.success(`成功更新 ${result.success_count} 条， 失败 ${result.fail_count} 条`)
      if (result.fail_count > 0) {
        console.warn('Failed items:', result.errors)
      }
      onSuccess()
    } catch (error) {
      message.error('批量更新失败')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Modal
      title={`批量状态变更（已选择 ${selectedIds.length} 条记录）`}
      open={open}
      onCancel={onClose}
      onOk={handleSubmit}
      confirmLoading={loading}
      width={500}
    >
      <Alert
        message="请确保所选记录的状态流转符合规则，不合规的记录将被跳过"
        type="info"
        showIcon
        style={{ marginBottom: 16 }}
      />
      <Form form={form} layout="vertical">
        <Form.Item
          name="status"
          label="目标状态"
          rules={[{ required: true, message: '请选择目标状态' }]}
        >
          <Select
            placeholder="请选择目标状态"
            options={statusOptions}
            onChange={handleStatusChange}
          />
        </Form.Item>

        {targetStatus === 'failed' && (
          <>
            <Form.Item
              name="fail_reason"
              label="失败原因"
              rules={[{ required: true, message: '请选择失败原因' }]}
            >
              <Select
                placeholder="请选择失败原因"
                options={failReasonOptions}
              />
            </Form.Item>

            <Form.Item
              name="fail_remark"
              label="备注"
            >
              <Input.TextArea
                placeholder="请输入备注（可选）"
                rows={2}
                maxLength={200}
              />
            </Form.Item>
          </>
        )}
      </Form>
    </Modal>
  )
}

export default BatchStatusModal
