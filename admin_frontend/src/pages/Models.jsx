import { useState, useEffect } from 'react'
import { Plus, Edit, Trash2, TestTube, Power, Search, Loader } from 'lucide-react'
import { modelsApi } from '../api'
import toast from 'react-hot-toast'

export default function Models() {
  const [models, setModels] = useState([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [editingModel, setEditingModel] = useState(null)
  const [formData, setFormData] = useState({
    name: '',
    provider: 'openai',
    model_id: '',
    base_url: '',
    api_key: '',
    parameters: { temperature: 0.7, max_tokens: 2000 }
  })
  const [testMessage, setTestMessage] = useState('你好，请介绍一下自己')
  const [testResult, setTestResult] = useState(null)
  const [testing, setTesting] = useState(false)

  useEffect(() => {
    loadModels()
  }, [])

  const loadModels = async () => {
    try {
      const data = await modelsApi.list()
      setModels(data)
    } catch (error) {
      toast.error('加载模型失败')
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async () => {
    try {
      if (editingModel) {
        await modelsApi.update(editingModel.id, formData)
        toast.success('模型已更新')
      } else {
        await modelsApi.create(formData)
        toast.success('模型已创建')
      }
      setShowModal(false)
      setEditingModel(null)
      resetForm()
      loadModels()
    } catch (error) {
      toast.error('操作失败: ' + (error.response?.data?.detail || error.message))
    }
  }

  const handleEdit = (model) => {
    setEditingModel(model)
    setFormData({
      name: model.name,
      provider: model.provider,
      model_id: model.model_id,
      base_url: model.base_url || '',
      api_key: '',
      parameters: model.parameters || { temperature: 0.7, max_tokens: 2000 }
    })
    setShowModal(true)
  }

  const handleDelete = async (id) => {
    if (!confirm('确定要删除这个模型配置吗？')) return

    try {
      await modelsApi.delete(id)
      toast.success('模型已删除')
      loadModels()
    } catch (error) {
      toast.error('删除失败: ' + (error.response?.data?.detail || error.message))
    }
  }

  const handleActivate = async (id) => {
    try {
      await modelsApi.activate(id)
      toast.success('模型已激活')
      loadModels()
    } catch (error) {
      toast.error('激活失败')
    }
  }

  const handleTest = async (model) => {
    setTesting(true)
    setTestResult(null)

    try {
      const result = await modelsApi.test({
        model_id: model.id,
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
      provider: 'openai',
      model_id: '',
      base_url: '',
      api_key: '',
      parameters: { temperature: 0.7, max_tokens: 2000 }
    })
  }

  const providers = [
    { value: 'openai', label: 'OpenAI' },
    { value: 'anthropic', label: 'Anthropic' },
    { value: 'ollama', label: 'Ollama' },
    { value: 'doubao', label: '豆包' },
    { value: 'dashscope', label: 'DashScope' },
    { value: 'custom', label: '自定义' },
  ]

  return (
    <div className="fade-in">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-800">模型配置</h1>
        <button
          onClick={() => {
            resetForm()
            setEditingModel(null)
            setShowModal(true)
          }}
          className="flex items-center px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
        >
          <Plus className="h-5 w-5 mr-1" />
          添加模型
        </button>
      </div>

      {/* 模型列表 */}
      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="loading-spinner"></div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {models.map((model) => (
            <div
              key={model.id}
              className={`bg-white rounded-lg shadow-md p-4 border-2 transition-colors ${
                model.is_active ? 'border-green-500' : 'border-transparent'
              }`}
            >
              <div className="flex items-start justify-between mb-3">
                <div>
                  <h3 className="font-semibold text-gray-900">{model.name}</h3>
                  <p className="text-sm text-gray-500">{model.provider}</p>
                </div>
                {model.is_active && (
                  <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded-full">
                    激活中
                  </span>
                )}
              </div>

              <div className="space-y-2 text-sm text-gray-600 mb-4">
                <p>模型: {model.model_id}</p>
                {model.base_url && <p className="truncate">地址: {model.base_url}</p>}
                <p>
                  参数: 温度={model.parameters?.temperature || 0.7},
                  最大token={model.parameters?.max_tokens || 2000}
                </p>
              </div>

              <div className="flex gap-2">
                <button
                  onClick={() => handleActivate(model.id)}
                  disabled={model.is_active}
                  className={`flex-1 flex items-center justify-center px-3 py-2 rounded text-sm ${
                    model.is_active
                      ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                      : 'bg-green-50 text-green-600 hover:bg-green-100'
                  }`}
                >
                  <Power className="h-4 w-4 mr-1" />
                  激活
                </button>
                <button
                  onClick={() => handleEdit(model)}
                  className="px-3 py-2 bg-blue-50 text-blue-600 rounded hover:bg-blue-100"
                >
                  <Edit className="h-4 w-4" />
                </button>
                <button
                  onClick={() => handleDelete(model.id)}
                  disabled={model.is_active}
                  className="px-3 py-2 bg-red-50 text-red-600 rounded hover:bg-red-100 disabled:opacity-50"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            </div>
          ))}

          {models.length === 0 && (
            <div className="col-span-full text-center py-12 text-gray-500">
              暂无模型配置
            </div>
          )}
        </div>
      )}

      {/* 测试区域 */}
      <div className="mt-8 bg-white rounded-lg shadow-md p-6">
        <h2 className="text-lg font-semibold mb-4">模型测试</h2>
        <div className="flex gap-2 mb-4">
          <input
            type="text"
            value={testMessage}
            onChange={(e) => setTestMessage(e.target.value)}
            placeholder="输入测试消息..."
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
        </div>

        {testResult && (
          <div className="p-4 bg-gray-50 rounded-lg">
            <p className="text-sm text-gray-500 mb-2">测试结果：</p>
            <p className="text-gray-800">{testResult.reply}</p>
            {testResult.duration_ms && (
              <p className="text-xs text-gray-500 mt-2">耗时: {testResult.duration_ms}ms</p>
            )}
          </div>
        )}
      </div>

      {/* 编辑/创建弹窗 */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-lg max-h-[90vh] overflow-auto">
            <div className="p-6">
              <h2 className="text-xl font-bold mb-4">
                {editingModel ? '编辑模型' : '添加模型'}
              </h2>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">名称</label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">提供商</label>
                  <select
                    value={formData.provider}
                    onChange={(e) => setFormData({ ...formData, provider: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                  >
                    {providers.map(p => (
                      <option key={p.value} value={p.value}>{p.label}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">模型ID</label>
                  <input
                    type="text"
                    value={formData.model_id}
                    onChange={(e) => setFormData({ ...formData, model_id: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                    placeholder="gpt-4o-mini"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">API地址</label>
                  <input
                    type="text"
                    value={formData.base_url}
                    onChange={(e) => setFormData({ ...formData, base_url: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                    placeholder="https://api.openai.com/v1"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">API密钥</label>
                  <input
                    type="password"
                    value={formData.api_key}
                    onChange={(e) => setFormData({ ...formData, api_key: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                    placeholder="sk-..."
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">温度</label>
                    <input
                      type="number"
                      min="0"
                      max="2"
                      step="0.1"
                      value={formData.parameters.temperature}
                      onChange={(e) => setFormData({
                        ...formData,
                        parameters: { ...formData.parameters, temperature: parseFloat(e.target.value) }
                      })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">最大Token</label>
                    <input
                      type="number"
                      min="100"
                      max="128000"
                      value={formData.parameters.max_tokens}
                      onChange={(e) => setFormData({
                        ...formData,
                        parameters: { ...formData.parameters, max_tokens: parseInt(e.target.value) }
                      })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                    />
                  </div>
                </div>
              </div>

              <div className="flex justify-end gap-2 mt-6">
                <button
                  onClick={() => {
                    setShowModal(false)
                    setEditingModel(null)
                  }}
                  className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200"
                >
                  取消
                </button>
                <button
                  onClick={handleSubmit}
                  disabled={!formData.name || !formData.model_id}
                  className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50"
                >
                  {editingModel ? '更新' : '创建'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
