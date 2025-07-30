import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { toast } from 'react-hot-toast'

interface User {
  id: string
  name: string
  email: string
  location: string
  joinDate: string
  status: 'active' | 'inactive'
}

interface CulturalData {
  culturalScore: number
  diversityIndex: number
  platforms: {
    spotify: { connected: boolean; tracks: number; genres: number }
    instagram: { connected: boolean; posts: number; engagement: number }
    tiktok: { connected: boolean; videos: number; views: number }
  }
  predictions: {
    nextTrend: string
    probability: number
    timeframe: string
  }[]
  insights: {
    category: string
    finding: string
    confidence: number
  }[]
}

interface TodoItem {
  category: string
  priority: string
  title: string
  description: string
  estimated_time: string
  cultural_impact: number
  specific_actions: string[]
  due_date: string
  reasoning: string
}

interface TodoAnalysis {
  user_id: string
  analysis_type: string
  total_recommendations: number
  todos: TodoItem[]
  analysis_metadata: {
    based_on_days: number
    listening_patterns_analyzed: number
    cultural_score_impact: number
    estimated_total_time: number
    generated_at: string
  }
}

const CulturalIntelligence: React.FC = () => {
  const [selectedUser, setSelectedUser] = useState<User | null>(null)
  const [culturalData, setCulturalData] = useState<CulturalData | null>(null)
  const [todoAnalysis, setTodoAnalysis] = useState<TodoAnalysis | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [isLoadingTodos, setIsLoadingTodos] = useState(false)
  const [activeSection, setActiveSection] = useState('overview')

  const [users, setUsers] = useState<User[]>([])

  // Fetch users on component mount
  useEffect(() => {
    const fetchUsers = async () => {
      try {
        console.log('Fetching users from:', 'http://localhost:8000/api/cultural-mock/users')
        const response = await fetch('http://localhost:8000/api/cultural-mock/users')
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }
        const userData = await response.json()
        console.log('Users fetched successfully:', userData)
        setUsers(userData)
      } catch (error) {
        console.error('Failed to fetch users:', error)
        toast.error('Failed to load users')
      }
    }
    fetchUsers()
  }, [])

  const fetchUserData = async (user: User) => {
    console.log('Fetching data for user:', user)
    setIsLoading(true)
    setSelectedUser(user)
    
    try {
      const url = `http://localhost:8000/api/cultural-mock/analyze/${user.id}`
      console.log('Fetching from URL:', url)
      const response = await fetch(url)
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const data = await response.json()
      console.log('Cultural data received:', data)
      
      setCulturalData({
        culturalScore: data.cultural_score,
        diversityIndex: data.diversity_index,
        platforms: data.platforms,
        predictions: data.predictions.map((p: any) => ({
          nextTrend: p.nextTrend,
          probability: p.probability,
          timeframe: p.timeframe
        })),
        insights: data.insights.map((i: any) => ({
          category: i.category,
          finding: i.finding,
          confidence: i.confidence
        }))
      })
      
      setIsLoading(false)
      toast.success(`Loaded real data for ${user.name}`)
    } catch (error) {
      console.error('Failed to fetch user data:', error)
      setIsLoading(false)
      toast.error('Failed to load user data')
    }
  }

  const fetchTodoAnalysis = async (user: User) => {
    setIsLoadingTodos(true)
    
    try {
      const response = await fetch(`http://localhost:8000/api/cultural-mock/todo-analysis/${user.id}`, {
        method: 'POST'
      })
      if (!response.ok) {
        throw new Error('Failed to fetch todo analysis')
      }
      
      const data = await response.json()
      setTodoAnalysis(data)
      toast.success('Generated music-based todos!')
    } catch (error) {
      console.error('Failed to fetch todo analysis:', error)
      toast.error('Failed to generate todos')
    }
    
    setIsLoadingTodos(false)
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="container py-6">
          <h1 className="text-2xl font-semibold">Cultural Intelligence</h1>
          <p className="mt-1 text-sm text-gray-600">
            Analyze user cultural profiles and predict behavioral patterns
          </p>
        </div>
      </div>

      <div className="container py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Sidebar - User List */}
          <div className="lg:col-span-1">
            <div className="card">
              <div className="p-6">
                <h3 className="text-lg font-medium mb-4">Users</h3>
                <div className="space-y-3">
                  {users.map((user) => (
                    <div
                      key={user.id}
                      onClick={() => fetchUserData(user)}
                      className={`p-3 rounded-lg cursor-pointer transition-colors ${
                        selectedUser?.id === user.id
                          ? 'bg-blue-50 border border-blue-200'
                          : 'hover:bg-gray-50 border border-transparent'
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-sm font-medium">{user.name}</p>
                          <p className="text-xs text-gray-500">{user.location}</p>
                        </div>
                        <div className={`w-2 h-2 rounded-full ${
                          user.status === 'active' ? 'bg-green-400' : 'bg-gray-300'
                        }`}></div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Main Content */}
          <div className="lg:col-span-3">
            {!selectedUser ? (
              <div className="card">
                <div className="px-4 py-12 text-center">
                  <div className="mx-auto h-12 w-12 text-gray-400 mb-4">
                    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                    </svg>
                  </div>
                  <h3 className="mt-2 text-sm font-medium">No user selected</h3>
                  <p className="mt-1 text-sm text-gray-500">
                    Select a user from the sidebar to view their cultural intelligence profile.
                  </p>
                </div>
              </div>
            ) : isLoading ? (
              <div className="card">
                <div className="px-4 py-12 text-center">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
                  <h3 className="mt-4 text-sm font-medium">Analyzing cultural profile...</h3>
                  <p className="mt-1 text-sm text-gray-600">Processing data from connected platforms</p>
                </div>
              </div>
            ) : (
              <div className="space-y-6">
                {/* User Header */}
                <div className="card">
                  <div className="px-4 py-5 sm:p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <h2 className="text-xl font-semibold">{selectedUser.name}</h2>
                        <p className="text-sm text-gray-600">{selectedUser.email}</p>
                        <p className="text-sm text-gray-600">{selectedUser.location}</p>
                      </div>
                      <div className="text-right">
                        <p className="text-sm text-gray-500">Member since</p>
                        <p className="text-sm font-medium">{selectedUser.joinDate}</p>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Navigation Tabs */}
                <div className="card">
                  <div className="border-b border-gray-200">
                    <nav className="-mb-px flex space-x-8 px-6">
                      {['overview', 'platforms', 'predictions', 'insights', 'todos'].map((section) => (
                        <button
                          key={section}
                          onClick={() => setActiveSection(section)}
                          className={`py-4 px-1 border-b-2 font-medium text-sm ${
                            activeSection === section
                              ? 'border-blue-600 text-blue-600'
                              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                          }`}
                        >
                          {section.charAt(0).toUpperCase() + section.slice(1)}
                        </button>
                      ))}
                    </nav>
                  </div>

                  <div className="p-6">
                    {activeSection === 'overview' && (
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div className="bg-gray-50 p-4 rounded-lg">
                          <h4 className="text-sm font-medium text-gray-700 mb-2">Cultural Score</h4>
                          <div className="text-3xl font-bold text-blue-600">{culturalData?.culturalScore}%</div>
                          <p className="text-xs text-gray-500 mt-1">Based on platform analysis</p>
                        </div>
                        <div className="bg-gray-50 p-4 rounded-lg">
                          <h4 className="text-sm font-medium text-gray-700 mb-2">Diversity Index</h4>
                          <div className="text-3xl font-bold text-green-600">{culturalData?.diversityIndex}%</div>
                          <p className="text-xs text-gray-500 mt-1">Content variety score</p>
                        </div>
                      </div>
                    )}

                    {activeSection === 'platforms' && (
                      <div className="space-y-4">
                        {Object.entries(culturalData?.platforms || {}).map(([platform, data]) => (
                          <div key={platform} className="bg-gray-50 border border-gray-200 p-4 rounded-lg">
                            <div className="flex items-center justify-between mb-3">
                              <div className="flex items-center space-x-3">
                                <div className="text-lg">
                                  {platform === 'spotify' && '🎵'}
                                  {platform === 'instagram' && '📸'}
                                  {platform === 'tiktok' && '🎬'}
                                </div>
                                <h4 className="font-medium capitalize">{platform}</h4>
                              </div>
                              <div className={`px-2 py-1 rounded-full text-xs font-medium ${
                                data.connected 
                                  ? 'bg-green-100 text-green-700' 
                                  : 'bg-gray-100 text-gray-500'
                              }`}>
                                {data.connected ? 'Connected' : 'Disconnected'}
                              </div>
                            </div>
                            {data.connected && (
                              <div className="grid grid-cols-3 gap-4 text-sm">
                                {platform === 'spotify' && (
                                  <>
                                    <div><span className="text-gray-500">Tracks:</span> <span>{data.tracks}</span></div>
                                    <div><span className="text-gray-500">Genres:</span> <span>{data.genres}</span></div>
                                  </>
                                )}
                                {platform === 'instagram' && (
                                  <>
                                    <div><span className="text-gray-500">Posts:</span> <span>{data.posts}</span></div>
                                    <div><span className="text-gray-500">Engagement:</span> <span>{data.engagement}%</span></div>
                                  </>
                                )}
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    )}

                    {activeSection === 'predictions' && (
                      <div className="space-y-4">
                        {culturalData?.predictions.map((prediction, index) => (
                          <div key={index} className="bg-gray-50 border border-gray-200 p-4 rounded-lg">
                            <div className="flex items-center justify-between mb-2">
                              <h4 className="font-medium">{prediction.nextTrend}</h4>
                              <span className="text-sm font-medium text-green-600">{prediction.probability}%</span>
                            </div>
                            <p className="text-sm text-gray-600">Expected in {prediction.timeframe}</p>
                            <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
                              <div 
                                className="bg-gradient-to-r from-green-400 to-blue-500 h-2 rounded-full" 
                                style={{ width: `${prediction.probability}%` }}
                              ></div>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}

                    {activeSection === 'insights' && (
                      <div className="space-y-4">
                        {culturalData?.insights.map((insight, index) => (
                          <div key={index} className="bg-gray-50 border border-gray-200 p-4 rounded-lg">
                            <div className="flex items-center justify-between mb-2">
                              <h4 className="font-medium">{insight.category}</h4>
                              <span className="text-sm font-medium text-blue-600">{insight.confidence}% confidence</span>
                            </div>
                            <p className="text-sm text-gray-600">{insight.finding}</p>
                          </div>
                        ))}
                      </div>
                    )}

                    {activeSection === 'todos' && (
                      <div className="space-y-6">
                        <div className="flex items-center justify-between">
                          <h4 className="text-lg font-medium">Music-Based Cultural Todos</h4>
                          <button
                            onClick={() => selectedUser && fetchTodoAnalysis(selectedUser)}
                            disabled={isLoadingTodos}
                            className="btn btn-primary text-sm"
                          >
                            {isLoadingTodos ? 'Generating...' : 'Generate New Todos'}
                          </button>
                        </div>
                        
                        {todoAnalysis ? (
                          <div className="space-y-6">
                            {/* Analysis Summary */}
                            <div className="bg-blue-50 border border-blue-200 p-4 rounded-lg">
                              <h5 className="font-medium text-blue-900 mb-2">Analysis Summary</h5>
                              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                                <div>
                                  <span className="text-blue-700">Total Todos:</span>
                                  <div className="font-bold text-blue-900">{todoAnalysis.total_recommendations}</div>
                                </div>
                                <div>
                                  <span className="text-blue-700">Total Time:</span>
                                  <div className="font-bold text-blue-900">{todoAnalysis.analysis_metadata.estimated_total_time} min</div>
                                </div>
                                <div>
                                  <span className="text-blue-700">Score Impact:</span>
                                  <div className="font-bold text-blue-900">+{todoAnalysis.analysis_metadata.cultural_score_impact} pts</div>
                                </div>
                                <div>
                                  <span className="text-blue-700">Songs Analyzed:</span>
                                  <div className="font-bold text-blue-900">{todoAnalysis.analysis_metadata.listening_patterns_analyzed}</div>
                                </div>
                              </div>
                            </div>

                            {/* Todo Items */}
                            <div className="space-y-4">
                              {todoAnalysis.todos.map((todo, index) => (
                                <div key={index} className="bg-white border border-gray-200 p-6 rounded-lg hover:shadow-md transition-shadow">
                                  <div className="flex items-start justify-between mb-4">
                                    <div className="flex-1">
                                      <div className="flex items-center gap-3 mb-2">
                                        <h5 className="font-semibold text-lg">{todo.title}</h5>
                                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                                          todo.priority === 'high' ? 'bg-red-100 text-red-700' :
                                          todo.priority === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                                          'bg-green-100 text-green-700'
                                        }`}>
                                          {todo.priority} priority
                                        </span>
                                        <span className="px-2 py-1 bg-gray-100 text-gray-700 rounded-full text-xs">
                                          {todo.category}
                                        </span>
                                      </div>
                                      <p className="text-gray-600 mb-3">{todo.description}</p>
                                    </div>
                                    <div className="text-right ml-4">
                                      <div className="text-sm text-gray-500">Cultural Impact</div>
                                      <div className="text-2xl font-bold text-blue-600">{todo.cultural_impact}%</div>
                                    </div>
                                  </div>
                                  
                                  <div className="mb-4">
                                    <h6 className="font-medium text-sm text-gray-700 mb-2">Specific Actions:</h6>
                                    <ul className="space-y-1">
                                      {todo.specific_actions.map((action, actionIndex) => (
                                        <li key={actionIndex} className="flex items-center text-sm text-gray-600">
                                          <span className="w-1.5 h-1.5 bg-blue-500 rounded-full mr-2"></span>
                                          {action}
                                        </li>
                                      ))}
                                    </ul>
                                  </div>
                                  
                                  <div className="flex items-center justify-between text-sm">
                                    <div className="flex items-center gap-4">
                                      <span className="text-gray-500">
                                        ⏱️ {todo.estimated_time}
                                      </span>
                                      <span className="text-gray-500">
                                        📅 Due: {new Date(todo.due_date).toLocaleDateString()}
                                      </span>
                                    </div>
                                    <button className="btn btn-primary text-sm py-1 px-3">
                                      Mark Complete
                                    </button>
                                  </div>
                                  
                                  <div className="mt-3 pt-3 border-t border-gray-100">
                                    <p className="text-xs text-gray-500 italic">{todo.reasoning}</p>
                                  </div>
                                </div>
                              ))}
                            </div>
                          </div>
                        ) : (
                          <div className="text-center py-12">
                            <div className="text-4xl mb-4">🎵</div>
                            <h5 className="font-medium text-gray-700 mb-2">No Todo Analysis Generated</h5>
                            <p className="text-gray-500 mb-4">
                              Generate personalized cultural todos based on {selectedUser?.name}'s music listening history
                            </p>
                            <button
                              onClick={() => selectedUser && fetchTodoAnalysis(selectedUser)}
                              className="btn btn-primary"
                              disabled={isLoadingTodos}
                            >
                              {isLoadingTodos ? 'Analyzing...' : 'Generate Music Todos'}
                            </button>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default CulturalIntelligence