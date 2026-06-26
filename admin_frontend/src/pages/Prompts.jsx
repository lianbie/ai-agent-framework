import { useState, useEffect } from 'react'
import { Plus, Edit, Trash2, TestTube, Star, Search } from 'lucide-react'
import { promptsApi } from '../api'
import toast from 'react-hot-toast'

export default function Prompts() {
  const [prompts, setPrompts] = useState([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [editingPrompt, setEditingPrompt] = useState(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    system_prompt: '',
    is_default: false
  })
  const [testMessage, setTestMessage] = useState('')
  const [testResult, setTestResult] = useState(null)
  const [testing, setTesting] = useState(false)

  useEffect(() => {
    loadPrompts()
  }, [])

  const loadPrompts = async () => {
    try {
      const data = await promptsApi.list({ search: searchTerm })
      setPrompts(data)
    } catch (error) {
      toast.error('加载提示词失败')
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async () => {
    try {
      if (editingPrompt) {
        await promptsApi.update(editingPrompt.id, formData)
        toast.success('提示词已更新')
      } else {
        await promptsApi.create(formData)
        toast.success('提示词已创建')
      }
      setShowModal(false)
      setEditingPrompt(null)
      resetForm()
      loadPrompts()
    } catch (error) {
      toast.error('操作失败: ' + (error.response?.data?.detail || error.message))
    }
  }

  const handleEdit = (prompt) => {
    setEditingPrompt(prompt)
    setFormData({
      name: prompt.name,
      description: prompt.description || '',
      system_prompt: prompt.system_prompt,
      is_default: prompt.is_default
    })
    setShowModal(true)
  }

  const handleDelete = async (id) => {
    if (!confirm('确定要删除这个提示词吗？')) return

    try {
      await promptsApi.delete(id)
      toast.success('提示词已删除')
      loadPrompts()
    } catch (error) {
      toast.error('删除失败: ' + (error.response?.data?.detail || error.message))
    }
  }

  const handleTest = async (prompt) => {
    if (!testMessage.trim()) {
      toast.error('请输入测试消息')
      return
    }

    setTesting(true)
    setTestResult(null)

    try {
      const result = await promptsApi.test({
        prompt_id: prompt.id,
        message: testMessage
      })
      setTestResult(result)
    } catch (error) {
      toast.error('测试失败')
    } finally {
      setTesting(false)
    }
  }

  const resetForm = () => {
    setFormData({
      name: '',
      description: '',
      system_prompt: '',
      is_default: false
    })
  }

  const filteredPrompts = prompts.filter(p =>
    p.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    p.description?.toLowerCase().includes(searchTerm.toLowerCase())
  )

  return (
    <div className="fade-in">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-800">提示词管理</h1>
        <button
          onClick={() => {
            resetForm()
            setEditingPrompt(null)
            setShowModal(true)
          }}
          className="flex items-center px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
        >
          <Plus className="h-5 w-5 mr-1" />
          新建提示词
        </button>
      </div>

      {/* 搜索栏 */}
      <div className="mb-4">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
          <input
            type="text"
            placeholder="搜索提示词..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            onKeyUp={() => loadPrompts()}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
        </div>
      </div>

      {/* 提示词列表 */}
      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="loading-spinner"></div>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">名称</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">描述</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">版本</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">状态</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">操作</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {filteredPrompts.map((prompt) => (
                <tr key={prompt.id} className="table-row hover:bg-gray-50">
                  <td className="px-6 py-4">
                    <div className="flex items-center">
                      {prompt.is_default && (
                        <Star className="h-4 w-4 text-yellow-500 mr-2" />
                      )}
                      <span className="font-medium text-gray-900">{prompt.name}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500 max-w-xs truncate">
                    {prompt.description || '-'}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    v{prompt.version}
                  </td>
                  <td className="px-6 py-4">
                    {prompt.is_default ? (
                      <span className="px-2 py-1 text-xs font-medium bg-yellow-100 text-yellow-800 rounded-full">
                        默认
                      </span>
                    ) : (
                      <span className="px-2 py-1 text-xs font-medium bg-gray-100 text-gray-800 rounded-full">
                        普通
                      </span>
                    )}
                  </td>
                  <td className="px-6 py-4 text-right">
                    <div className="flex items-center justify-end gap-2">
                      <button
                        onClick={() => handleEdit(prompt)}
                        className="p-1 text-blue-600 hover:bg-blue-50 rounded"
                        title="编辑"
                      >
                        <Edit className="h-4 w-4" />
                      </button>
                      <button
                        onClick={() => handleDelete(prompt.id)}
                        className="p-1 text-red-600 hover:bg-red-50 rounded"
                        title="删除"
                        disabled={prompt.is_default}
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {filteredPrompts.length === 0 && (
            <div className="text-center py-12 text-gray-500">
              暂无提示词
            </div>
          )}
        </div>
      )}

      {/* 编辑/创建弹窗 */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl max-h-[90vh] overflow-auto">
            <div className="p-6">
              <h2 className="text-xl font-bold mb-4">
                {editingPrompt ? '编辑提示词' : '新建提示词'}
              </h2>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    名称 <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                    placeholder="输入提示词名称"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    描述
                  </label>
                  <input
                    type="text"
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                    placeholder="输入描述（可选）"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    系统提示词 <span className="text-red-500">*</span>
                  </label>
                  <textarea
                    value={formData.system_prompt}
                    onChange={(e) => setFormData({ ...formData, system_prompt: e.target.value })}
                    rows={8}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                    placeholder="输入系统提示词..."
                  />
                </div>

                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="is_default"
                    checked={formData.is_default}
                    onChange={(e) => setFormData({ ...formData, is_default: e.target.checked })}
                    className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                  />
                  <label htmlFor="is_default" className="ml-2 text-sm text-gray-700">
                    设为默认提示词
                  </label>
                </div>
              </div>

              <div className="flex justify-end gap-2 mt-6">
                <button
                  onClick={() => {
                    setShowModal(false)
                    setEditingPrompt(null)
                  }}
                  className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
                >
                  取消
                </button>
                <button
                  onClick={handleSubmit}
                  disabled={!formData.name || !formData.system_prompt}
                  className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 transition-colors"
                >
                  {editingPrompt ? '更新' : '创建'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
