import { Routes, Route, Navigate, useLocation } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import AdminLayout from './layouts/AdminLayout'
import Login from './pages/Login'

// 页面组件
import Dashboard from './pages/Dashboard'
import Chat from './pages/Chat'
import Prompts from './pages/Prompts'
import Knowledge from './pages/Knowledge'
import Models from './pages/Models'
import Monitor from './pages/Monitor'

// 路由守卫
function PrivateRoute({ children }) {
  const token = localStorage.getItem('token')
  const location = useLocation()

  if (!token) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  return children
}

function App() {
  return (
    <>
      <Toaster position="top-right" />
      <Routes>
        {/* 登录页面 */}
        <Route path="/login" element={<Login />} />

        {/* 管理后台路由（需要登录） */}
        <Route
          path="/admin"
          element={
            <PrivateRoute>
              <AdminLayout />
            </PrivateRoute>
          }
        >
          <Route index element={<Dashboard />} />
          <Route path="chat" element={<Chat />} />
          <Route path="prompts" element={<Prompts />} />
          <Route path="knowledge" element={<Knowledge />} />
          <Route path="models" element={<Models />} />
          <Route path="monitor" element={<Monitor />} />
        </Route>

        {/* 重定向 */}
        <Route path="/" element={<Navigate to="/admin" replace />} />
        <Route path="*" element={<Navigate to="/admin" replace />} />
      </Routes>
    </>
  )
}

export default App
