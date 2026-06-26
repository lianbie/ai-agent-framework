import { useState, useEffect } from 'react'
import { Link, useLocation, Outlet, useNavigate } from 'react-router-dom'
import {
  LayoutDashboard,
  MessageSquare,
  FileText,
  Database,
  Settings,
  Activity,
  ChevronLeft,
  ChevronRight,
  Bot,
  LogOut,
  User,
  Bell,
  Search
} from 'lucide-react'
import toast from 'react-hot-toast'

const menuItems = [
  { path: '/admin', icon: LayoutDashboard, label: '仪表盘' },
  { path: '/admin/chat', icon: MessageSquare, label: '对话测试' },
  { path: '/admin/prompts', icon: FileText, label: '提示词管理' },
  { path: '/admin/knowledge', icon: Database, label: '知识库管理' },
  { path: '/admin/models', icon: Settings, label: '模型配置' },
  { path: '/admin/monitor', icon: Activity, label: '系统监控' },
]

export default function AdminLayout() {
  const [collapsed, setCollapsed] = useState(false)
  const [user, setUser] = useState(null)
  const location = useLocation()
  const navigate = useNavigate()

  useEffect(() => {
    const userStr = localStorage.getItem('user')
    if (userStr) {
      try { setUser(JSON.parse(userStr)) } catch (e) {}
    }
  }, [])

  const handleLogout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    toast.success('已退出登录')
    navigate('/login')
  }

  const currentPage = menuItems.find(item => item.path === location.pathname)

  return (
    <div className="flex h-screen bg-gray-50">
      {/* 侧边栏 */}
      <aside className={`bg-white shadow-lg transition-all duration-300 flex flex-col ${collapsed ? 'w-16' : 'w-64'}`}>
        {/* Logo */}
        <div className="h-16 flex items-center justify-center border-b">
          <Bot className="h-8 w-8 text-primary-600" />
          {!collapsed && (
            <span className="ml-2 text-lg font-semibold gradient-text">AI客服管理</span>
          )}
        </div>

        {/* 菜单 */}
        <nav className="mt-4 flex-1">
          {menuItems.map((item) => {
            const Icon = item.icon
            const isActive = location.pathname === item.path
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center px-4 py-3 transition-colors ${
                  isActive
                    ? 'bg-primary-50 text-primary-600 border-r-4 border-primary-600'
                    : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                }`}
              >
                <Icon className="h-5 w-5 flex-shrink-0" />
                {!collapsed && <span className="ml-3">{item.label}</span>}
              </Link>
            )
          })}
        </nav>

        {/* 用户信息 */}
        <div className="border-t p-4">
          {user && (
            <div className={`flex items-center ${collapsed ? 'justify-center' : 'justify-between'}`}>
              <div className="flex items-center">
                <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
                  <User className="h-4 w-4 text-primary-600" />
                </div>
                {!collapsed && (
                  <div className="ml-3">
                    <p className="text-sm font-medium text-gray-700">{user.nickname || user.username}</p>
                    <p className="text-xs text-gray-400">{user.role}</p>
                  </div>
                )}
              </div>
              {!collapsed && (
                <button onClick={handleLogout} className="p-2 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors">
                  <LogOut className="h-4 w-4" />
                </button>
              )}
            </div>
          )}
        </div>

        {/* 折叠按钮 */}
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="p-3 border-t text-gray-400 hover:text-gray-600 hover:bg-gray-50 transition-colors"
        >
          {collapsed ? <ChevronRight className="h-5 w-5 mx-auto" /> : <ChevronLeft className="h-5 w-5 mx-auto" />}
        </button>
      </aside>

      {/* 主内容区 */}
      <main className="flex-1 flex flex-col overflow-hidden">
        {/* 顶部Header */}
        <header className="h-16 bg-white border-b flex items-center justify-between px-6">
          <div className="flex items-center gap-4">
            <h2 className="text-lg font-semibold text-gray-800">
              {currentPage?.label || '管理后台'}
            </h2>
          </div>
          <div className="flex items-center gap-4">
            <button className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors">
              <Search className="h-5 w-5" />
            </button>
            <button className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors relative">
              <Bell className="h-5 w-5" />
              <span className="absolute top-1 right-1 w-2 h-2 bg-primary-600 rounded-full"></span>
            </button>
          </div>
        </header>

        {/* 内容区 */}
        <div className="flex-1 overflow-auto p-6 bg-gray-50">
          <Outlet />
        </div>
      </main>
    </div>
  )
}
