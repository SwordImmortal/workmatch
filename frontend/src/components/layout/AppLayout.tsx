import { useState } from 'react'
import { Layout, Menu, MenuProps } from 'antd'
import {
  UserOutlined,
  TeamOutlined,
  ProjectOutlined,
  FileTextOutlined,
  BellOutlined,
  BarChartOutlined,
  SettingOutlined,
  MenuFoldOutlined,
} from '@ant-design/icons'

const { Sider, Header, Content } = Layout

const menuItems: MenuProps['items'] = [
  {
    key: '/persons',
    icon: <UserOutlined />,
    label: '人员管理',
  },
  {
    key: '/projects',
    icon: <ProjectOutlined />,
    label: '项目管理',
  },
  {
    key: '/enterprises',
    icon: <TeamOutlined />,
    label: '企业管理',
  },
  {
    key: '/follow-ups',
    icon: <FileTextOutlined />,
    label: '跟进记录',
  },
  {
    key: '/reminders',
    icon: <BellOutlined />,
    label: '提醒管理',
  },
  {
    key: '/statistics',
    icon: <BarChartOutlined />,
    label: '数据统计',
  },
  {
    key: '/settings',
    icon: <SettingOutlined />,
    label: '系统设置',
  },
]

const AppLayout: React.FC = () => {
  const [collapsed, setCollapsed] = useState(false)
  const [selectedKey, setSelectedKey] = useState('/persons')

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider
        collapsible
        collapsed={collapsed}
        onCollapse={setCollapsed}
        theme="light"
        style={{
          overflow: 'auto',
          height: '100vh',
          position: 'fixed',
          left: 0,
          top: 0,
          bottom: 0,
        }}
      >
        <div className="logo">
          {collapsed ? 'WM' : 'WorkMatch'}
        </div>
        <Menu
          mode="inline"
          selectedKeys={[selectedKey]}
          items={menuItems}
          onClick={(e) => setSelectedKey(e.key)}
        />
      </Sider>
      <Layout style={{ marginLeft: collapsed ? 80 : 200 }}>
        <Header style={{ background: '#fff', padding: '0 16px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            {collapsed ? null : (
              <MenuFoldOutlined
                style={{ fontSize: '18px', cursor: 'pointer' }}
                onClick={() => setCollapsed(!collapsed)}
              />
            )}
            <h2 style={{ margin: 0 }}>WorkMatch</h2>
          </div>
        </Header>
        <Content style={{ margin: '16px', overflow: 'initial' }}>
          <div style={{ padding: '24px', background: '#fff', borderRadius: '8px' }}>
            <h2>欢迎使用 WorkMatch</h2>
            <p>蓝领 RPO 招聘管理系统</p>
            <p style={{ color: '#999' }}>请从左侧菜单选择功能模块开始操作</p>
          </div>
        </Content>
      </Layout>
    </Layout>
  )
}

export default AppLayout
