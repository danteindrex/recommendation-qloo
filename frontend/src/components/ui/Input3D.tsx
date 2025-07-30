import React, { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

interface Input3DProps {
  value: string
  onChange: (value: string) => void
  type?: 'text' | 'email' | 'password' | 'number' | 'tel' | 'url'
  placeholder?: string
  label?: string
  error?: string
  disabled?: boolean
  required?: boolean
  variant?: 'default' | 'glass' | 'elegant' | 'gradient'
  size?: 'sm' | 'md' | 'lg'
  icon?: React.ReactNode
  iconPosition?: 'left' | 'right'
  showPasswordToggle?: boolean
  autoComplete?: string
  className?: string
  'aria-label'?: string
  'aria-describedby'?: string
  onFocus?: () => void
  onBlur?: () => void
}

const Input3D: React.FC<Input3DProps> = ({
  value,
  onChange,
  type = 'text',
  placeholder,
  label,
  error,
  disabled = false,
  required = false,
  variant = 'default',
  size = 'md',
  icon,
  iconPosition = 'left',
  showPasswordToggle = false,
  autoComplete,
  className = '',
  'aria-label': ariaLabel,
  'aria-describedby': ariaDescribedBy,
  onFocus,
  onBlur
}) => {
  const [isFocused, setIsFocused] = useState(false);
  const [isHovered, setIsHovered] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [isFloating, setIsFloating] = useState(value.length > 0);
  const inputRef = useRef<HTMLInputElement>(null);

  const sizeStyles = {
    sm: {
      input: 'px-3 py-2 text-sm min-h-[36px]',
      label: 'text-xs',
      icon: 'w-4 h-4'
    },
    md: {
      input: 'px-4 py-3 text-base min-h-[44px]',
      label: 'text-sm',
      icon: 'w-5 h-5'
    },
    lg: {
      input: 'px-5 py-4 text-lg min-h-[52px]',
      label: 'text-base',
      icon: 'w-6 h-6'
    }
  };

  const variantStyles = {
    default: {
      container: 'bg-white border border-gray-300',
      containerFocused: 'border-blue-500 shadow-lg',
      containerError: 'border-red-500',
      input: 'bg-transparent text-gray-900 placeholder-gray-400',
      label: 'text-gray-600',
      labelFocused: 'text-blue-600',
      labelError: 'text-red-600'
    },
    glass: {
      container: 'bg-white/10 backdrop-blur-md border border-white/20',
      containerFocused: 'border-white/40 shadow-xl',
      containerError: 'border-red-400/60',
      input: 'bg-transparent text-white placeholder-white/60',
      label: 'text-white/80',
      labelFocused: 'text-white',
      labelError: 'text-red-300'
    },
    elegant: {
      container: 'bg-gradient-to-r from-white/90 to-white/70 backdrop-blur-lg border border-white/30',
      containerFocused: 'border-blue-400/60 shadow-2xl',
      containerError: 'border-red-400/60',
      input: 'bg-transparent text-gray-800 placeholder-gray-500',
      label: 'text-gray-700',
      labelFocused: 'text-blue-600',
      labelError: 'text-red-600'
    },
    gradient: {
      container: 'bg-gradient-to-r from-indigo-500/10 to-purple-500/10 border border-indigo-300/30',
      containerFocused: 'border-indigo-400/60 shadow-xl shadow-indigo-500/20',
      containerError: 'border-red-400/60',
      input: 'bg-transparent text-gray-900 placeholder-gray-500',
      label: 'text-indigo-700',
      labelFocused: 'text-indigo-600',
      labelError: 'text-red-600'
    }
  };

  useEffect(() => {
    setIsFloating(value.length > 0 || isFocused);
  }, [value, isFocused]);

  const handleFocus = () => {
    setIsFocused(true);
    onFocus?.();
  };

  const handleBlur = () => {
    setIsFocused(false);
    onBlur?.();
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onChange(e.target.value);
  };

  const togglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };

  const inputType = type === 'password' && showPassword ? 'text' : type;

  const containerClasses = `
    relative rounded-lg transition-all duration-300 transform-gpu
    ${variantStyles[variant].container}
    ${isFocused ? variantStyles[variant].containerFocused : ''}
    ${error ? variantStyles[variant].containerError : ''}
    ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-text'}
    ${isHovered && !disabled ? 'shadow-md' : ''}
  `;

  const inputClasses = `
    w-full ${sizeStyles[size].input} rounded-lg
    ${variantStyles[variant].input}
    ${icon && iconPosition === 'left' ? 'pl-10' : ''}
    ${icon && iconPosition === 'right' ? 'pr-10' : ''}
    ${showPasswordToggle && type === 'password' ? 'pr-10' : ''}
    border-0 outline-none resize-none
    transition-all duration-200
    ${disabled ? 'cursor-not-allowed' : ''}
  `;

  const labelClasses = `
    absolute left-4 transition-all duration-200 pointer-events-none
    ${sizeStyles[size].label}
    ${error ? variantStyles[variant].labelError : 
      isFocused ? variantStyles[variant].labelFocused : 
      variantStyles[variant].label}
    ${isFloating 
      ? 'top-2 transform scale-75 origin-top-left' 
      : `top-1/2 transform -translate-y-1/2 scale-100`}
  `;

  const EyeIcon = () => (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
    </svg>
  );

  const EyeOffIcon = () => (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L3 3m6.878 6.878L21 21" />
    </svg>
  );

  return (
    <div className={`relative ${className}`}>
      {/* Input Container */}
      <motion.div
        className={containerClasses}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
        onClick={() => inputRef.current?.focus()}
        style={{
          transform: `translateZ(${isFocused ? 4 : isHovered ? 2 : 0}px)`,
          boxShadow: isFocused 
            ? '0 8px 25px rgba(0,0,0,0.15), 0 0 0 3px rgba(59, 130, 246, 0.1)' 
            : isHovered 
              ? '0 4px 15px rgba(0,0,0,0.1)' 
              : '0 2px 8px rgba(0,0,0,0.05)'
        }}
        whileHover={!disabled ? { scale: 1.01 } : {}}
        whileFocus={{ scale: 1.02 }}
        transition={{ type: "spring", stiffness: 400, damping: 25 }}
      >
        {/* Left Icon */}
        {icon && iconPosition === 'left' && (
          <div className={`absolute left-3 top-1/2 transform -translate-y-1/2 ${sizeStyles[size].icon} text-gray-400`}>
            {icon}
          </div>
        )}

        {/* Input */}
        <input
          ref={inputRef}
          type={inputType}
          value={value}
          onChange={handleChange}
          onFocus={handleFocus}
          onBlur={handleBlur}
          disabled={disabled}
          required={required}
          autoComplete={autoComplete}
          className={inputClasses}
          placeholder={isFloating ? placeholder : ''}
          aria-label={ariaLabel || label}
          aria-describedby={ariaDescribedBy}
          aria-invalid={!!error}
        />

        {/* Floating Label */}
        {label && (
          <motion.label
            className={labelClasses}
            animate={{
              y: isFloating ? -8 : 0,
              scale: isFloating ? 0.75 : 1,
              color: error ? 'rgb(239, 68, 68)' : isFocused ? 'rgb(59, 130, 246)' : undefined
            }}
            transition={{ duration: 0.2, ease: "easeOut" }}
          >
            {label}
            {required && <span className="text-red-500 ml-1">*</span>}
          </motion.label>
        )}

        {/* Right Icon */}
        {icon && iconPosition === 'right' && (
          <div className={`absolute right-3 top-1/2 transform -translate-y-1/2 ${sizeStyles[size].icon} text-gray-400`}>
            {icon}
          </div>
        )}

        {/* Password Toggle */}
        {showPasswordToggle && type === 'password' && (
          <motion.button
            type="button"
            onClick={togglePasswordVisibility}
            className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
            aria-label={showPassword ? 'Hide password' : 'Show password'}
          >
            {showPassword ? <EyeOffIcon /> : <EyeIcon />}
          </motion.button>
        )}

        {/* Focus Ring Effect */}
        <AnimatePresence>
          {isFocused && (
            <motion.div
              className="absolute inset-0 rounded-lg pointer-events-none"
              style={{
                background: 'linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(147, 51, 234, 0.1))',
                filter: 'blur(1px)'
              }}
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              transition={{ duration: 0.2 }}
            />
          )}
        </AnimatePresence>

        {/* Shimmer Effect for elegant variant */}
        {variant === 'elegant' && isFocused && (
          <motion.div
            className="absolute inset-0 rounded-lg pointer-events-none overflow-hidden"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <motion.div
              className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent"
              initial={{ x: '-100%' }}
              animate={{ x: '100%' }}
              transition={{ duration: 1.5, ease: "easeInOut" }}
            />
          </motion.div>
        )}
      </motion.div>

      {/* Error Message */}
      <AnimatePresence>
        {error && (
          <motion.div
            className="mt-2 text-sm text-red-600 flex items-center"
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.2 }}
          >
            <svg className="w-4 h-4 mr-1 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
            {error}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default Input3D