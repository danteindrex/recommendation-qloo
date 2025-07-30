import React from 'react'
import { motion } from 'framer-motion'

interface LoaderProps {
  size?: 'sm' | 'md' | 'lg'
  message?: string
  fullScreen?: boolean
}

const Loader: React.FC<LoaderProps> = ({ size = 'md', message, fullScreen = false }) => {
  const sizeClasses = {
    sm: 'w-8 h-8',
    md: 'w-12 h-12',
    lg: 'w-16 h-16'
  }

  const dotSizeClasses = {
    sm: 'w-2 h-2',
    md: 'w-3 h-3',
    lg: 'w-4 h-4'
  }

  const loader = (
    <div className="flex flex-col items-center justify-center">
      <div className={`relative ${sizeClasses[size]}`}>
        <motion.div
          className={`absolute inset-0 rounded-full border-4 border-indigo-200`}
          animate={{ rotate: 360 }}
          transition={{ duration: 1.5, repeat: Infinity, ease: 'linear' }}
        />
        <motion.div
          className={`absolute inset-0 rounded-full border-4 border-transparent border-t-indigo-600`}
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
        />
        <div className="absolute inset-0 flex items-center justify-center">
          <motion.div
            className={`${dotSizeClasses[size]} bg-indigo-600 rounded-full`}
            animate={{ scale: [1, 1.2, 1] }}
            transition={{ duration: 1, repeat: Infinity }}
          />
        </div>
      </div>
      {message && (
        <motion.p
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="mt-4 text-gray-600 text-sm font-medium"
        >
          {message}
        </motion.p>
      )}
    </div>
  )

  if (fullScreen) {
    return (
      <div className="fixed inset-0 bg-white/80 backdrop-blur-sm z-50 flex items-center justify-center">
        {loader}
      </div>
    )
  }

  return loader
}

export default Loader