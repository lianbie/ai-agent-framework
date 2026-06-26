import { useState, useRef, useEffect } from 'react'
import { Send, Bot, User, Trash2, Plus, MessageSquare, Clock, RefreshCw } from 'lucide-react'
import toast from 'react-hot-toast'

export default function Chat() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [streaming, setStreaming] = useState(false)
  const [sessionId, setSessionId] = useState(null)
  const [sessions, setSessions] = useState([])
  const [userId] = useState('admin_user')
  const messagesEndRef = useRef(null)
  const abortControllerRef = useRef(null)

  useEffect(() => {
    scrollToBottom()
    loadSessions()
  }, [messages])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const loadSessions = async () => {
    try {
      const response = await fetch(`/api/agent/sessions?user_id=${userId}`)
      const data = await response.json()
      if (data.sessions) {
        setSessions(data.sessions)
      }
    } catch (error) {
      console.error('加载会话列表失败:', error)
    }
  }

  const createNewSession = async () => {
    try {
      const response = await fetch(`/api/agent/sessions/new?user_id=${userId}`, {
        method: 'POST'
      })
      const data = await response.json()
      if (data.session_id) {
        setSessionId(data.session_id)
        setMessages([])
        toast.success('新会话已创建')
        loadSessions()
      }
    } catch (error) {
      toast.error('创建会话失败')
    }
  }

  const loadSessionHistory = async (sid) => {
    try {
      const response = await fetch(`/api/agent/sessions/${sid}/history`)
      const data = await response.json()
      if (data.history) {
        setMessages(data.history.map(h => ({
          role: h.role,
          content: h.content
        })))
        setSessionId(sid)
      }
    } catch (error) {
      toast.error('加载会话历史失败')
    }
  }

  const deleteSession = async (sid) => {
    if (!confirm('确定要删除这个会话吗？')) return

    try {
      await fetch(`/api/agent/sessions/${sid}`, { method: 'DELETE' })
      toast.success('会话已删除')
      if (sessionId === sid) {
        setSessionId(null)
        setMessages([])
      }
      loadSessions()
    } catch (error) {
      toast.error('删除会话失败')
    }
  }

  const handleSend = async () => {
    if (!input.trim() || loading) return

    const userMessage = input.trim()
    setInput('')
    setMessages(prev => [...prev, { role: 'user', content: userMessage }])
    setLoading(true)
    setStreaming(true)

    setMessages(prev => [...prev, { role: 'assistant', content: '', streaming: true }])

    abortControllerRef.current = new AbortController()

    try {
      const response = await fetch('/api/agent/chat/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: userMessage,
          user_id: userId,
          session_id: sessionId
        }),
        signal: abortControllerRef.current.signal
      })

      if (!response.ok) {
        throw new Error('请求失败')
      }

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''
      let fullReply = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n\n')
        buffer = lines.pop() || ''

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6))

              if (data.type === 'chunk') {
                fullReply += data.content
                setMessages(prev => {
                  const newMessages = [...prev]
                  const lastMsg = newMessages[newMessages.length - 1]
                  if (lastMsg.role === 'assistant') {
                    lastMsg.content = fullReply
                  }
                  return newMessages
                })

                if (!sessionId && data.session_id) {
                  setSessionId(data.session_id)
                }
              } else if (data.type === 'done') {
                setMessages(prev => {
                  const newMessages = [...prev]
                  const lastMsg = newMessages[newMessages.length - 1]
                  if (lastMsg.role === 'assistant') {
                    lastMsg.streaming = false
                    lastMsg.duration = data.duration_ms
                  }
                  return newMessages
                })
                loadSessions()
              } else if (data.type === 'error') {
                toast.error('请求失败: ' + data.error)
                setMessages(prev => prev.filter(m => !(m.role === 'assistant' && !m.content)))
              }
            } catch (e) {
              // 忽略解析错误
            }
          }
        }
      }
    } catch (error) {
      if (error.name !== 'AbortError') {
        toast.error('请求失败: ' + error.message)
        setMessages(prev => prev.filter(m => !(m.role === 'assistant' && !m.content)))
      }
    } finally {
      setLoading(false)
      setStreaming(false)
      abortControllerRef.current = null
    }
  }

  const stopGeneration = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const clearChat = () => {
    setMessages([])
    setSessionId(null)
    toast.success('对话已清空')
  }

  // 重置Agent
  const resetAgent = async () => {
    try {
      const response = await fetch('/api/agent/reset', { method: 'POST' })
      const data = await response.json()
      if (data.success) {
        toast.success('Agent已重置，模型配置已生效')
      } else {
        toast.error('重置失败')
      }
    } catch (error) {
      toast.error('重置失败: ' + error.message)
    }
  }

  const formatTime = (dateStr) => {
    if (!dateStr) return ''
    const date = new Date(dateStr)
    return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  }

  return (
    <div className="fade-in h-[calc(100vh-8rem)]">
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-bold text-gray-800">对话测试</h1>
        <div className="flex gap-2">
          <button
            onClick={resetAgent}
            className="flex items-center px-3 py-2 text-sm text-orange-600 hover:text-orange-700 hover:bg-orange-50 rounded-lg transition-colors"
            title="重置Agent（切换模型后点击）"
          >
            <RefreshCw className="h-4 w-4 mr-1" />
            重置Agent
          </button>
          <button
            onClick={createNewSession}
            className="flex items-center px-3 py-2 text-sm text-white btn-primary rounded-lg"
          >
            <Plus className="h-4 w-4 mr-1" />
            新会话
          </button>
          <button
            onClick={clearChat}
            className="flex items-center px-3 py-2 text-sm text-gray-600 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
          >
            <Trash2 className="h-4 w-4 mr-1" />
            清空
          </button>
        </div>
      </div>

      <div className="flex gap-4 h-[calc(100%-4rem)]">
        {/* 会话列表 */}
        <div className="w-64 bg-white rounded-xl card-shadow overflow-hidden flex flex-col">
          <div className="p-3 border-b bg-gray-50">
            <h3 className="font-semibold text-gray-700 flex items-center">
              <MessageSquare className="h-4 w-4 mr-2 text-primary-600" />
              会话列表
            </h3>
          </div>
          <div className="flex-1 overflow-auto">
            {sessions.length === 0 ? (
              <div className="p-4 text-center text-gray-400 text-sm">
                暂无会话
              </div>
            ) : (
              sessions.map((session) => (
                <div
                  key={session.session_id}
                  className={`p-3 border-b cursor-pointer hover:bg-gray-50 transition-colors ${
                    sessionId === session.session_id ? 'bg-primary-50 border-l-4 border-l-primary-600' : ''
                  }`}
                  onClick={() => loadSessionHistory(session.session_id)}
                >
                  <div className="flex justify-between items-start">
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-800 truncate">
                        {session.last_message || '新会话'}
                      </p>
                      <div className="flex items-center mt-1 text-xs text-gray-400">
                        <Clock className="h-3 w-3 mr-1" />
                        {formatTime(session.last_message_at)}
                        <span className="ml-2">{session.message_count} 条消息</span>
                      </div>
                    </div>
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        deleteSession(session.session_id)
                      }}
                      className="p-1 text-gray-400 hover:text-red-500"
                    >
                      <Trash2 className="h-3 w-3" />
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* 聊天区域 */}
        <div className="flex-1 bg-white rounded-xl card-shadow flex flex-col">
          {/* 消息区域 */}
          <div className="flex-1 overflow-auto p-4 space-y-4">
            {messages.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-full text-gray-400">
                <Bot className="h-16 w-16 mb-4 text-primary-300" />
                <p className="text-lg text-gray-600">开始对话测试</p>
                <p className="text-sm mt-2">输入消息与AI客服进行交互</p>
                <p className="text-xs mt-1 text-primary-500">支持流式响应，实时显示</p>
              </div>
            ) : (
              messages.map((msg, index) => (
                <div
                  key={index}
                  className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  {msg.role === 'assistant' ? (
                    <div className="max-w-[70%] flex items-start gap-3">
                      <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary-500 to-purple-500 flex items-center justify-center flex-shrink-0">
                        <Bot className="h-4 w-4 text-white" />
                      </div>
                      <div className="bg-gray-100 rounded-2xl rounded-tl-md p-4">
                        <div className="whitespace-pre-wrap text-gray-800">
                          {msg.content || (msg.streaming && '思考中...')}
                        </div>
                        {msg.streaming && (
                          <span className="inline-flex gap-1 ml-1">
                            <span className="w-1.5 h-1.5 rounded-full bg-primary-400 animate-bounce" style={{ animationDelay: '0ms' }} />
                            <span className="w-1.5 h-1.5 rounded-full bg-primary-400 animate-bounce" style={{ animationDelay: '150ms' }} />
                            <span className="w-1.5 h-1.5 rounded-full bg-primary-400 animate-bounce" style={{ animationDelay: '300ms' }} />
                          </span>
                        )}
                        {msg.duration && (
                          <div className="text-xs mt-2 text-gray-400">
                            耗时: {msg.duration}ms
                          </div>
                        )}
                      </div>
                    </div>
                  ) : (
                    <div className="max-w-[70%] bg-gradient-to-r from-primary-500 to-purple-500 rounded-2xl rounded-tr-md p-4 text-white">
                      <div className="whitespace-pre-wrap">{msg.content}</div>
                    </div>
                  )}
                </div>
              ))
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* 输入区域 */}
          <div className="border-t p-4">
            <div className="flex gap-2">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder={sessionId ? "输入消息..." : "点击新会话开始"}
                className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                disabled={loading}
              />
              {streaming ? (
                <button
                  onClick={stopGeneration}
                  className="px-4 py-3 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors"
                >
                  停止
                </button>
              ) : (
                <button
                  onClick={handleSend}
                  disabled={!input.trim() || loading}
                  className="px-4 py-3 btn-primary text-white rounded-lg disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <Send className="h-5 w-5" />
                </button>
              )}
            </div>
            {sessionId && (
              <div className="mt-2 text-xs text-gray-400">
                当前会话: {sessionId}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
