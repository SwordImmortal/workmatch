import { useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { Layout, Menu, Dropdown, Avatar, Space } from 'antd'
import type { MenuProps } from 'antd'
import {
  UserOutlined,
  TeamOutlined,
  ProjectOutlined,
  FileTextOutlined,
  BellOutlined,
  BarChartOutlined,
  LogoutOutlined,
  HomeOutlined,
} from '@ant-design/icons'
import { useAuthStore } from '../../store/index'

const { Sider, Header, Content } = Layout

interface AppLayoutProps {
  children: React.ReactNode
}

const AppLayout: React.FC<AppLayoutProps> = ({ children }) => {
  const [collapsed, setCollapsed] = useState(false)
  const navigate = useNavigate()
  const location = useLocation()
  const { user, logout } = useAuthStore()

  const menuItems: MenuProps['items'] = [
    {
      key: '/',
      icon: <HomeOutlined />,
      label: '首页',
    },
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
  ]

  const handleMenuClick: MenuProps['onClick'] = (e) => {
    navigate(e.key)
  }

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const userMenuItems: MenuProps['items'] = [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: '个人信息',
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: '退出登录',
      onClick: handleLogout,
    },
  ]

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
        <div
          style={{
            height: 64,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: collapsed ? 16 : 20,
            fontWeight: 'bold',
            color: '#1890ff',
            borderBottom: '1px solid #f0f0f0',
          }}
        >
          {collapsed ? 'WM' : 'WorkMatch'}
        </div>
        <Menu
          mode="inline"
          selectedKeys={[location.pathname]}
          items={menuItems}
          onClick={handleMenuClick}
        />
      </Sider>
      <Layout style={{ marginLeft: collapsed ? 80 : 200, transition: 'margin-left 0.2s' }}>
        <Header
          style={{
            background: '#fff',
            padding: '0 24px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            borderBottom: '1px solid #f0f0f0',
          }}
        >
          <h3 style={{ margin: 0 }}>
            {(() => {
              const item = menuItems.find(item => item && 'key' in item && (item as { key: string }).key === location.pathname)
              return item && 'label' in item ? (item as { label: string }).label : 'WorkMatch'
            })()}
          </h3>
          <Dropdown menu={{ items: userMenuItems }} placement="bottomRight">
            <Space style={{ cursor: 'pointer' }}>
              <Avatar icon={<UserOutlined />} />
              <span>{user?.name || '用户'}</span>
            </Space>
          </Dropdown>
        </Header>
        <Content style={{ margin: 16, overflow: 'initial' }}>
          {children}
        </Content>
      </Layout>
    </Layout>
  )
}

export default AppLayout
