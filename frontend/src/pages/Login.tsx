import { useState } from 'react'
import { Form, Input, Button, message } from 'antd'
import { UserOutlined, LockOutlined, TeamOutlined } from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import { authApi } from '../services/auth'
import { useAuthStore } from '../store/index'
import type { LoginRequest } from '../services/auth'
import styles from './Login.module.css'

const LoginPage: React.FC = () => {
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()
  const setAuth = useAuthStore((state) => state.setAuth)

  const onFinish = async (values: LoginRequest) => {
    setLoading(true)
    try {
      const response = await authApi.login(values)
      setAuth(response.user, response.access_token)
      message.success('登录成功')
      navigate('/')
    } catch (error: any) {
      message.error(error.response?.data?.detail || '登录失败，请检查用户名和密码')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className={styles.container}>
      {/* 背景装饰 */}
      <div className={styles.background}>
        <div className={styles.shape1} />
        <div className={styles.shape2} />
        <div className={styles.shape3} />
      </div>

      {/* 登录卡片 */}
      <div className={styles.loginCard}>
        {/* Logo 和标题 */}
        <div className={styles.header}>
          <div className={styles.logoWrapper}>
            <TeamOutlined className={styles.logo} />
          </div>
          <h1 className={styles.title}>WorkMatch</h1>
          <p className={styles.subtitle}>蓝领 RPO 招聘管理系统</p>
        </div>

        {/* 登录表单 */}
        <Form
          name="login"
          onFinish={onFinish}
          autoComplete="off"
          layout="vertical"
          className={styles.form}
        >
          <Form.Item
            name="username"
            rules={[{ required: true, message: '请输入用户名' }]}
          >
            <Input
              prefix={<UserOutlined className={styles.inputIcon} />}
              placeholder="用户名"
              size="large"
              className={styles.input}
            />
          </Form.Item>
          <Form.Item
            name="password"
            rules={[{ required: true, message: '请输入密码' }]}
          >
            <Input.Password
              prefix={<LockOutlined className={styles.inputIcon} />}
              placeholder="密码"
              size="large"
              className={styles.input}
            />
          </Form.Item>
          <Form.Item>
            <Button
              type="primary"
              htmlType="submit"
              loading={loading}
              block
              size="large"
              className={styles.loginButton}
            >
              登录
            </Button>
          </Form.Item>
        </Form>

        {/* 底部信息 */}
        <div className={styles.footer}>
          <p>© 2024 WorkMatch. All rights reserved.</p>
        </div>
      </div>
    </div>
  )
}

export default LoginPage
