import React, { useState, useEffect } from 'react'
import { Card, Row, Col, Statistic, Progress, Spin, Empty, Table, Tag } from 'antd'
import {
  UserOutlined,
  ClockCircleOutlined,
  RiseOutlined,
  CalendarOutlined,
} from '@ant-design/icons'
import { statisticsApi } from '../services/statistics'
import type { OverviewStats } from '../types/statistics'

const statusLabels: Record<string, string> = {
  signed_up: '已报名',
  invited: '已邀约',
  interview_pending: '待面试',
  interviewed: '已面试',
  in_trial: '试工中',
  trial_passed: '试工通过',
  failed: '失败',
  unreachable: '联系不上',
}

const statusColors: Record<string, string> = {
  signed_up: '#1890ff',
  invited: '#722ed1',
  interview_pending: '#faad14',
  interviewed: '#13c2c2',
  in_trial: '#eb2f96',
  trial_passed: '#52c41a',
  failed: '#ff4d4f',
  unreachable: '#8c8c8c',
}

const Dashboard: React.FC = () => {
  const [loading, setLoading] = useState(false)
  const [data, setData] = useState<OverviewStats | null>(null)

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true)
      try {
        const result = await statisticsApi.getOverview()
        setData(result)
      } catch (error) {
        console.error('Failed to fetch overview stats:', error)
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [])

  const projectColumns = [
    {
      title: '项目名称',
      dataIndex: 'project_name',
      key: 'project_name',
    },
    {
      title: '总人数',
      dataIndex: 'total',
      key: 'total',
      render: (total: number) => total.toLocaleString(),
    },
    {
      title: '通过人数',
      dataIndex: 'passed',
      key: 'passed',
      render: (passed: number) => passed.toLocaleString(),
    },
    {
      title: '通过率',
      key: 'percentage',
      render: (_: unknown, record: { total: number; passed: number }) => {
        const rate = record.total > 0 ? (record.passed / record.total) * 100 : 0
        return `${rate.toFixed(1)}%`
      },
    },
  ]

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '40px 0' }}>
        <Spin size="large" />
      </div>
    )
  }

  if (!data) {
    return <Empty description="暂无数据" />
  }

  return (
    <div>
      <h2 style={{ marginBottom: 24 }}>数据概览</h2>
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="总人员"
              value={data.total_persons || 0}
              prefix={<UserOutlined style={{ color: '#1890ff' }} />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="今日新增"
              value={data.today_new || 0}
              prefix={<RiseOutlined style={{ color: '#52c41a' }} />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="本周新增"
              value={data.week_new || 0}
              prefix={<CalendarOutlined style={{ color: '#13c2c2' }} />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="待处理提醒"
              value={data.pending_reminders || 0}
              prefix={<ClockCircleOutlined style={{ color: '#faad14' }} />}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={12}>
          <Card title="转化率">
            <div style={{ textAlign: 'center' }}>
              <Progress
                type="circle"
                percent={Math.round((data.conversion_rate || 0) * 100)}
                format={(percent) => `${percent}%`}
                strokeColor="#52c41a"
              />
              <div style={{ marginTop: 16, color: '#8c8c8c' }}>
                整体转化率
              </div>
            </div>
          </Card>
        </Col>
        <Col span={12}>
          <Card title="项目统计">
            {data.project_stats && data.project_stats.length > 0 ? (
              <Table
                columns={projectColumns}
                dataSource={data.project_stats}
                rowKey="project_id"
                pagination={false}
                size="small"
              />
            ) : (
              <Empty description="暂无项目数据" />
            )}
          </Card>
        </Col>
      </Row>

      <Row gutter={16}>
        <Col span={24}>
          <Card title="状态分布">
            {data.status_breakdown && Object.keys(data.status_breakdown).length > 0 ? (
              <div>
                {Object.entries(data.status_breakdown).map(([status, count]) => (
                  <div key={status} style={{ marginBottom: 8 }}>
                    <Tag color={statusColors[status] || 'default'}>
                      {statusLabels[status] || status}
                    </Tag>
                    <Progress
                      percent={Math.round((count / data.total_persons) * 100)}
                      size="small"
                      style={{ marginTop: 8 }}
                    />
                  </div>
                ))}
              </div>
            ) : (
              <Empty description="暂无状态分布数据" />
            )}
          </Card>
        </Col>
      </Row>
    </div>
  )
}

export default Dashboard
