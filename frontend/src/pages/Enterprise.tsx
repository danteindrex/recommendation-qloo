import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { toast } from 'react-hot-toast'
import { Bar, Doughnut, Line, Radar } from 'react-chartjs-2'

// Chart.js imports are already registered in Analytics.tsx

interface TeamPerformance {
  team_id: string
  team_name: string
  members_count: number
  cultural_score: number
  diversity_index: number
  active_campaigns: number
  monthly_growth: number
  engagement_rate: number
  cultural_initiatives: number
  cross_cultural_projects: number
  top_cultural_insights: string[]
}

interface TeamAnalytics {
  organization_summary: {
    total_teams: number
    total_members: number
    average_cultural_score: number
    average_diversity_index: number
    total_active_campaigns: number
  }
  team_performance: TeamPerformance[]
  collaboration_matrix: Record<string, Record<string, number>>
  cultural_trends: Array<{
    trend: string
    adoption_rate: number
    leading_teams: string[]
    impact_score: number
  }>
}

interface MarketData {
  market_id: string
  market_name: string
  market_penetration: number
  growth_rate: number
  cultural_alignment_score: number
  trending_segments: string[]
  opportunity_score: number
  revenue_potential: number
  time_to_market: number
}

interface MarketIntelligence {
  executive_summary: {
    total_addressable_market: number
    serviceable_addressable_market: number
    average_market_growth: number
    high_opportunity_markets: string[]
    cultural_alignment_average: number
  }
  market_analysis: MarketData[]
  global_trends: Array<{
    trend_name: string
    global_impact: number
    affected_markets: string[]
    timeline: string
    business_opportunity: string
  }>
  competitive_landscape: {
    direct_competitors: number
    market_leaders: Array<{
      name: string
      market_share: number
      strength: string
    }>
    our_position: {
      market_share: number
      growth_trajectory: number
      key_advantages: string[]
    }
  }
}

interface CulturalInitiative {
  id: string
  title: string
  description: string
  status: string
  progress: number
  participating_teams: string[]
  budget?: number
  roi_metrics?: Record<string, number>
}

const Enterprise: React.FC = () => {
  const [activeTab, setActiveTab] = useState('overview')
  const [teamAnalytics, setTeamAnalytics] = useState<TeamAnalytics | null>(null)
  const [marketIntelligence, setMarketIntelligence] = useState<MarketIntelligence | null>(null)
  const [initiatives, setInitiatives] = useState<CulturalInitiative[]>([])
  const [isLoading, setIsLoading] = useState(false)

  useEffect(() => {
    if (activeTab === 'overview' || activeTab === 'teams') {
      fetchTeamAnalytics()
    }
    if (activeTab === 'overview' || activeTab === 'markets') {
      fetchMarketIntelligence()
    }
    if (activeTab === 'overview' || activeTab === 'initiatives') {
      fetchInitiatives()
    }
  }, [activeTab])

  const fetchTeamAnalytics = async () => {
    try {
      setIsLoading(true)
      const response = await fetch('http://localhost:8000/api/enterprise/team-analytics')
      if (!response.ok) throw new Error('Failed to fetch team analytics')
      const data = await response.json()
      setTeamAnalytics(data)
    } catch (error) {
      console.error('Error fetching team analytics:', error)
      toast.error('Failed to load team analytics')
    } finally {
      setIsLoading(false)
    }
  }

  const fetchMarketIntelligence = async () => {
    try {
      setIsLoading(true)
      const response = await fetch('http://localhost:8000/api/enterprise/market-intelligence')
      if (!response.ok) throw new Error('Failed to fetch market intelligence')
      const data = await response.json()
      setMarketIntelligence(data)
    } catch (error) {
      console.error('Error fetching market intelligence:', error)
      toast.error('Failed to load market intelligence')
    } finally {
      setIsLoading(false)
    }
  }

  const fetchInitiatives = async () => {
    try {
      setIsLoading(true)
      const response = await fetch('http://localhost:8000/api/enterprise/cultural-initiatives')
      if (!response.ok) throw new Error('Failed to fetch initiatives')
      const data = await response.json()
      setInitiatives(data.initiatives)
    } catch (error) {
      console.error('Error fetching initiatives:', error)
      toast.error('Failed to load cultural initiatives')
    } finally {
      setIsLoading(false)
    }
  }

  const generateReport = async (reportType: string) => {
    try {
      const response = await fetch(`http://localhost:8000/api/enterprise/generate-report?report_type=${reportType}`, {
        method: 'POST'
      })
      if (!response.ok) throw new Error('Failed to generate report')
      const data = await response.json()
      toast.success(`${reportType} report generated successfully!`)
      console.log('Report generated:', data)
    } catch (error) {
      console.error('Error generating report:', error)
      toast.error('Failed to generate report')
    }
  }

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

  const StatCard = ({ title, value, subtitle, icon, trend }: {
    title: string
    value: string | number
    subtitle: string
    icon: string
    trend?: number
  }) => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="card p-6"
    >
      <div className="flex items-center justify-between mb-4">
        <div className="text-3xl">{icon}</div>
        {trend && (
          <div className={`text-sm font-medium px-3 py-1 rounded-full ${
            trend > 0 ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
          }`}>
            {trend > 0 ? '+' : ''}{trend.toFixed(1)}%
          </div>
        )}
      </div>
      <h3 className="text-gray-600 text-sm">{title}</h3>
      <p className="text-2xl font-bold mt-1">{value}</p>
      <p className="text-xs text-gray-500 mt-2">{subtitle}</p>
    </motion.div>
  )

  return (
    <div className="min-h-screen">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-800 text-white">
        <div className="container py-12">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center"
          >
            <h1 className="text-4xl md:text-5xl font-bold mb-4">
              Enterprise Cultural Intelligence
            </h1>
            <p className="text-xl text-blue-100 mb-8 max-w-3xl mx-auto">
              Comprehensive analytics and insights for enterprise cultural intelligence operations
            </p>
          </motion.div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="bg-white border-b border-gray-200 sticky top-20 z-40">
        <div className="container">
          <nav className="flex space-x-8 py-4">
            {[
              { id: 'overview', label: 'Overview', icon: '📊' },
              { id: 'teams', label: 'Team Analytics', icon: '👥' },
              { id: 'markets', label: 'Market Intelligence', icon: '🌍' },
              { id: 'initiatives', label: 'Cultural Initiatives', icon: '🚀' },
              { id: 'reports', label: 'Reports', icon: '📈' }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-2 px-4 py-2 rounded-lg font-medium transition-colors ${
                  activeTab === tab.id
                    ? 'bg-blue-50 text-blue-600 border border-blue-200'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                }`}
              >
                <span>{tab.icon}</span>
                <span>{tab.label}</span>
              </button>
            ))}
          </nav>
        </div>
      </div>

      <div className="container py-8">
        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div className="space-y-8">
            {/* Executive Summary Cards */}
            {teamAnalytics && (
              <div className="grid md:grid-cols-4 gap-6">
                <StatCard
                  title="Total Teams"
                  value={teamAnalytics.organization_summary.total_teams}
                  subtitle="Active teams monitored"
                  icon="👥"
                />
                <StatCard
                  title="Team Members"
                  value={teamAnalytics.organization_summary.total_members}
                  subtitle="Across all cultural teams"
                  icon="👤"
                />
                <StatCard
                  title="Cultural Score"
                  value={`${teamAnalytics.organization_summary.average_cultural_score.toFixed(1)}%`}
                  subtitle="Organization average"
                  icon="🎯"
                />
                <StatCard
                  title="Active Campaigns"
                  value={teamAnalytics.organization_summary.total_active_campaigns}
                  subtitle="Cross-cultural campaigns"
                  icon="📢"
                />
              </div>
            )}

            {/* Market Overview */}
            {marketIntelligence && (
              <div className="grid md:grid-cols-2 gap-8">
                <motion.div
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="card p-6"
                >
                  <h3 className="text-xl font-semibold mb-4">Market Opportunities</h3>
                  <div className="h-80">
                    <Bar
                      data={{
                        labels: marketIntelligence.market_analysis.map(m => m.market_name),
                        datasets: [{
                          label: 'Growth Rate (%)',
                          data: marketIntelligence.market_analysis.map(m => m.growth_rate),
                          backgroundColor: 'rgba(59, 130, 246, 0.8)',
                        }, {
                          label: 'Opportunity Score',
                          data: marketIntelligence.market_analysis.map(m => m.opportunity_score),
                          backgroundColor: 'rgba(34, 197, 94, 0.8)',
                        }]
                      }}
                      options={chartOptions}
                    />
                  </div>
                </motion.div>

                <motion.div
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="card p-6"
                >
                  <h3 className="text-xl font-semibold mb-4">Team Performance</h3>
                  <div className="h-80">
                    <Radar
                      data={{
                        labels: teamAnalytics?.team_performance.map(t => t.team_name) || [],
                        datasets: [{
                          label: 'Cultural Score',
                          data: teamAnalytics?.team_performance.map(t => t.cultural_score) || [],
                          borderColor: 'rgb(59, 130, 246)',
                          backgroundColor: 'rgba(59, 130, 246, 0.2)',
                        }, {
                          label: 'Diversity Index',
                          data: teamAnalytics?.team_performance.map(t => t.diversity_index) || [],
                          borderColor: 'rgb(34, 197, 94)',
                          backgroundColor: 'rgba(34, 197, 94, 0.2)',
                        }]
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
            )}

            {/* Quick Actions */}
            <div className="card p-6">
              <h3 className="text-xl font-semibold mb-4">Quick Actions</h3>
              <div className="grid md:grid-cols-3 gap-4">
                <button
                  onClick={() => generateReport('comprehensive')}
                  className="btn btn-primary text-center"
                >
                  Generate Comprehensive Report
                </button>
                <button
                  onClick={() => generateReport('team_performance')}
                  className="btn btn-secondary text-center"
                >
                  Team Performance Report
                </button>
                <button
                  onClick={() => generateReport('market_analysis')}
                  className="btn bg-green-600 hover:bg-green-700 text-white text-center"
                >
                  Market Intelligence Report
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Team Analytics Tab */}
        {activeTab === 'teams' && teamAnalytics && (
          <div className="space-y-8">
            <h2 className="text-2xl font-bold">Team Cultural Analytics</h2>
            
            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
              {teamAnalytics.team_performance.map((team, index) => (
                <motion.div
                  key={team.team_id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="card p-6"
                >
                  <h3 className="font-semibold text-lg mb-2">{team.team_name}</h3>
                  <div className="text-sm text-gray-600 mb-4">{team.members_count} members</div>
                  
                  <div className="space-y-3">
                    <div>
                      <div className="flex justify-between text-sm">
                        <span>Cultural Score</span>
                        <span className="font-medium">{team.cultural_score}%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-blue-600 h-2 rounded-full" 
                          style={{ width: `${team.cultural_score}%` }}
                        ></div>
                      </div>
                    </div>
                    
                    <div>
                      <div className="flex justify-between text-sm">
                        <span>Diversity Index</span>
                        <span className="font-medium">{team.diversity_index}%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-green-600 h-2 rounded-full" 
                          style={{ width: `${team.diversity_index}%` }}
                        ></div>
                      </div>
                    </div>
                  </div>
                  
                  <div className="mt-4 pt-4 border-t border-gray-100">
                    <div className="text-xs text-gray-500 space-y-1">
                      <div>Active Campaigns: {team.active_campaigns}</div>
                      <div>Growth: +{team.monthly_growth.toFixed(1)}%</div>
                      <div>Engagement: {(team.engagement_rate * 100).toFixed(1)}%</div>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>

            {/* Cultural Trends */}
            <div className="card p-6">
              <h3 className="text-xl font-semibold mb-4">Cultural Trends Adoption</h3>
              <div className="space-y-4">
                {teamAnalytics.cultural_trends.map((trend, index) => (
                  <div key={index} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-medium">{trend.trend}</h4>
                      <span className="text-sm font-medium text-blue-600">
                        {(trend.adoption_rate * 100).toFixed(0)}% adoption
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
                      <div 
                        className="bg-blue-600 h-2 rounded-full" 
                        style={{ width: `${trend.adoption_rate * 100}%` }}
                      ></div>
                    </div>
                    <div className="flex items-center justify-between text-sm text-gray-600">
                      <span>Leading teams: {trend.leading_teams.join(', ')}</span>
                      <span>Impact: {trend.impact_score}/100</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Market Intelligence Tab */}
        {activeTab === 'markets' && marketIntelligence && (
          <div className="space-y-8">
            <h2 className="text-2xl font-bold">Global Market Intelligence</h2>
            
            {/* Executive Summary */}
            <div className="grid md:grid-cols-4 gap-6">
              <StatCard
                title="Total Addressable Market"
                value={`$${(marketIntelligence.executive_summary.total_addressable_market / 1000000000).toFixed(1)}B`}
                subtitle="Global market size"
                icon="💰"
              />
              <StatCard
                title="Serviceable Market"
                value={`$${(marketIntelligence.executive_summary.serviceable_addressable_market / 1000000000).toFixed(1)}B`}
                subtitle="Addressable opportunity"
                icon="🎯"
              />
              <StatCard
                title="Average Growth"
                value={`${marketIntelligence.executive_summary.average_market_growth.toFixed(1)}%`}
                subtitle="Cross-market average"
                icon="📈"
              />
              <StatCard
                title="Our Market Share"
                value={`${(marketIntelligence.competitive_landscape.our_position.market_share * 100).toFixed(1)}%`}
                subtitle="Current position"
                icon="🏆"
              />
            </div>

            {/* Market Analysis Grid */}
            <div className="grid md:grid-cols-2 gap-6">
              {marketIntelligence.market_analysis.map((market, index) => (
                <motion.div
                  key={market.market_id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="card p-6"
                >
                  <h3 className="font-semibold text-lg mb-4">{market.market_name}</h3>
                  
                  <div className="grid grid-cols-2 gap-4 mb-4">
                    <div>
                      <div className="text-sm text-gray-600">Penetration</div>
                      <div className="text-xl font-bold text-blue-600">{market.market_penetration}%</div>
                    </div>
                    <div>
                      <div className="text-sm text-gray-600">Growth Rate</div>
                      <div className="text-xl font-bold text-green-600">+{market.growth_rate}%</div>
                    </div>
                    <div>
                      <div className="text-sm text-gray-600">Opportunity</div>
                      <div className="text-xl font-bold text-purple-600">{market.opportunity_score}/100</div>
                    </div>
                    <div>
                      <div className="text-sm text-gray-600">Revenue Potential</div>
                      <div className="text-xl font-bold text-orange-600">
                        ${(market.revenue_potential / 1000000).toFixed(1)}M
                      </div>
                    </div>
                  </div>

                  <div>
                    <div className="text-sm text-gray-600 mb-2">Trending Segments:</div>
                    <div className="flex flex-wrap gap-2">
                      {market.trending_segments.map((segment, idx) => (
                        <span key={idx} className="px-2 py-1 bg-blue-100 text-blue-700 rounded-full text-xs">
                          {segment}
                        </span>
                      ))}
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>

            {/* Global Trends */}
            <div className="card p-6">
              <h3 className="text-xl font-semibold mb-4">Global Cultural Trends</h3>
              <div className="space-y-4">
                {marketIntelligence.global_trends.map((trend, index) => (
                  <div key={index} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-medium">{trend.trend_name}</h4>
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                        trend.business_opportunity === 'Very High' ? 'bg-green-100 text-green-700' :
                        trend.business_opportunity === 'High' ? 'bg-blue-100 text-blue-700' :
                        'bg-yellow-100 text-yellow-700'
                      }`}>
                        {trend.business_opportunity} Opportunity
                      </span>
                    </div>
                    <div className="flex items-center justify-between text-sm text-gray-600">
                      <span>Impact: {(trend.global_impact * 100).toFixed(0)}%</span>
                      <span>Timeline: {trend.timeline}</span>
                      <span>Markets: {trend.affected_markets.length}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Cultural Initiatives Tab */}
        {activeTab === 'initiatives' && (
          <div className="space-y-8">
            <h2 className="text-2xl font-bold">Cultural Initiatives</h2>
            
            <div className="space-y-6">
              {initiatives.map((initiative, index) => (
                <motion.div
                  key={initiative.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="card p-6"
                >
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex-1">
                      <h3 className="font-semibold text-lg mb-2">{initiative.title}</h3>
                      <p className="text-gray-600 mb-4">{initiative.description}</p>
                    </div>
                    <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                      initiative.status === 'active' ? 'bg-green-100 text-green-700' :
                      initiative.status === 'in_progress' ? 'bg-blue-100 text-blue-700' :
                      'bg-yellow-100 text-yellow-700'
                    }`}>
                      {initiative.status}
                    </span>
                  </div>
                  
                  <div className="mb-4">
                    <div className="flex justify-between text-sm mb-2">
                      <span>Progress</span>
                      <span className="font-medium">{(initiative.progress * 100).toFixed(0)}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-blue-600 h-2 rounded-full" 
                        style={{ width: `${initiative.progress * 100}%` }}
                      ></div>
                    </div>
                  </div>

                  <div className="flex items-center justify-between text-sm text-gray-600">
                    <div>
                      <span>Teams: </span>
                      {initiative.participating_teams.map((team, idx) => (
                        <span key={idx} className="bg-gray-100 px-2 py-1 rounded mr-1">
                          {team}
                        </span>
                      ))}
                    </div>
                    {initiative.budget && (
                      <div>Budget: ${initiative.budget.toLocaleString()}</div>
                    )}
                  </div>

                  {initiative.roi_metrics && (
                    <div className="mt-4 pt-4 border-t border-gray-100">
                      <div className="text-sm text-gray-600">ROI Metrics:</div>
                      <div className="grid grid-cols-3 gap-4 mt-2">
                        {Object.entries(initiative.roi_metrics).map(([key, value]) => (
                          <div key={key} className="text-center">
                            <div className="text-lg font-bold text-blue-600">+{value}%</div>
                            <div className="text-xs text-gray-500 capitalize">
                              {key.replace('_', ' ')}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </motion.div>
              ))}
            </div>
          </div>
        )}

        {/* Reports Tab */}
        {activeTab === 'reports' && (
          <div className="space-y-8">
            <h2 className="text-2xl font-bold">Enterprise Reports</h2>
            
            <div className="grid md:grid-cols-2 gap-8">
              <div className="card p-6">
                <h3 className="font-semibold text-lg mb-4">Available Reports</h3>
                <div className="space-y-4">
                  {[
                    {
                      type: 'comprehensive',
                      title: 'Comprehensive Enterprise Report',
                      description: 'Complete analysis including team performance, market intelligence, and strategic recommendations',
                      icon: '📊'
                    },
                    {
                      type: 'team_performance',
                      title: 'Team Performance Analysis',
                      description: 'Detailed cultural analytics and collaboration metrics for all teams',
                      icon: '👥'
                    },
                    {
                      type: 'market_analysis',
                      title: 'Global Market Intelligence',
                      description: 'Market opportunities, competitive landscape, and growth projections',
                      icon: '🌍'
                    },
                    {
                      type: 'cultural_trends',
                      title: 'Cultural Trends Report',
                      description: 'Emerging cultural trends and their business impact analysis',
                      icon: '📈'
                    }
                  ].map((report, index) => (
                    <div key={report.type} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex items-start justify-between">
                        <div className="flex items-start space-x-3">
                          <span className="text-2xl">{report.icon}</span>
                          <div>
                            <h4 className="font-medium">{report.title}</h4>
                            <p className="text-sm text-gray-600 mt-1">{report.description}</p>
                          </div>
                        </div>
                        <button
                          onClick={() => generateReport(report.type)}
                          className="btn btn-primary text-sm"
                        >
                          Generate
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="card p-6">
                <h3 className="font-semibold text-lg mb-4">Report History</h3>
                <div className="space-y-3">
                  {[
                    { name: 'Comprehensive Report - Q3 2024', date: '2024-07-15', size: '2.4 MB' },
                    { name: 'Team Performance - July 2024', date: '2024-07-01', size: '1.8 MB' },
                    { name: 'Market Intelligence - June 2024', date: '2024-06-30', size: '3.1 MB' }
                  ].map((report, index) => (
                    <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <div>
                        <div className="font-medium text-sm">{report.name}</div>
                        <div className="text-xs text-gray-500">{report.date} • {report.size}</div>
                      </div>
                      <button className="text-blue-600 hover:text-blue-700 text-sm">
                        Download
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default Enterprise