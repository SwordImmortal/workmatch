import React from 'react'
import { createBrowserRouter, Navigate, Outlet } from 'react-router-dom'
import { useAuthStore } from './store/index'
import LoginPage from './pages/Login'
import AppLayout from './components/layout/AppLayout'

// Protected Route wrapper
const ProtectedRoute: React.FC = () => {
  const token = useAuthStore((state) => state.token)

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
    ],
  },
])
