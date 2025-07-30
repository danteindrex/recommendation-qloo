import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Line, Bar, Doughnut, Radar } from 'react-chartjs-2'
import { analyticsWebSocket, useWebSocket } from '../services/websocket'
import { toast } from 'react-hot-toast'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  RadialLinearScale,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js'

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  RadialLinearScale,
  Title,
  Tooltip,
  Legend,
  Filler
)

interface AnalyticsData {
  culturalEvolution: {
    labels: string[]
    scores: number[]
  }
  categoryDistribution: {
    labels: string[]
    values: number[]
  }
  engagementMetrics: {
    labels: string[]
    spotify: number[]
    instagram: number[]
    tiktok: number[]
  }
  culturalRadar: {
    labels: string[]
    current: number[]
    previous: number[]
  }
}

const Analytics: React.FC = () => {
  const [timeRange, setTimeRange] = useState<'week' | 'month' | 'year'>('month')
  const [isLiveMode, setIsLiveMode] = useState(false)
  const userId = 'demo-user'
  const [analyticsData, setAnalyticsData] = useState<AnalyticsData>({
    culturalEvolution: {
      labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
      scores: [65, 68, 72, 78, 82, 87]
    },
    categoryDistribution: {
      labels: ['Music', 'Visual Arts', 'Literature', 'Culinary', 'Fashion', 'Film'],
      values: [35, 20, 15, 12, 10, 8]
    },
    engagementMetrics: {
      labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
      spotify: [120, 145, 98, 167, 189, 156, 201],
      instagram: [89, 67, 94, 123, 145, 178, 156],
      tiktok: [45, 56, 78, 89, 67, 90, 123]
    },
    culturalRadar: {
      labels: ['Innovation', 'Tradition', 'Diversity', 'Authenticity', 'Creativity', 'Community'],
      current: [85, 60, 92, 78, 88, 75],
      previous: [70, 65, 80, 70, 75, 68]
    }
  })

  // WebSocket handlers for real-time analytics
  const wsHandlers = {
    analytics_update: (data: any) => {
      console.log('Real-time analytics update:', data)
      
      // Update specific chart data based on update type
      if (data.type === 'cultural_score') {
        setAnalyticsData(prev => ({
          ...prev,
          culturalEvolution: {
            ...prev.culturalEvolution,
            scores: [...prev.culturalEvolution.scores.slice(1), data.value]
          }
        }))
        toast('Cultural score updated!', { icon: '📈' })
      } else if (data.type === 'engagement') {
        // Update engagement metrics
        const platform = data.platform
        if (platform) {
          setAnalyticsData(prev => {
            if (prev.engagementMetrics[platform]) {
              return {
                ...prev,
                engagementMetrics: {
                  ...prev.engagementMetrics,
                  [platform]: [...prev.engagementMetrics[platform].slice(1), data.value]
                }
              }
            }
            return prev
          })
        }
      } else if (data.type === 'category_update') {
        // Update category distribution
        toast('Category metrics updated!', { icon: '🎯' })
      }
    },
    analytics_connection_established: () => {
      toast.success('Live analytics connected!')
    }
  }

  // Use WebSocket hook for analytics
  const { subscribe, isConnected } = useWebSocket(
    analyticsWebSocket,
    'analytics-updates',
    userId,
    wsHandlers
  )

  useEffect(() => {
    if (userId && isLiveMode) {
      subscribe('analytics')
    }
  }, [isLiveMode, userId])

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: true,
        position: 'bottom' as const
      }
    }
  }

  const StatCard = ({ title, value, change, icon }: { title: string; value: string; change: number; icon: string }) => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="card"
      whileHover={{ y: -5, scale: 1.02 }}
    >
      <div className="flex items-center justify-between mb-4">
        <div className="text-3xl">{icon}</div>
        <div className={`text-sm font-medium px-3 py-1 rounded-full ${
          change > 0 ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'
        }`}>
          {change > 0 ? '+' : ''}{change}%
        </div>
      </div>
      <h3 className="text-gray-600 text-sm">{title}</h3>
      <p className="text-2xl font-bold mt-1">{value}</p>
    </motion.div>
  )

  return (
    <div className="min-h-screen">
      <div className="container py-12">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-12"
        >
          <h1 className="text-4xl font-bold mb-4">Cultural Analytics</h1>
          <p className="text-xl text-gray-600">
            Track your cultural journey with data-driven insights
          </p>
        </motion.div>

        {/* Controls Row */}
        <div className="flex flex-col sm:flex-row justify-between items-center mb-8 gap-4">
          {/* Time Range Selector */}
          <div className="card p-1">
            {(['week', 'month', 'year'] as const).map((range) => (
              <button
                key={range}
                onClick={() => setTimeRange(range)}
                className={`px-6 py-2 rounded-lg font-medium transition-all capitalize ${
                  timeRange === range
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                }`}
              >
                {range}
              </button>
            ))}
          </div>
          
          {/* Live Mode Toggle */}
          <div className="flex items-center space-x-3">
            <span className="text-sm font-medium text-gray-600">Live Mode</span>
            <button
              onClick={() => setIsLiveMode(!isLiveMode)}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                isLiveMode ? 'bg-blue-600' : 'bg-gray-200'
              }`}
            >
              <span className="sr-only">Enable live mode</span>
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  isLiveMode ? 'translate-x-6' : 'translate-x-1'
                }`}
              />
            </button>
            {isLiveMode && isConnected && (
              <span className="flex items-center text-green-600 text-sm">
                <span className="w-2 h-2 bg-green-600 rounded-full animate-pulse mr-1"></span>
                Connected
              </span>
            )}
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid md:grid-cols-4 gap-6 mb-12">
          <StatCard title="Cultural Score" value="87%" change={5} icon="🎯" />
          <StatCard title="Active Platforms" value="3/5" change={0} icon="🔗" />
          <StatCard title="Weekly Insights" value="23" change={15} icon="💡" />
          <StatCard title="Diversity Index" value="92%" change={8} icon="🌈" />
        </div>

        {/* Charts Grid */}
        <div className="grid lg:grid-cols-2 gap-8 mb-12">
          {/* Cultural Evolution Chart */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.1 }}
            className="card p-6"
          >
            <h3 className="text-xl font-semibold mb-6">Cultural Evolution</h3>
            <div className="h-80">
              <Line
                data={{
                  labels: analyticsData.culturalEvolution.labels,
                  datasets: [{
                    label: 'Cultural Score',
                    data: analyticsData.culturalEvolution.scores,
                    borderColor: 'rgb(59, 130, 246)',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    tension: 0.4,
                    fill: true
                  }]
                }}
                options={{
                  ...chartOptions,
                  scales: {
                    y: {
                      beginAtZero: true,
                      max: 100
                    }
                  }
                }}
              />
            </div>
          </motion.div>

          {/* Category Distribution */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.2 }}
            className="card p-6"
          >
            <h3 className="text-xl font-semibold mb-6">Category Distribution</h3>
            <div className="h-80">
              <Doughnut
                data={{
                  labels: analyticsData.categoryDistribution.labels,
                  datasets: [{
                    data: analyticsData.categoryDistribution.values,
                    backgroundColor: [
                      'rgba(59, 130, 246, 0.8)',
                      'rgba(236, 72, 153, 0.8)',
                      'rgba(245, 158, 11, 0.8)',
                      'rgba(16, 185, 129, 0.8)',
                      'rgba(139, 92, 246, 0.8)',
                      'rgba(239, 68, 68, 0.8)'
                    ],
                    borderWidth: 0
                  }]
                }}
                options={{
                  ...chartOptions,
                  plugins: {
                    ...chartOptions.plugins,
                    legend: {
                      ...chartOptions.plugins.legend,
                      position: 'right'
                    }
                  }
                }}
              />
            </div>
          </motion.div>

          {/* Platform Engagement */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.3 }}
            className="card p-6"
          >
            <h3 className="text-xl font-semibold mb-6">Platform Engagement</h3>
            <div className="h-80">
              <Bar
                data={{
                  labels: analyticsData.engagementMetrics.labels,
                  datasets: [
                    {
                      label: 'Spotify',
                      data: analyticsData.engagementMetrics.spotify,
                      backgroundColor: 'rgba(34, 197, 94, 0.8)'
                    },
                    {
                      label: 'Instagram',
                      data: analyticsData.engagementMetrics.instagram,
                      backgroundColor: 'rgba(219, 39, 119, 0.8)'
                    },
                    {
                      label: 'TikTok',
                      data: analyticsData.engagementMetrics.tiktok,
                      backgroundColor: 'rgba(0, 0, 0, 0.8)'
                    }
                  ]
                }}
                options={chartOptions}
              />
            </div>
          </motion.div>

          {/* Cultural Dimensions Radar */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.4 }}
            className="card p-6"
          >
            <h3 className="text-xl font-semibold mb-6">Cultural Dimensions</h3>
            <div className="h-80">
              <Radar
                data={{
                  labels: analyticsData.culturalRadar.labels,
                  datasets: [
                    {
                      label: 'Current',
                      data: analyticsData.culturalRadar.current,
                      borderColor: 'rgb(59, 130, 246)',
                      backgroundColor: 'rgba(59, 130, 246, 0.2)',
                      pointBackgroundColor: 'rgb(59, 130, 246)'
                    },
                    {
                      label: 'Previous Month',
                      data: analyticsData.culturalRadar.previous,
                      borderColor: 'rgb(156, 163, 175)',
                      backgroundColor: 'rgba(156, 163, 175, 0.1)',
                      pointBackgroundColor: 'rgb(156, 163, 175)'
                    }
                  ]
                }}
                options={{
                  ...chartOptions,
                  scales: {
                    r: {
                      beginAtZero: true,
                      max: 100
                    }
                  }
                }}
              />
            </div>
          </motion.div>
        </div>

        {/* Insights Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="card p-6"
        >
          <h3 className="text-xl font-semibold mb-6">Recent Insights</h3>
          <div className="space-y-4">
            {[
              {
                type: 'trend',
                title: 'Musical Taste Evolution',
                description: 'Your preference for electronic music has increased by 23% this month',
                icon: '📈',
                color: 'bg-green-100 text-green-700'
              },
              {
                type: 'milestone',
                title: 'Cultural Milestone Reached',
                description: 'You\'ve explored content from 15 different countries this month',
                icon: '🏆',
                color: 'bg-blue-100 text-blue-700'
              },
              {
                type: 'recommendation',
                title: 'Expand Your Horizons',
                description: 'Based on your patterns, exploring Latin Jazz could enrich your cultural profile',
                icon: '💡',
                color: 'bg-yellow-100 text-yellow-700'
              }
            ].map((insight, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.6 + index * 0.1 }}
                className="flex items-start space-x-4 p-4 rounded-lg bg-gray-50"
              >
                <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${insight.color}`}>
                  <span className="text-xl">{insight.icon}</span>
                </div>
                <div>
                  <h4 className="font-semibold">{insight.title}</h4>
                  <p className="text-gray-600 text-sm mt-1">{insight.description}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </div>
    </div>
  )
}

export default Analytics