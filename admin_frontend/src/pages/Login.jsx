import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Phone, Lock, MessageSquare, Eye, EyeOff, Bot } from 'lucide-react'
import toast from 'react-hot-toast'

export default function Login() {
  const navigate = useNavigate()
  const [loginType, setLoginType] = useState('sms')
  const [phone, setPhone] = useState('')
  const [code, setCode] = useState('')
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  const [countdown, setCountdown] = useState(0)
  const [devCode, setDevCode] = useState('')

  useEffect(() => {
    if (countdown > 0) {
      const timer = setTimeout(() => setCountdown(countdown - 1), 1000)
      return () => clearTimeout(timer)
    }
  }, [countdown])

  const sendCode = async () => {
    if (!phone || phone.length !== 11) {
      toast.error('请输入正确的手机号')
      return
    }

    try {
      const response = await fetch('/api/auth/send-code', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ phone })
      })
      const data = await response.json()

      if (data.success) {
        toast.success('验证码已发送')
        setCountdown(60)
        if (data.code) {
          setDevCode(data.code)
          toast.success(`开发环境验证码: ${data.code}`, { duration: 10000 })
        }
      } else {
        toast.error(data.message || '发送失败')
      }
    } catch (error) {
      toast.error('发送验证码失败')
    }
  }

  const handleSmsLogin = async () => {
    if (!phone || !code) {
      toast.error('请输入手机号和验证码')
      return
    }

    setLoading(true)
    try {
      const response = await fetch('/api/auth/login/sms', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ phone, code })
      })
      const data = await response.json()

      if (data.success) {
        localStorage.setItem('token', data.token)
        localStorage.setItem('user', JSON.stringify({
          id: data.user_id,
          username: data.username,
          nickname: data.nickname,
          role: data.role
        }))
        toast.success('登录成功')
        navigate('/admin')
      } else {
        toast.error(data.message || '登录失败')
      }
    } catch (error) {
      toast.error('登录失败')
    } finally {
      setLoading(false)
    }
  }

  const handlePasswordLogin = async () => {
    if (!username || !password) {
      toast.error('请输入用户名和密码')
      return
    }

    setLoading(true)
    try {
      const response = await fetch('/api/auth/login/password', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      })
      const data = await response.json()

      if (data.success) {
        localStorage.setItem('token', data.token)
        localStorage.setItem('user', JSON.stringify({
          id: data.user_id,
          username: data.username,
          nickname: data.nickname,
          role: data.role
        }))
        toast.success('登录成功')
        navigate('/admin')
      } else {
        toast.error(data.message || '登录失败')
      }
    } catch (error) {
      toast.error('登录失败')
    } finally {
      setLoading(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      if (loginType === 'sms') {
        handleSmsLogin()
      } else {
        handlePasswordLogin()
      }
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-600 to-purple-600 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-white rounded-2xl shadow-lg mb-4">
            <span className="text-3xl">🤖</span>
          </div>
          <h1 className="text-3xl font-bold text-white">AI智能客服</h1>
          <p className="text-white/80 mt-2">管理后台登录</p>
        </div>

        {/* 登录卡片 */}
        <div className="bg-white rounded-2xl shadow-xl p-8">
          {/* 登录方式切换 */}
          <div className="flex mb-6 bg-gray-100 rounded-lg p-1">
            <button
              onClick={() => setLoginType('sms')}
              className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
                loginType === 'sms'
                  ? 'bg-white text-primary-600 shadow-sm'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              短信验证码登录
            </button>
            <button
              onClick={() => setLoginType('password')}
              className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
                loginType === 'password'
                  ? 'bg-white text-primary-600 shadow-sm'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              密码登录
            </button>
          </div>

          {/* 短信登录表单 */}
          {loginType === 'sms' && (
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">手机号</label>
                <div className="relative">
                  <Phone className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                  <input
                    type="tel"
                    value={phone}
                    onChange={(e) => setPhone(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="请输入手机号"
                    maxLength={11}
                    className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">验证码</label>
                <div className="flex gap-2">
                  <div className="relative flex-1">
                    <MessageSquare className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                    <input
                      type="text"
                      value={code}
                      onChange={(e) => setCode(e.target.value)}
                      onKeyPress={handleKeyPress}
                      placeholder="请输入验证码"
                      maxLength={6}
                      className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    />
                  </div>
                  <button
                    onClick={sendCode}
                    disabled={countdown > 0}
                    className="px-4 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors whitespace-nowrap"
                  >
                    {countdown > 0 ? `${countdown}秒` : '获取验证码'}
                  </button>
                </div>
                {devCode && (
                  <p className="text-xs text-gray-500 mt-1">开发环境验证码: {devCode}</p>
                )}
              </div>

              <button
                onClick={handleSmsLogin}
                disabled={loading}
                className="w-full py-3 btn-primary text-white rounded-lg disabled:opacity-50 disabled:cursor-not-allowed font-medium"
              >
                {loading ? '登录中...' : '登录'}
              </button>
            </div>
          )}

          {/* 密码登录表单 */}
          {loginType === 'password' && (
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">用户名/手机号/邮箱</label>
                <div className="relative">
                  <Phone className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                  <input
                    type="text"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="请输入用户名"
                    className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">密码</label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                  <input
                    type={showPassword ? 'text' : 'password'}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="请输入密码"
                    className="w-full pl-10 pr-12 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                  <button
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                  >
                    {showPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
                  </button>
                </div>
              </div>

              <button
                onClick={handlePasswordLogin}
                disabled={loading}
                className="w-full py-3 btn-primary text-white rounded-lg disabled:opacity-50 disabled:cursor-not-allowed font-medium"
              >
                {loading ? '登录中...' : '登录'}
              </button>
            </div>
          )}

          {/* 提示信息 */}
          <div className="mt-6 p-4 bg-gray-50 rounded-lg">
            <p className="text-sm text-gray-600 font-medium">演示账号</p>
            <p className="text-xs text-gray-500 mt-1">
              用户名: admin &nbsp;&nbsp; 密码: admin123
            </p>
            <p className="text-xs text-gray-500 mt-1">
              或使用任意手机号 + 验证码登录
            </p>
          </div>
        </div>

        {/* 底部信息 */}
        <p className="text-center text-white/60 text-sm mt-6">
          AI Agent Framework © 2024
        </p>
      </div>
    </div>
  )
}
