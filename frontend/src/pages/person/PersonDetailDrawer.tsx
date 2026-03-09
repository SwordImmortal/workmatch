import { useState, useEffect } from 'react'
import { Drawer, Descriptions, Tag, Table, Empty, Spin } from 'antd'
import { personApi } from '../../services/person'
import type { Person } from '../../types/person'
import type { PersonProjectStatus } from '../../types'

interface PersonDetailDrawerProps {
  open: boolean
  personId: number | null
  onClose: () => void
}

const statusMap: Record<PersonProjectStatus, { label: string; color: string }> = {
  signed_up: { label: '已报名', color: 'default' },
  invited: { label: '已邀约', color: 'blue' },
  interview_pending: { label: '待面试', color: 'orange' },
  interviewed: { label: '已面试', color: 'cyan' },
  in_trial: { label: '试工中', color: 'purple' },
  trial_passed: { label: '试工通过', color: 'green' },
  failed: { label: '失败', color: 'red' },
  unreachable: { label: '联系不上', color: 'default' },
}

const PersonDetailDrawer: React.FC<PersonDetailDrawerProps> = ({
  open,
  personId,
  onClose,
}) => {
  const [loading, setLoading] = useState(false)
  const [person, setPerson] = useState<Person | null>(null)
  const [projects, setProjects] = useState<any[]>([])

  useEffect(() => {
    if (open && personId) {
      fetchData()
    }
  }, [open, personId])

  const fetchData = async () => {
    setLoading(true)
    try {
      const data = await personApi.getWithProjects(personId!)
      setPerson(data)
      setProjects((data as any).projects || [])
    } catch (error) {
      console.error('Failed to fetch person:', error)
    } finally {
      setLoading(false)
    }
  }

  const genderMap: Record<string, string> = {
    male: '男',
    female: '女',
    unknown: '未知',
  }

  const sourceMap: Record<string, string> = {
    boss: 'BOSS直聘',
    kuaishou: '快手',
    douyin: '抖音',
    '58': '58同城',
    referral: '内推',
    other: '其他',
  }

  const projectColumns = [
    {
      title: '项目名称',
      dataIndex: 'project_name',
      key: 'project_name',
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: PersonProjectStatus) => {
        const item = statusMap[status]
        return item ? <Tag color={item.color}>{item.label}</Tag> : status
      },
    },
    {
      title: '负责人',
      dataIndex: 'owner_name',
      key: 'owner_name',
    },
    {
      title: '更新时间',
      dataIndex: 'updated_at',
      key: 'updated_at',
      render: (date: string) => new Date(date).toLocaleString(),
    },
  ]

  return (
    <Drawer
      title="人员详情"
      placement="right"
      width={600}
      open={open}
      onClose={onClose}
    >
      {loading ? (
        <div style={{ textAlign: 'center', padding: 40 }}>
          <Spin />
        </div>
      ) : person ? (
        <>
          <Descriptions column={2} bordered>
            <Descriptions.Item label="姓名">{person.name}</Descriptions.Item>
            <Descriptions.Item label="手机号">{person.phone}</Descriptions.Item>
            <Descriptions.Item label="城市">{person.city}</Descriptions.Item>
            <Descriptions.Item label="性别">
              {genderMap[person.gender] || person.gender}
            </Descriptions.Item>
            <Descriptions.Item label="年龄">{person.age || '-'}</Descriptions.Item>
            <Descriptions.Item label="来源">
              {sourceMap[person.source] || person.source}
            </Descriptions.Item>
            <Descriptions.Item label="身份证号">{person.id_card || '-'}</Descriptions.Item>
            <Descriptions.Item label="详细地址">{person.address || '-'}</Descriptions.Item>
            <Descriptions.Item label="可复用" span={2}>
              <Tag color={person.reusable ? 'green' : 'default'}>
                {person.reusable ? '是' : '否'}
              </Tag>
            </Descriptions.Item>
            <Descriptions.Item label="备注" span={2}>
              {person.remark || '-'}
            </Descriptions.Item>
          </Descriptions>

          <h4 style={{ marginTop: 24, marginBottom: 16 }}>项目状态</h4>
          <Table
            columns={projectColumns}
            dataSource={projects}
            rowKey="id"
            pagination={false}
            locale={{ emptyText: '暂无项目记录' }}
          />
        </>
      ) : (
        <Empty description="未找到人员信息" />
      )}
    </Drawer>
  )
}

export default PersonDetailDrawer
