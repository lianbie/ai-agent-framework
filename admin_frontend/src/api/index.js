import axios from 'axios'

// 创建axios实例
const api = axios.create({
  baseURL: '/api/admin',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    // 可以在这里添加token等认证信息
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    const message = error.response?.data?.detail || error.message || '请求失败'
    console.error('API Error:', message)
    return Promise.reject(error)
  }
)

// ============ 提示词API ============

export const promptsApi = {
  // 获取提示词列表
  list: (params = {}) => api.get('/prompts', { params }),

  // 获取单个提示词
  get: (id) => api.get(`/prompts/${id}`),

  // 创建提示词
  create: (data) => api.post('/prompts', data),

  // 更新提示词
  update: (id, data) => api.put(`/prompts/${id}`, data),

  // 删除提示词
  delete: (id) => api.delete(`/prompts/${id}`),

  // 测试提示词
  test: (data) => api.post('/prompts/test', data),
}

// ============ 知识库API ============

export const knowledgeApi = {
  // 获取文档列表
  listDocuments: (params = {}) => api.get('/knowledge/documents', { params }),

  // 上传文档
  upload: (file) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/knowledge/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },

  // 删除文档
  deleteDocument: (id) => api.delete(`/knowledge/documents/${id}`),

  // 搜索知识库
  search: (data) => api.post('/knowledge/search', data),

  // 获取统计
  getStats: () => api.get('/knowledge/stats'),
}

// ============ 模型配置API ============

export const modelsApi = {
  // 获取模型列表
  list: (params = {}) => api.get('/models', { params }),

  // 获取单个模型
  get: (id) => api.get(`/models/${id}`),

  // 创建模型配置
  create: (data) => api.post('/models', data),

  // 更新模型配置
  update: (id, data) => api.put(`/models/${id}`, data),

  // 删除模型配置
  delete: (id) => api.delete(`/models/${id}`),

  // 激活模型
  activate: (id) => api.post(`/models/${id}/activate`),

  // 测试模型
  test: (data) => api.post('/models/test', data),
}

// ============ 对话管理API ============

export const conversationsApi = {
  // 获取对话列表
  list: (params = {}) => api.get('/conversations', { params }),

  // 获取会话列表
  listSessions: (params = {}) => api.get('/conversations/sessions', { params }),

  // 获取会话详情
  getSession: (sessionId) => api.get(`/conversations/sessions/${sessionId}`),

  // 删除对话
  delete: (id) => api.delete(`/conversations/${id}`),

  // 删除会话
  deleteSession: (sessionId) => api.delete(`/conversations/sessions/${sessionId}`),

  // 导出对话
  export: (data) => api.post('/conversations/export', data),
}

// ============ 系统监控API ============

export const monitorApi = {
  // 获取系统统计
  getStats: () => api.get('/monitor/stats'),

  // 获取系统日志
  getLogs: (params = {}) => api.get('/monitor/logs', { params }),

  // 健康检查
  healthCheck: () => api.get('/monitor/health'),

  // 获取性能指标
  getPerformance: () => api.get('/monitor/performance'),
}

// ============ 智能问答API ============

export const chatApi = {
  // 发送消息
  send: (data) => axios.post('/api/agent/chat', data),

  // 健康检查
  health: () => axios.get('/api/agent/health'),

  // 获取信息
  info: () => axios.get('/api/agent/info'),
}

export default api
