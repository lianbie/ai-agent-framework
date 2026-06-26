import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import {
  MessageSquare,
  FileText,
  Database,
  Settings,
  TrendingUp,
  Clock,
  AlertCircle,
  CheckCircle
} from 'lucide-react'
import { monitorApi } from '../api'

export default function Dashboard() {
  const [stats, setStats] = useState(null)
  const [health, setHealth] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const [statsData, healthData] = await Promise.all([
        monitorApi.getStats(),
        monitorApi.healthCheck()
      ])
      setStats(statsData)
      setHealth(healthData)
    } catch (error) {
      console.error('加载数据失败:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="loading-spinner"></div>
      </div>
    )
  }

  const statCards = [
    {
      title: '总对话数',
      value: stats?.total_conversations || 0,
      icon: MessageSquare,
      color: 'bg-blue-500',
      link: '/admin/chat'
    },
    {
      title: '知识库文档',
      value: stats?.total_documents || 0,
      icon: Database,
      color: 'bg-green-500',
      link: '/admin/knowledge'
    },
    {
      title: '提示词数量',
      value: stats?.total_prompts || 0,
      icon: FileText,
      color: 'bg-purple-500',
      link: '/admin/prompts'
    },
    {
      title: '模型配置',
      value: stats?.total_models || 0,
      icon: Settings,
      color: 'bg-orange-500',
      link: '/admin/models'
    },
  ]

  return (
    <div className="fade-in space-y-6">
      <h1 className="text-2xl font-bold text-gray-800">仪表盘</h1>

      {/* 统计卡片 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((card, index) => {
          const Icon = card.icon
          return (
            <Link
              key={index}
              to={card.link}
              className="bg-white rounded-xl p-6 card-shadow hover:shadow-lg transition-all duration-300"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500">{card.title}</p>
                  <p className="text-3xl font-bold text-gray-800 mt-2">{card.value}</p>
                </div>
                <div className={`${card.color} p-3 rounded-xl`}>
                  <Icon className="h-6 w-6 text-white" />
                </div>
              </div>
            </Link>
          )
        })}
      </div>

      {/* 系统状态 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 今日统计 */}
        <div className="bg-white rounded-xl p-6 card-shadow">
          <h2 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
            <TrendingUp className="h-5 w-5 mr-2 text-primary-600" />
            今日统计
          </h2>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-gray-600">API调用次数</span>
              <span className="font-semibold">{stats?.api_calls_today || 0}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">平均响应时间</span>
              <span className="font-semibold">
                {stats?.avg_response_time_ms ? `${Math.round(stats.avg_response_time_ms)}ms` : '-'}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">错误率</span>
              <span className={`font-semibold ${stats?.error_rate > 5 ? 'text-red-500' : 'text-green-500'}`}>
                {stats?.error_rate ? `${stats.error_rate}%` : '0%'}
              </span>
            </div>
          </div>
        </div>

        {/* 系统健康 */}
        <div className="bg-white rounded-xl p-6 card-shadow">
          <h2 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
            <Activity className="h-5 w-5 mr-2 text-primary-600" />
            系统状态
          </h2>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-gray-600">服务状态</span>
              <span className={`flex items-center ${health?.status === 'ok' ? 'text-green-500' : 'text-yellow-500'}`}>
                {health?.status === 'ok' ? (
                  <CheckCircle className="h-4 w-4 mr-1" />
                ) : (
                  <AlertCircle className="h-4 w-4 mr-1" />
                )}
                {health?.status === 'ok' ? '正常' : '异常'}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">数据库</span>
              <span className={`flex items-center ${health?.database ? 'text-green-500' : 'text-red-500'}`}>
                {health?.database ? (
                  <CheckCircle className="h-4 w-4 mr-1" />
                ) : (
                  <AlertCircle className="h-4 w-4 mr-1" />
                )}
                {health?.database ? '已连接' : '未连接'}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Redis</span>
              <span className={`flex items-center ${health?.redis ? 'text-green-500' : 'text-red-500'}`}>
                {health?.redis ? (
                  <CheckCircle className="h-4 w-4 mr-1" />
                ) : (
                  <AlertCircle className="h-4 w-4 mr-1" />
                )}
                {health?.redis ? '已连接' : '未连接'}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">运行时间</span>
              <span className="font-semibold flex items-center">
                <Clock className="h-4 w-4 mr-1 text-gray-400" />
                {health?.uptime_seconds ? formatUptime(health.uptime_seconds) : '-'}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

function Activity(props) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
      <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
    </svg>
  )
}

function formatUptime(seconds) {
  if (seconds < 60) return `${seconds}秒`
  if (seconds < 3600) return `${Math.floor(seconds / 60)}分钟`
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}小时`
  return `${Math.floor(seconds / 86400)}天`
}
