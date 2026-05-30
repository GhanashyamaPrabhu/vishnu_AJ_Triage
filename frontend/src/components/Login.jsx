import React, { useState } from 'react'
import { useAuth } from '../hooks/useAuth.jsx'
import { useNavigate } from 'react-router-dom'

const Login = () => {
  const [formData, setFormData] = useState({
    username: '',
    password: ''
  })
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const [showPassword, setShowPassword] = useState(false)

  const { login } = useAuth()
  const navigate = useNavigate()

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
    // Clear error when user starts typing
    if (error) setError('')
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setIsLoading(true)
    setError('')

    try {
      const result = await login(formData.username, formData.password)
      
      if (result.success) {
        navigate('/')
      } else {
        setError(result.error || 'Login failed. Please check your credentials.')
      }
    } catch (err) {
      setError('An unexpected error occurred. Please try again.')
      console.error('Login error:', err)
    } finally {
      setIsLoading(false)
    }
  }

  const handleDemoLogin = async () => {
    setFormData({
      username: 'ajadmin',
      password: 'AJTriage2024!'
    })
    setError('')
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#1a2f5e] via-[#2e4a7a] to-[#1a2f5e] flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      {/* Institution Header */}
      <div className="text-center mb-8">
        <div className="mx-auto w-20 h-20 bg-white rounded-full flex items-center justify-center shadow-lg mb-4">
          <span className="text-[#1a2f5e] font-bold text-2xl">AJ</span>
        </div>
        <h1 className="text-2xl font-bold text-white leading-tight">
          A.J. INSTITUTE OF MEDICAL SCIENCES
        </h1>
        <h2 className="text-lg font-medium text-blue-100">
          AND RESEARCH CENTRE
        </h2>
        <h3 className="text-base font-medium text-blue-200 mt-2">
          Department of Paediatrics
        </h3>
        <h4 className="text-lg font-semibold text-white mt-3">
          SATS AI Co-Pilot — Paediatric Triage
        </h4>
      </div>

      {/* Login Form */}
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-4 shadow-2xl sm:rounded-lg sm:px-10 border border-gray-200">
          <div className="mb-6 text-center">
            <h2 className="text-2xl font-bold text-gray-900">
              Sign In
            </h2>
            <p className="mt-2 text-sm text-gray-600">
              Access the pediatric triage system
            </p>
          </div>

          <form className="space-y-6" onSubmit={handleSubmit}>
            {/* Username Field */}
            <div>
              <label htmlFor="username" className="form-label">
                Username
              </label>
              <div className="mt-1 relative">
                <input
                  id="username"
                  name="username"
                  type="text"
                  autoComplete="username"
                  required
                  value={formData.username}
                  onChange={handleChange}
                  className="form-input"
                  placeholder="Enter your username"
                  disabled={isLoading}
                />
                <div className="absolute inset-y-0 right-0 pr-3 flex items-center">
                  <svg className="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                </div>
              </div>
            </div>

            {/* Password Field */}
            <div>
              <label htmlFor="password" className="form-label">
                Password
              </label>
              <div className="mt-1 relative">
                <input
                  id="password"
                  name="password"
                  type={showPassword ? 'text' : 'password'}
                  autoComplete="current-password"
                  required
                  value={formData.password}
                  onChange={handleChange}
                  className="form-input pr-10"
                  placeholder="Enter your password"
                  disabled={isLoading}
                />
                <button
                  type="button"
                  className="absolute inset-y-0 right-0 pr-3 flex items-center"
                  onClick={() => setShowPassword(!showPassword)}
                  disabled={isLoading}
                >
                  {showPassword ? (
                    <svg className="h-5 w-5 text-gray-400 hover:text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L3 3m6.878 6.878L21 21" />
                    </svg>
                  ) : (
                    <svg className="h-5 w-5 text-gray-400 hover:text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                  )}
                </button>
              </div>
            </div>

            {/* Error Message */}
            {error && (
              <div className="alert-error animate-fade-in">
                <div className="flex items-center">
                  <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  {error}
                </div>
              </div>
            )}

            {/* Submit Button */}
            <div>
              <button
                type="submit"
                disabled={isLoading || !formData.username || !formData.password}
                className="btn-primary w-full flex justify-center py-3 text-base font-medium"
              >
                {isLoading ? (
                  <div className="flex items-center">
                    <div className="spinner w-5 h-5 mr-2"></div>
                    Signing in...
                  </div>
                ) : (
                  'Sign In'
                )}
              </button>
            </div>
          </form>

          {/* Demo Credentials */}
          <div className="mt-6">
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-300" />
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-2 bg-white text-gray-500">Demo Access</span>
              </div>
            </div>

            <div className="mt-4">
              <button
                type="button"
                onClick={handleDemoLogin}
                disabled={isLoading}
                className="btn-secondary w-full flex justify-center py-2 text-sm"
              >
                Use Demo Credentials
              </button>
              <div className="mt-2 text-xs text-gray-500 text-center">
                Username: <span className="font-mono">ajadmin</span> | 
                Password: <span className="font-mono">AJTriage2024!</span>
              </div>
            </div>
          </div>

          {/* System Info */}
          <div className="mt-6 text-center">
            <p className="text-xs text-gray-500">
              Clinical Trial Data Collection System
            </p>
            <p className="text-xs text-gray-400 mt-1">
              Secure • HIPAA Compliant • Research Use Only
            </p>
          </div>
        </div>

        {/* Footer */}
        <div className="mt-8 text-center">
          <p className="text-sm text-blue-100">
            © 2024 A.J. Institute of Medical Sciences and Research Centre
          </p>
          <p className="text-xs text-blue-200 mt-1">
            Department of Paediatrics - SATS AI Co-Pilot System
          </p>
        </div>
      </div>

      {/* Background Pattern */}
      <div className="fixed inset-0 -z-10 overflow-hidden">
        <div className="absolute -top-40 -right-32 w-80 h-80 bg-blue-400 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-pulse-slow"></div>
        <div className="absolute -bottom-40 -left-32 w-80 h-80 bg-purple-400 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-pulse-slow"></div>
      </div>
    </div>
  )
}

export default Login