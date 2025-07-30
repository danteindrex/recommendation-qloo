import React, { useState } from 'react'
import { motion } from 'framer-motion'
import axios from 'axios'

interface SocialConnectButtonProps {
  platform: 'spotify' | 'instagram' | 'tiktok'
  isConnected: boolean
  lastSync?: string | null
  onConnectionChange?: (connected: boolean) => void
}

const SocialConnectButton: React.FC<SocialConnectButtonProps> = ({
  platform,
  isConnected,
  lastSync,
  onConnectionChange
}) => {
  const [isLoading, setIsLoading] = useState(false)

  const platformConfig = {
    spotify: {
      name: 'Spotify',
      icon: '🎵',
      color: 'from-green-500 to-green-600',
      hoverColor: 'hover:from-green-600 hover:to-green-700',
      bgColor: 'bg-green-500'
    },
    instagram: {
      name: 'Instagram',
      icon: '📸',
      color: 'from-purple-500 to-pink-500',
      hoverColor: 'hover:from-purple-600 hover:to-pink-600',
      bgColor: 'bg-gradient-to-r from-purple-500 to-pink-500'
    },
    tiktok: {
      name: 'TikTok',
      icon: '🎬',
      color: 'from-gray-900 to-gray-700',
      hoverColor: 'hover:from-black hover:to-gray-800',
      bgColor: 'bg-gray-900'
    }
  }

  const config = platformConfig[platform]

  const handleConnect = async () => {
    setIsLoading(true)
    try {
      const response = await axios.get(
        `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/social-media/oauth/${platform}/url`,
        {
          params: {
            redirect_uri: `${window.location.origin}/social/callback/${platform}`,
            state: window.crypto.randomUUID()
          },
          headers: {
            Authorization: `Bearer ${localStorage.getItem('access_token')}`
          }
        }
      )

      // Redirect to OAuth URL
      window.location.href = response.data.oauth_url
    } catch (error) {
      console.error('Failed to initiate OAuth:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleDisconnect = async () => {
    setIsLoading(true)
    try {
      await axios.delete(
        `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/social-media/connections/${platform}`,
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('access_token')}`
          }
        }
      )
      onConnectionChange?.(false)
    } catch (error) {
      console.error('Failed to disconnect:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleSync = async () => {
    setIsLoading(true)
    try {
      await axios.post(
        `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/social-media/sync/${platform}`,
        {},
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('access_token')}`
          }
        }
      )
      onConnectionChange?.(true)
    } catch (error) {
      console.error('Failed to sync:', error)
    } finally {
      setIsLoading(false)
    }
  }

  if (isConnected) {
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className={`relative overflow-hidden rounded-xl p-6 text-white bg-gradient-to-br ${config.color}`}
      >
        <div className="relative z-10">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-3">
              <span className="text-3xl">{config.icon}</span>
              <div>
                <h3 className="text-lg font-semibold">{config.name}</h3>
                <p className="text-sm opacity-90">Connected</p>
              </div>
            </div>
            <div className="w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
          </div>
          
          {lastSync && (
            <p className="text-xs opacity-75 mb-4">Last sync: {new Date(lastSync).toLocaleDateString()}</p>
          )}
          
          <div className="flex space-x-2">
            <button
              onClick={handleSync}
              disabled={isLoading}
              className="flex-1 bg-white/20 hover:bg-white/30 px-4 py-2 rounded-lg text-sm font-medium transition-colors disabled:opacity-50"
            >
              {isLoading ? 'Syncing...' : 'Sync Now'}
            </button>
            <button
              onClick={handleDisconnect}
              disabled={isLoading}
              className="bg-white/10 hover:bg-white/20 px-4 py-2 rounded-lg text-sm font-medium transition-colors disabled:opacity-50"
            >
              Disconnect
            </button>
          </div>
        </div>
        
        <div className="absolute -bottom-4 -right-4 text-8xl opacity-10">
          {config.icon}
        </div>
      </motion.div>
    )
  }

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      className="bg-gray-100 rounded-xl p-6"
    >
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className={`w-12 h-12 rounded-xl ${config.bgColor} flex items-center justify-center text-2xl text-white`}>
            {config.icon}
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-800">{config.name}</h3>
            <p className="text-sm text-gray-500">Not connected</p>
          </div>
        </div>
      </div>
      
      <button
        onClick={handleConnect}
        disabled={isLoading}
        className={`w-full bg-gradient-to-r ${config.color} ${config.hoverColor} text-white font-medium py-3 rounded-lg transition-all transform hover:scale-105 disabled:opacity-50 disabled:hover:scale-100`}
      >
        {isLoading ? (
          <span className="flex items-center justify-center">
            <span className="spinner mr-2"></span>
            Connecting...
          </span>
        ) : (
          'Connect Account'
        )}
      </button>
    </motion.div>
  )
}

export default SocialConnectButton