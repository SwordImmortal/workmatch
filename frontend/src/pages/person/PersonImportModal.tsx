import { useState } from 'react'
import { Modal, Upload, Button, Alert, Table, message } from 'antd'
import { UploadOutlined, DownloadOutlined, InboxOutlined } from '@ant-design/icons'
import type { UploadFile } from 'antd/es/upload/interface'
import { personApi } from '../../services/person'

interface PersonImportModalProps {
  open: boolean
  onClose: () => void
  onSuccess: () => void
}

interface ImportError {
  row: number
  field: string | null
  message: string
}

const PersonImportModal: React.FC<PersonImportModalProps> = ({
  open,
  onClose,
  onSuccess,
}) => {
  const [fileList, setFileList] = useState<UploadFile[]>([])
  const [uploading, setUploading] = useState(false)
  const [result, setResult] = useState<{
    success_count: number
    fail_count: number
    total: number
    errors: ImportError[]
  } | null>(null)

  const handleDownloadTemplate = () => {
    personApi.downloadTemplate()
  }

  const handleUpload = async () => {
    if (fileList.length === 0) {
      message.warning('请先选择文件')
      return
    }

    setUploading(true)
    setResult(null)

    try {
      const file = fileList[0].originFileObj as File
      const importResult = await personApi.importExcel(file)
      setResult(importResult)

      if (importResult.fail_count === 0) {
        message.success(`导入成功，共 ${importResult.success_count} 条记录`)
        onSuccess()
      } else {
        message.warning(`部分导入成功，成功 ${importResult.success_count} 条，失败 ${importResult.fail_count} 条`)
      }
    } catch (error: unknown) {
      const err = error as { response?: { data?: { detail?: string } } }
      message.error(err.response?.data?.detail || '导入失败')
    } finally {
      setUploading(false)
    }
  }

  const handleClose = () => {
    setFileList([])
    setResult(null)
    onClose()
  }

  const errorColumns = [
    {
      title: '行号',
      dataIndex: 'row',
      width: 80,
    },
    {
      title: '字段',
      dataIndex: 'field',
      width: 100,
    },
    {
      title: '错误信息',
      dataIndex: 'message',
    },
  ]

  return (
    <Modal
      title="批量导入人员"
      open={open}
      onCancel={handleClose}
      width={700}
      footer={[
        <Button key="cancel" onClick={handleClose}>
          取消
        </Button>,
        <Button
          key="download"
          icon={<DownloadOutlined />}
          onClick={handleDownloadTemplate}
        >
          下载模板
        </Button>,
        <Button
          key="upload"
          type="primary"
          loading={uploading}
          onClick={handleUpload}
        >
          确认导入
        </Button>,
      ]}
    >
      <Alert
        message="导入说明"
        description={
          <div>
            <p>1. 请先下载模板文件</p>
            <p>2. 按照模板格式填写人员信息</p>
            <p>3. 单次最多导入 1000 行数据</p>
            <p>4. 手机号重复的行将被跳过</p>
          </div>
        }
        type="info"
        showIcon
        style={{ marginBottom: 16 }}
      />

      <Upload.Dragger
        accept=".xlsx,.xls"
        fileList={fileList}
        beforeUpload={() => false}
        onChange={(info) => {
          setFileList(info.fileList.slice(-1))
        }}
        maxCount={1}
      >
        <p className="ant-upload-drag-icon">
          <InboxOutlined />
        </p>
        <p className="ant-upload-text">点击或拖拽文件到此区域上传</p>
        <p className="ant-upload-hint">支持 .xlsx 或 .xls 格式</p>
      </Upload.Dragger>

      {result && result.errors.length > 0 && (
        <div style={{ marginTop: 16 }}>
          <Alert
            message={`导入结果: 成功 ${result.success_count} 条, 失败 ${result.fail_count} 条`}
            type={result.fail_count > 0 ? 'warning' : 'success'}
            showIcon
            style={{ marginBottom: 8 }}
          />
          <Table
            columns={errorColumns}
            dataSource={result.errors}
            rowKey={(record: ImportError) => `${record.row}-${record.field}`}
            pagination={false}
            size="small"
            scroll={{ y: 200 }}
          />
        </div>
      )}
    </Modal>
  )
}

export default PersonImportModal
