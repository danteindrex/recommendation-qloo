import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useState, useEffect } from 'react'
import { Toaster } from 'react-hot-toast'
import Dashboard from './pages/Dashboard'
import Analytics from './pages/Analytics'
import Enterprise from './pages/Enterprise'
import Admin from './pages/Admin'
import CulturalIntelligence from './pages/CulturalIntelligence'

const queryClient = new QueryClient()

function Navigation() {
  const [isScrolled, setIsScrolled] = useState(false)
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)
  const location = useLocation()

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 10)
    }
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  useEffect(() => {
    setIsMobileMenuOpen(false)
  }, [location])

  const navLinks = [
    { path: '/cultural-intelligence', label: 'Platform' },
    { path: '/analytics', label: 'Analytics' },
    { path: '/enterprise', label: 'Enterprise' },
    { path: '/admin', label: 'Support' },
  ]

  const isActive = (path: string) => location.pathname === path

  return (
    <nav className={`fixed top-0 w-full z-50 transition-all ${
      isScrolled ? 'bg-white shadow-lg' : 'bg-white/95'
    } border-b border-gray-200`}>
      <div className="container">
        <div className="flex justify-between items-center py-4">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-blue-600 flex items-center justify-center text-white font-bold text-lg rounded-lg">
              C
            </div>
            <span className="text-xl font-bold">CulturalOS</span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-1">
            {navLinks.map((link) => (
              <Link
                key={link.path}
                to={link.path}
                className={`px-4 py-2 text-sm font-medium rounded-lg transition-colors ${
                  isActive(link.path)
                    ? 'bg-blue-50 text-blue-600'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                }`}
              >
                {link.label}
              </Link>
            ))}
          </div>

          {/* Actions */}
          <div className="hidden md:flex items-center space-x-3">
            <Link to="/admin" className="btn btn-primary">
              Contact
            </Link>
          </div>

          {/* Mobile Menu Button */}
          <button
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            className="md:hidden p-2 rounded-lg text-gray-600 hover:text-gray-900 hover:bg-gray-50 transition-colors"
          >
            <svg
              className="w-6 h-6"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              {isMobileMenuOpen ? (
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              ) : (
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 6h16M4 12h16M4 18h16"
                />
              )}
            </svg>
          </button>
        </div>

        {/* Mobile Menu */}
        {isMobileMenuOpen && (
          <div className="md:hidden py-4 border-t border-gray-200">
            <div className="flex flex-col space-y-1">
              {navLinks.map((link) => (
                <Link
                  key={link.path}
                  to={link.path}
                  className={`px-4 py-3 text-sm font-medium rounded-lg transition-colors ${
                    isActive(link.path)
                      ? 'bg-blue-50 text-blue-600'
                      : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                  }`}
                >
                  {link.label}
                </Link>
              ))}
              <div className="pt-4 px-4">
                <Link to="/admin" className="btn btn-primary w-full text-center">
                  Contact
                </Link>
              </div>
            </div>
          </div>
        )}
      </div>
    </nav>
  )
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <div className="App min-h-screen">
          <Navigation />
          <main className="pt-20">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/analytics" element={<Analytics />} />
              <Route path="/enterprise" element={<Enterprise />} />
              <Route path="/admin" element={<Admin />} />
              <Route path="/cultural-intelligence" element={<CulturalIntelligence />} />
            </Routes>
          </main>
          <Toaster 
            position="top-right"
            toastOptions={{
              duration: 4000,
              style: {
                background: '#1f2937',
                color: '#fff',
              },
              success: {
                style: {
                  background: '#10b981',
                },
              },
              error: {
                style: {
                  background: '#ef4444',
                },
              },
            }}
          />
        </div>
      </Router>
    </QueryClientProvider>
  )
}

export default App