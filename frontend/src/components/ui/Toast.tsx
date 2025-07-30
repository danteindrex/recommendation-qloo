import React, { useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

export interface ToastProps {
  id: string
  message: string
  type?: 'success' | 'error' | 'warning' | 'info'
  duration?: number
  onClose: (id: string) => void
}

const Toast: React.FC<ToastProps> = ({
  id,
  message,
  type = 'info',
  duration = 5000,
  onClose
}) => {
  useEffect(() => {
    const timer = setTimeout(() => {
      onClose(id)
    }, duration)

    return () => clearTimeout(timer)
  }, [id, duration, onClose])

  const typeStyles = {
    success: {
      bg: 'bg-green-50',
      border: 'border-green-200',
      text: 'text-green-800',
      icon: '✅'
    },
    error: {
      bg: 'bg-red-50',
      border: 'border-red-200',
      text: 'text-red-800',
      icon: '❌'
    },
    warning: {
      bg: 'bg-amber-50',
      border: 'border-amber-200',
      text: 'text-amber-800',
      icon: '⚠️'
    },
    info: {
      bg: 'bg-blue-50',
      border: 'border-blue-200',
      text: 'text-blue-800',
      icon: 'ℹ️'
    }
  }

  const style = typeStyles[type]

  return (
    <motion.div
      initial={{ opacity: 0, x: 100, scale: 0.8 }}
      animate={{ opacity: 1, x: 0, scale: 1 }}
      exit={{ opacity: 0, x: 100, scale: 0.8 }}
      className={`flex items-center gap-3 p-4 rounded-lg border ${style.bg} ${style.border} ${style.text} shadow-lg min-w-[300px] max-w-md`}
    >
      <span className="text-2xl">{style.icon}</span>
      <p className="flex-1 font-medium">{message}</p>
      <button
        onClick={() => onClose(id)}
        className="p-1 rounded hover:bg-black/10 transition-colors"
      >
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </motion.div>
  )
}

// Toast Container Component
export const ToastContainer: React.FC<{ toasts: ToastProps[] }> = ({ toasts }) => {
  return (
    <div className="fixed top-4 right-4 z-50 space-y-2">
      <AnimatePresence>
        {toasts.map((toast) => (
          <Toast key={toast.id} {...toast} />
        ))}
      </AnimatePresence>
    </div>
  )
}

// Hook for managing toasts
export const useToast = () => {
  const [toasts, setToasts] = React.useState<ToastProps[]>([])

  const addToast = (toast: Omit<ToastProps, 'id' | 'onClose'>) => {
    const id = Date.now().toString()
    setToasts((prev) => [...prev, { ...toast, id, onClose: removeToast }])
  }

  const removeToast = (id: string) => {
    setToasts((prev) => prev.filter((toast) => toast.id !== id))
  }

  return { toasts, addToast, removeToast }
}

export default Toast