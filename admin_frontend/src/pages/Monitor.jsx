import { useState, useEffect } from 'react'
import {
  Activity,
  Cpu,
  MemoryStick,
  Clock,
  RefreshCw,
  AlertTriangle,
  Info,
  AlertCircle,
  CheckCircle
} from 'lucide-react'
import { monitorApi } from '../api'
import toast from 'react-hot-toast'

export default function Monitor() {
  const [stats, setStats] = useState(null)
  const [health, setHealth] = useState(null)
  const [performance, setPerformance] = useState(null)
  const [logs, setLogs] = useState([])
  const [loading, setLoading] = useState(true)
  const [logLevel, setLogLevel] = useState('')

  useEffect(() => {
    loadData()
    const interval = setInterval(loadData, 30000) // 每30秒刷新
    return () => clearInterval(interval)
  }, [logLevel])

  const loadData = async () => {
    try {
      const [statsData, healthData, perfData, logsData] = await Promise.all([
        monitorApi.getStats(),
        monitorApi.healthCheck(),
        monitorApi.getPerformance(),
        monitorApi.getLogs({ level: logLevel || undefined, page_size: 50 })
      ])
      setStats(statsData)
      setHealth(healthData)
      setPerformance(perfData)
      setLogs(logsData)
    } catch (error) {
      console.error('加载监控数据失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const getLogLevelIcon = (level) => {
    switch (level) {
      case 'ERROR':
        return <AlertCircle className="h-4 w-4 text-red-500" />
      case 'WARNING':
        return <AlertTriangle className="h-4 w-4 text-yellow-500" />
      case 'INFO':
        return <Info className="h-4 w-4 text-blue-500" />
      default:
        return <CheckCircle className="h-4 w-4 text-gray-400" />
    }
  }

  const getLogLevelColor = (level) => {
    switch (level) {
      case 'ERROR': return 'bg-red-50 text-red-800'
      case 'WARNING': return 'bg-yellow-50 text-yellow-800'
      case 'INFO': return 'bg-blue-50 text-blue-800'
      default: return 'bg-gray-50 text-gray-800'
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="loading-spinner"></div>
      </div>
    )
  }

  return (
    <div className="fade-in">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-800">系统监控</h1>
        <button
          onClick={loadData}
          className="flex items-center px-4 py-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
        >
          <RefreshCw className="h-5 w-5 mr-1" />
          刷新
        </button>
      </div>

      {/* 系统状态卡片 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {/* 服务状态 */}
        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">服务状态</p>
              <p className={`text-lg font-semibold ${health?.status === 'ok' ? 'text-green-600' : 'text-yellow-600'}`}>
                {health?.status === 'ok' ? '正常' : '异常'}
              </p>
            </div>
            <Activity className="h-8 w-8 text-primary-500" />
          </div>
        </div>

        {/* CPU使用率 */}
        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">CPU使用率</p>
              <p className="text-lg font-semibold">
                {performance?.process?.cpu_percent?.toFixed(1) || 0}%
              </p>
            </div>
            <Cpu className="h-8 w-8 text-blue-500" />
          </div>
        </div>

        {/* 内存使用 */}
        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">内存使用</p>
              <p className="text-lg font-semibold">
                {performance?.process?.memory_mb?.toFixed(0) || 0} MB
              </p>
            </div>
            <MemoryStick className="h-8 w-8 text-purple-500" />
          </div>
        </div>

        {/* 运行时间 */}
        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">运行时间</p>
              <p className="text-lg font-semibold">
                {formatUptime(health?.uptime_seconds || 0)}
              </p>
            </div>
            <Clock className="h-8 w-8 text-orange-500" />
          </div>
        </div>
      </div>

      {/* 连接状态 */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center justify-between">
            <span className="text-gray-600">数据库</span>
            <span className={`flex items-center ${health?.database ? 'text-green-600' : 'text-red-600'}`}>
              {health?.database ? (
                <CheckCircle className="h-5 w-5 mr-1" />
              ) : (
                <AlertCircle className="h-5 w-5 mr-1" />
              )}
              {health?.database ? '已连接' : '未连接'}
            </span>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center justify-between">
            <span className="text-gray-600">Redis</span>
            <span className={`flex items-center ${health?.redis ? 'text-green-600' : 'text-red-600'}`}>
              {health?.redis ? (
                <CheckCircle className="h-5 w-5 mr-1" />
              ) : (
                <AlertCircle className="h-5 w-5 mr-1" />
              )}
              {health?.redis ? '已连接' : '未连接'}
            </span>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center justify-between">
            <span className="text-gray-600">向量存储</span>
            <span className={`flex items-center ${health?.vector_store ? 'text-green-600' : 'text-red-600'}`}>
              {health?.vector_store ? (
                <CheckCircle className="h-5 w-5 mr-1" />
              ) : (
                <AlertCircle className="h-5 w-5 mr-1" />
              )}
              {health?.vector_store ? '已连接' : '未连接'}
            </span>
          </div>
        </div>
      </div>

      {/* 系统统计 */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h2 className="text-lg font-semibold mb-4">系统统计</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <p className="text-sm text-gray-500">总对话数</p>
            <p className="text-2xl font-bold">{stats?.total_conversations || 0}</p>
          </div>
          <div>
            <p className="text-sm text-gray-500">今日API调用</p>
            <p className="text-2xl font-bold">{stats?.api_calls_today || 0}</p>
          </div>
          <div>
            <p className="text-sm text-gray-500">平均响应时间</p>
            <p className="text-2xl font-bold">
              {stats?.avg_response_time_ms ? `${Math.round(stats.avg_response_time_ms)}ms` : '-'}
            </p>
          </div>
          <div>
            <p className="text-sm text-gray-500">错误率</p>
            <p className={`text-2xl font-bold ${stats?.error_rate > 5 ? 'text-red-600' : 'text-green-600'}`}>
              {stats?.error_rate || 0}%
            </p>
          </div>
        </div>
      </div>

      {/* 系统日志 */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold">系统日志</h2>
          <select
            value={logLevel}
            onChange={(e) => setLogLevel(e.target.value)}
            className="px-3 py-1 border border-gray-300 rounded-lg text-sm"
          >
            <option value="">全部级别</option>
            <option value="ERROR">错误</option>
            <option value="WARNING">警告</option>
            <option value="INFO">信息</option>
            <option value="DEBUG">调试</option>
          </select>
        </div>

        <div className="overflow-auto max-h-96">
          {logs.length > 0 ? (
            <div className="space-y-2">
              {logs.map((log) => (
                <div
                  key={log.id}
                  className={`p-3 rounded-lg ${getLogLevelColor(log.level)}`}
                >
                  <div className="flex items-start gap-2">
                    {getLogLevelIcon(log.level)}
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <span className="font-medium text-xs">{log.level}</span>
                        {log.module && (
                          <span className="text-xs opacity-75">[{log.module}]</span>
                        )}
                        <span className="text-xs opacity-50">
                          {new Date(log.created_at).toLocaleString()}
                        </span>
                      </div>
                      <p className="mt-1 text-sm">{log.message}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              暂无日志记录
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

function formatUptime(seconds) {
  if (seconds < 60) return `${seconds}秒`
  if (seconds < 3600) return `${Math.floor(seconds / 60)}分钟`
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}小时`
  return `${Math.floor(seconds / 86400)}天`
}
