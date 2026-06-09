import React, { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'

const Header = () => {
  const location = useLocation()
  const [isMenuOpen, setIsMenuOpen] = useState(false)

  const isActivePath = (path) => {
    return location.pathname === path
  }

  const navItems = [
    {
      path: '/',
      label: 'New Triage',
      icon: '🏥'
    },
    {
      path: '/history',
      label: 'Case History',
      icon: '📋'
    },
    {
      path: '/admin',
      label: 'Admin Dashboard',
      icon: '⚙️'
    }
  ]

  return (
    <header className="bg-white shadow-lg border-b border-gray-200">
      {/* Institution Header */}
      <div className="bg-[#1a2f5e] text-white py-3">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-lg font-bold leading-tight">
              A.J. INSTITUTE OF MEDICAL SCIENCES AND RESEARCH CENTRE
            </h1>
            <h2 className="text-sm font-medium opacity-90">
              Department of Paediatrics
            </h2>
            <h3 className="text-sm font-medium opacity-80">
              SATS AI Co-Pilot — Paediatric Triage
            </h3>
          </div>
        </div>
      </div>

      {/* Navigation Header */}
      <div className="bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo and Brand */}
            <div className="flex items-center">
              <Link to="/" className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-[#1a2f5e] rounded-full flex items-center justify-center">
                  <span className="text-white font-bold text-lg">AJ</span>
                </div>
                <div className="hidden sm:block">
                  <h1 className="text-xl font-bold text-gray-900">SATS AI</h1>
                  <p className="text-xs text-gray-600">Pediatric Triage System</p>
                </div>
              </Link>
            </div>

            {/* Desktop Navigation */}
            <nav className="hidden md:flex space-x-8">
              {navItems.map((item) => (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200 ${
                    isActivePath(item.path)
                      ? 'bg-[#1a2f5e] text-white'
                      : 'text-gray-700 hover:text-[#1a2f5e] hover:bg-gray-100'
                  }`}
                >
                  <span>{item.icon}</span>
                  <span>{item.label}</span>
                </Link>
              ))}
            </nav>

            {/* Mobile Menu Button */}
            <div className="md:hidden">
              <button
                onClick={() => setIsMenuOpen(!isMenuOpen)}
                className="p-2 rounded-md text-gray-600 hover:text-gray-900 hover:bg-gray-100"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              </button>

              {isMenuOpen && (
                <div className="absolute right-4 mt-2 w-48 bg-white rounded-md shadow-lg py-1 z-50 border border-gray-200">
                  {navItems.map((item) => (
                    <Link
                      key={item.path}
                      to={item.path}
                      onClick={() => setIsMenuOpen(false)}
                      className={`flex items-center space-x-2 px-4 py-2 text-sm hover:bg-gray-100 ${
                        isActivePath(item.path)
                          ? 'bg-gray-100 text-[#1a2f5e] font-medium'
                          : 'text-gray-700'
                      }`}
                    >
                      <span>{item.icon}</span>
                      <span>{item.label}</span>
                    </Link>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Click outside to close menu */}
      {isMenuOpen && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => setIsMenuOpen(false)}
        />
      )}
    </header>
  )
}

export default Header