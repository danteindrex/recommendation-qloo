import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { culturalWebSocket, useWebSocket } from '../services/websocket'
import { toast } from 'react-hot-toast'

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState({
    culturalScore: 0,
    connections: 0,
    insights: 0,
    trends: 0
  })
  const [realtimeUpdate, setRealtimeUpdate] = useState<any>(null)
  const userId = 'demo-user'

  // WebSocket handlers
  const wsHandlers = {
    cultural_insight: (data: any) => {
      console.log('Received cultural insight:', data)
      setRealtimeUpdate(data)
      toast('New cultural insight available!')
      setStats(prev => ({ ...prev, insights: prev.insights + 1 }))
    },
    notification: (data: any) => {
      console.log('Received notification:', data)
    },
    connection: (data: any) => {
      if (data.status === 'connected') {
        toast.success('Real-time updates connected')
      }
    }
  }

  const { subscribe } = useWebSocket(
    culturalWebSocket,
    'cultural-updates',
    userId,
    wsHandlers
  )

  useEffect(() => {
    const timer = setTimeout(() => {
      setStats({
        culturalScore: 87,
        connections: 4,
        insights: 156,
        trends: 23
      })
    }, 500)

    if (userId) {
      subscribe('all')
    }

    return () => clearTimeout(timer)
  }, [])

  const features = [
    {
      title: 'Cultural Intelligence',
      description: 'AI-powered cultural analysis and insights for global understanding',
      link: '/cultural-intelligence'
    },
    {
      title: 'Social Analytics', 
      description: 'Real-time social media integration and trend analysis across platforms',
      link: '/analytics'
    },
    {
      title: 'Enterprise Solutions',
      description: 'Scalable cultural intelligence solutions for enterprise organizations',
      link: '/enterprise'
    }
  ]

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="py-24">
        <div className="container">
          <div className="text-center mb-16">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
            >
              <h1 className="text-4xl md:text-6xl font-bold mb-6">
                Discover Your <span className="text-blue-600">Cultural Universe</span>
              </h1>
              <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
                Experience the future of cultural intelligence with advanced AI analytics, 
                real-time insights, and immersive visualizations.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Link to="/cultural-intelligence" className="btn btn-primary px-8 py-4 text-lg">
                  Get Started
                </Link>
                <Link to="/analytics" className="btn btn-secondary px-8 py-4 text-lg">
                  View Demo
                </Link>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-16 bg-gray-50">
        <div className="container">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">Real-Time Intelligence</h2>
            <p className="text-lg text-gray-600">Live cultural insights powered by advanced AI</p>
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            {[
              { label: "Cultural Score", value: stats.culturalScore, icon: "🧠" },
              { label: "Connections", value: stats.connections, icon: "🌐" },
              { label: "Insights Generated", value: stats.insights, icon: "✨" },
              { label: "Trends Tracked", value: stats.trends, icon: "📈" }
            ].map((stat, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                className="card text-center"
              >
                <div className="text-2xl mb-3">{stat.icon}</div>
                <div className="text-3xl font-bold text-gray-900 mb-1">
                  {stat.value.toLocaleString()}
                </div>
                <div className="text-sm text-gray-600 font-medium">
                  {stat.label}
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Real-time Update Notification */}
      {realtimeUpdate && (
        <motion.section 
          className="bg-blue-50 border-l-4 border-blue-600 py-6"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
        >
          <div className="container">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="text-2xl">✨</div>
                <div>
                  <p className="font-semibold text-blue-900">NEW CULTURAL INSIGHT AVAILABLE</p>
                  <p className="text-sm text-blue-700">Your cultural profile has been updated with new data</p>
                </div>
              </div>
              <Link to="/cultural-intelligence" className="btn btn-primary">
                View Now
              </Link>
            </div>
          </div>
        </motion.section>
      )}

      {/* Features Section */}
      <section className="py-20">
        <div className="container">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold mb-4">Our Solutions</h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Comprehensive cultural intelligence solutions designed to meet the challenges 
              of global understanding and social analytics.
            </p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                className="card hover:shadow-lg"
              >
                <h3 className="text-xl font-semibold mb-3">{feature.title}</h3>
                <p className="text-gray-600 mb-4 leading-relaxed">{feature.description}</p>
                <Link to={feature.link} className="btn btn-primary w-full">
                  Learn More
                </Link>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-blue-600 text-white">
        <div className="container text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <h2 className="text-3xl md:text-5xl font-bold mb-6">
              Ready to Transform Your <span className="text-blue-200">Cultural Understanding?</span>
            </h2>
            <p className="text-xl text-blue-100 mb-8 max-w-3xl mx-auto">
              Join organizations worldwide using CulturalOS to unlock the power of 
              cultural intelligence and drive meaningful global connections.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link to="/cultural-intelligence" className="btn bg-white text-blue-600 hover:bg-blue-50 px-8 py-4 text-lg">
                Get Started Today
              </Link>
              <Link to="/enterprise" className="btn border-white text-white hover:bg-white hover:text-blue-600 px-8 py-4 text-lg">
                Enterprise Solutions
              </Link>
            </div>
          </motion.div>
        </div>
      </section>
    </div>
  )
}

export default Dashboard