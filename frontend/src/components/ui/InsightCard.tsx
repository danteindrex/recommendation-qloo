import React from 'react'
import { motion } from 'framer-motion'

interface InsightCardProps {
  type: 'pattern' | 'trend' | 'blind_spot' | 'recommendation'
  title: string
  description: string
  confidence?: number
  factors?: string[]
  recommendations?: string[]
  icon?: string
  color?: string
  delay?: number
}

const InsightCard: React.FC<InsightCardProps> = ({
  type,
  title,
  description,
  confidence,
  factors = [],
  recommendations = [],
  icon,
  color,
  delay = 0
}) => {
  const typeConfig = {
    pattern: {
      icon: icon || '🔄',
      bgColor: color || 'bg-indigo-100',
      textColor: 'text-indigo-700',
      borderColor: 'border-indigo-200'
    },
    trend: {
      icon: icon || '📈',
      bgColor: color || 'bg-green-100',
      textColor: 'text-green-700',
      borderColor: 'border-green-200'
    },
    blind_spot: {
      icon: icon || '👁️',
      bgColor: color || 'bg-amber-100',
      textColor: 'text-amber-700',
      borderColor: 'border-amber-200'
    },
    recommendation: {
      icon: icon || '💡',
      bgColor: color || 'bg-purple-100',
      textColor: 'text-purple-700',
      borderColor: 'border-purple-200'
    }
  }

  const config = typeConfig[type]

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.4 }}
      className="card hover:shadow-2xl"
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className={`w-12 h-12 rounded-xl ${config.bgColor} flex items-center justify-center text-2xl`}>
          {config.icon}
        </div>
        {confidence && (
          <div className="text-sm font-medium text-gray-500">
            {Math.round(confidence * 100)}% confidence
          </div>
        )}
      </div>

      {/* Content */}
      <h3 className="text-xl font-semibold mb-2 text-gray-800">{title}</h3>
      <p className="text-gray-600 mb-4">{description}</p>

      {/* Factors */}
      {factors.length > 0 && (
        <div className="mb-4">
          <p className="text-sm font-medium text-gray-700 mb-2">Key Factors:</p>
          <div className="flex flex-wrap gap-2">
            {factors.map((factor, i) => (
              <span
                key={i}
                className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium ${config.bgColor} ${config.textColor}`}
              >
                {factor}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Recommendations */}
      {recommendations.length > 0 && (
        <div>
          <p className="text-sm font-medium text-gray-700 mb-2">Recommendations:</p>
          <ul className="space-y-2">
            {recommendations.map((rec, i) => (
              <li key={i} className="flex items-start">
                <span className={`${config.textColor} mr-2 mt-0.5`}>•</span>
                <span className="text-sm text-gray-600">{rec}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Progress Bar (for trends) */}
      {type === 'trend' && confidence && (
        <div className="mt-4">
          <div className="w-full bg-gray-200 rounded-full h-2">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${confidence * 100}%` }}
              transition={{ delay: delay + 0.3, duration: 0.8 }}
              className="bg-gradient-to-r from-green-500 to-emerald-500 h-2 rounded-full"
            />
          </div>
        </div>
      )}
    </motion.div>
  )
}

export default InsightCard