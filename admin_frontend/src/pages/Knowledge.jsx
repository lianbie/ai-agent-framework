import { useState, useEffect, useRef } from 'react'
import { Upload, Trash2, Search, FileText, CheckCircle, Clock, AlertCircle, Loader } from 'lucide-react'
import { knowledgeApi } from '../api'
import toast from 'react-hot-toast'

export default function Knowledge() {
  const [documents, setDocuments] = useState([])
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [uploading, setUploading] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState([])
  const [searching, setSearching] = useState(false)
  const fileInputRef = useRef(null)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const [docsData, statsData] = await Promise.all([
        knowledgeApi.listDocuments(),
        knowledgeApi.getStats()
      ])
      setDocuments(docsData)
      setStats(statsData)
    } catch (error) {
      toast.error('加载数据失败')
    } finally {
      setLoading(false)
    }
  }

  const handleUpload = async (e) => {
    const file = e.target.files[0]
    if (!file) return

    setUploading(true)
    try {
      await knowledgeApi.upload(file)
      toast.success('文档上传成功')
      loadData()
    } catch (error) {
      toast.error('上传失败: ' + (error.response?.data?.detail || error.message))
    } finally {
      setUploading(false)
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }
    }
  }

  const handleDelete = async (id) => {
    if (!confirm('确定要删除这个文档吗？')) return

    try {
      await knowledgeApi.deleteDocument(id)
      toast.success('文档已删除')
      loadData()
    } catch (error) {
      toast.error('删除失败')
    }
  }

  const handleSearch = async () => {
    if (!searchQuery.trim()) return

    setSearching(true)
    try {
      const results = await knowledgeApi.search({
        query: searchQuery,
        top_k: 5
      })
      setSearchResults(results)
    } catch (error) {
      toast.error('搜索失败')
    } finally {
      setSearching(false)
    }
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-5 w-5 text-green-500" />
      case 'processing':
        return <Loader className="h-5 w-5 text-blue-500 animate-spin" />
      case 'pending':
        return <Clock className="h-5 w-5 text-yellow-500" />
      case 'failed':
        return <AlertCircle className="h-5 w-5 text-red-500" />
      default:
        return null
    }
  }

  const getStatusText = (status) => {
    switch (status) {
      case 'completed': return '已完成'
      case 'processing': return '处理中'
      case 'pending': return '待处理'
      case 'failed': return '失败'
      default: return status
    }
  }

  const formatFileSize = (bytes) => {
    if (!bytes) return '-'
    if (bytes < 1024) return bytes + ' B'
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
  }

  return (
    <div className="fade-in">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-800">知识库管理</h1>
        <button
          onClick={() => fileInputRef.current?.click()}
          disabled={uploading}
          className="flex items-center px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 transition-colors"
        >
          {uploading ? (
            <Loader className="h-5 w-5 mr-1 animate-spin" />
          ) : (
            <Upload className="h-5 w-5 mr-1" />
          )}
          上传文档
        </button>
        <input
          ref={fileInputRef}
          type="file"
          accept=".txt,.pdf,.docx,.xlsx,.csv,.json"
          onChange={handleUpload}
          className="hidden"
        />
      </div>

      {/* 统计卡片 */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white rounded-lg shadow p-4">
            <p className="text-sm text-gray-500">总文档数</p>
            <p className="text-2xl font-bold">{stats.total_documents}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <p className="text-sm text-gray-500">已完成</p>
            <p className="text-2xl font-bold text-green-600">{stats.completed_documents}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <p className="text-sm text-gray-500">总分片数</p>
            <p className="text-2xl font-bold">{stats.total_chunks}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <p className="text-sm text-gray-500">总大小</p>
            <p className="text-2xl font-bold">{formatFileSize(stats.total_size_bytes)}</p>
          </div>
        </div>
      )}

      {/* 搜索测试 */}
      <div className="bg-white rounded-lg shadow-md p-4 mb-6">
        <h2 className="text-lg font-semibold mb-3">搜索测试</h2>
        <div className="flex gap-2">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            placeholder="输入搜索内容..."
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
          <button
            onClick={handleSearch}
            disabled={searching || !searchQuery.trim()}
            className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 transition-colors"
          >
            {searching ? (
              <Loader className="h-5 w-5 animate-spin" />
            ) : (
              <Search className="h-5 w-5" />
            )}
          </button>
        </div>

        {searchResults.length > 0 && (
          <div className="mt-4 space-y-3">
            <h3 className="text-sm font-medium text-gray-700">搜索结果：</h3>
            {searchResults.map((result, index) => (
              <div key={index} className="p-3 bg-gray-50 rounded-lg">
                <div className="flex justify-between items-start">
                  <p className="text-sm text-gray-800 flex-1">{result.content}</p>
                  <span className="text-xs text-gray-500 ml-2">
                    相似度: {(result.score * 100).toFixed(1)}%
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* 文档列表 */}
      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="loading-spinner"></div>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">文件名</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">类型</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">大小</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">分片数</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">状态</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">上传时间</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">操作</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {documents.map((doc) => (
                <tr key={doc.id} className="table-row hover:bg-gray-50">
                  <td className="px-6 py-4">
                    <div className="flex items-center">
                      <FileText className="h-5 w-5 text-gray-400 mr-2" />
                      <span className="font-medium text-gray-900">{doc.filename}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {doc.file_type || '-'}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {formatFileSize(doc.file_size)}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {doc.chunk_count}
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-1">
                      {getStatusIcon(doc.status)}
                      <span className="text-sm">{getStatusText(doc.status)}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {new Date(doc.created_at).toLocaleString()}
                  </td>
                  <td className="px-6 py-4 text-right">
                    <button
                      onClick={() => handleDelete(doc.id)}
                      className="p-1 text-red-600 hover:bg-red-50 rounded"
                      title="删除"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {documents.length === 0 && (
            <div className="text-center py-12 text-gray-500">
              暂无文档，请上传知识库文件
            </div>
          )}
        </div>
      )}
    </div>
  )
}
