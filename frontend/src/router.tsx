import React from 'react'
import { createBrowserRouter, Navigate, Outlet } from 'react-router-dom'
import { useAuthStore } from './store/index'
import LoginPage from './pages/Login'
import AppLayout from './components/layout/AppLayout'

// 开发环境模拟用户
const DEV_USER = {
  id: 1,
  username: 'admin',
  name: '管理员',
  role: 'admin',
}

// Protected Route wrapper
const ProtectedRoute: React.FC = () => {
  const token = useAuthStore((state) => state.token)
  const user = useAuthStore((state) => state.user)
  const setAuth = useAuthStore((state) => state.setAuth)

  // 开发环境：如果没有 token，自动设置模拟用户
  if (!token && import.meta.env.DEV) {
    setAuth(DEV_USER, 'dev-mock-token')
    return (
      <AppLayout>
        <Outlet />
      </AppLayout>
    )
  }

  if (!token) {
    return <Navigate to="/login" replace />
  }

  return (
    <AppLayout>
      <Outlet />
    </AppLayout>
  )
}

// Lazy load pages
const Dashboard = React.lazy(() => import('./pages/Dashboard'))
const PersonList = React.lazy(() => import('./pages/person/PersonList'))
const ProjectList = React.lazy(() => import('./pages/project/ProjectList'))
const EnterpriseList = React.lazy(() => import('./pages/enterprise/EnterpriseList'))
const PersonProjectList = React.lazy(() => import('./pages/personProject/PersonProjectList'))
const FollowUpList = React.lazy(() => import('./pages/followUp/FollowUpList'))
const ReminderList = React.lazy(() => import('./pages/reminder/ReminderList'))

export const router = createBrowserRouter([
  {
    path: '/login',
    element: <LoginPage />,
  },
  {
    path: '/',
    element: <ProtectedRoute />,
    children: [
      {
        index: true,
        element: (
          <React.Suspense fallback={<div>Loading...</div>}>
            <Dashboard />
          </React.Suspense>
        ),
      },
      {
        path: 'persons',
        element: (
          <React.Suspense fallback={<div>Loading...</div>}>
            <PersonList />
          </React.Suspense>
        ),
      },
      {
        path: 'projects',
        element: (
          <React.Suspense fallback={<div>Loading...</div>}>
            <ProjectList />
          </React.Suspense>
        ),
      },
      {
        path: 'enterprises',
        element: (
          <React.Suspense fallback={<div>Loading...</div>}>
            <EnterpriseList />
          </React.Suspense>
        ),
      },
      {
        path: 'person-projects',
        element: (
          <React.Suspense fallback={<div>Loading...</div>}>
            <PersonProjectList />
          </React.Suspense>
        ),
      },
      {
        path: 'follow-ups',
        element: (
          <React.Suspense fallback={<div>Loading...</div>}>
            <FollowUpList />
          </React.Suspense>
        ),
      },
      {
        path: 'reminders',
        element: (
          <React.Suspense fallback={<div>Loading...</div>}>
            <ReminderList />
          </React.Suspense>
        ),
      },
      {
        path: 'statistics',
        element: (
          <React.Suspense fallback={<div>Loading...</div>}>
            <Dashboard />
          </React.Suspense>
        ),
      },
    ],
  },
])
