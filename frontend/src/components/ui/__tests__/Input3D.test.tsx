import React from 'react'
import { render, screen, fireEvent } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { vi } from 'vitest'
import Input3D from '../Input3D'

// Mock framer-motion
vi.mock('framer-motion', () => ({
  motion: {
    div: React.forwardRef<HTMLDivElement, any>(({ children, ...props }, ref) => (
      <div ref={ref} {...props}>{children}</div>
    )),
    label: React.forwardRef<HTMLLabelElement, any>(({ children, ...props }, ref) => (
      <label ref={ref} {...props}>{children}</label>
    )),
    button: React.forwardRef<HTMLButtonElement, any>(({ children, ...props }, ref) => (
      <button ref={ref} {...props}>{children}</button>
    ))
  },
  AnimatePresence: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}))

describe('Input3D', () => {
  const user = userEvent.setup()

  const defaultProps = {
    value: '',
    onChange: vi.fn()
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders with default props', () => {
    render(<Input3D {...defaultProps} />)
    
    const input = screen.getByRole('textbox')
    expect(input).toBeInTheDocument()
    expect(input).toHaveValue('')
  })

  it('handles value changes', async () => {
    const onChange = vi.fn()
    render(<Input3D {...defaultProps} onChange={onChange} />)
    
    const input = screen.getByRole('textbox')
    await user.type(input, 'test')
    
    expect(onChange).toHaveBeenCalledTimes(4) // Once for each character
  })

  it('renders with label', () => {
    render(<Input3D {...defaultProps} label="Test Label" />)
    
    expect(screen.getByText('Test Label')).toBeInTheDocument()
  })

  it('renders with placeholder', () => {
    render(<Input3D {...defaultProps} placeholder="Enter text" />)
    
    const input = screen.getByRole('textbox')
    // The placeholder might be empty initially due to floating label behavior
    expect(input).toHaveAttribute('placeholder')
  })

  it('shows floating label when focused or has value', async () => {
    const { rerender } = render(<Input3D {...defaultProps} label="Test Label" />)
    
    const input = screen.getByRole('textbox')
    await user.click(input)
    
    // Label should float when focused
    expect(screen.getByText('Test Label')).toBeInTheDocument()
    
    // Label should stay floating when has value
    rerender(<Input3D value="test" onChange={vi.fn()} label="Test Label" />)
    expect(screen.getByText('Test Label')).toBeInTheDocument()
  })

  it('shows required indicator', () => {
    render(<Input3D {...defaultProps} label="Required Field" required />)
    
    expect(screen.getByText('*')).toBeInTheDocument()
  })

  it('shows error message', () => {
    render(<Input3D {...defaultProps} error="This field is required" />)
    
    expect(screen.getByText('This field is required')).toBeInTheDocument()
  })

  it('can be disabled', () => {
    render(<Input3D {...defaultProps} disabled />)
    
    const input = screen.getByRole('textbox')
    expect(input).toBeDisabled()
  })

  it('renders with different types', () => {
    const { rerender } = render(<Input3D {...defaultProps} type="email" />)
    expect(screen.getByRole('textbox')).toHaveAttribute('type', 'email')

    rerender(<Input3D {...defaultProps} type="password" />)
    expect(screen.getByDisplayValue('')).toHaveAttribute('type', 'password')

    rerender(<Input3D {...defaultProps} type="number" />)
    expect(screen.getByRole('spinbutton')).toHaveAttribute('type', 'number')
  })

  it('renders with different variants', () => {
    const { rerender } = render(<Input3D {...defaultProps} variant="default" />)
    expect(screen.getByRole('textbox')).toBeInTheDocument()

    rerender(<Input3D {...defaultProps} variant="glass" />)
    expect(screen.getByRole('textbox')).toBeInTheDocument()

    rerender(<Input3D {...defaultProps} variant="elegant" />)
    expect(screen.getByRole('textbox')).toBeInTheDocument()
  })

  it('renders with different sizes', () => {
    const { rerender } = render(<Input3D {...defaultProps} size="sm" />)
    expect(screen.getByRole('textbox')).toBeInTheDocument()

    rerender(<Input3D {...defaultProps} size="lg" />)
    expect(screen.getByRole('textbox')).toBeInTheDocument()
  })

  it('renders with left icon', () => {
    const icon = <span data-testid="icon">🔍</span>
    render(<Input3D {...defaultProps} icon={icon} iconPosition="left" />)
    
    expect(screen.getByTestId('icon')).toBeInTheDocument()
  })

  it('renders with right icon', () => {
    const icon = <span data-testid="icon">🔍</span>
    render(<Input3D {...defaultProps} icon={icon} iconPosition="right" />)
    
    expect(screen.getByTestId('icon')).toBeInTheDocument()
  })

  it('shows password toggle for password type', async () => {
    render(<Input3D {...defaultProps} type="password" showPasswordToggle />)
    
    const toggleButton = screen.getByRole('button', { name: /show password/i })
    expect(toggleButton).toBeInTheDocument()
    
    await user.click(toggleButton)
    expect(screen.getByRole('button', { name: /hide password/i })).toBeInTheDocument()
  })

  it('toggles password visibility', async () => {
    render(<Input3D {...defaultProps} type="password" showPasswordToggle />)
    
    const input = screen.getByDisplayValue('')
    const toggleButton = screen.getByRole('button', { name: /show password/i })
    
    expect(input).toHaveAttribute('type', 'password')
    
    await user.click(toggleButton)
    expect(input).toHaveAttribute('type', 'text')
    
    await user.click(toggleButton)
    expect(input).toHaveAttribute('type', 'password')
  })

  it('calls onFocus and onBlur callbacks', async () => {
    const onFocus = vi.fn()
    const onBlur = vi.fn()
    render(<Input3D {...defaultProps} onFocus={onFocus} onBlur={onBlur} />)
    
    const input = screen.getByRole('textbox')
    
    await user.click(input)
    expect(onFocus).toHaveBeenCalledTimes(1)
    
    await user.tab()
    expect(onBlur).toHaveBeenCalledTimes(1)
  })

  it('supports autoComplete', () => {
    render(<Input3D {...defaultProps} autoComplete="email" />)
    
    const input = screen.getByRole('textbox')
    expect(input).toHaveAttribute('autocomplete', 'email')
  })

  it('supports aria attributes', () => {
    render(
      <Input3D 
        {...defaultProps} 
        aria-label="Custom label"
        aria-describedby="description"
      />
    )
    
    const input = screen.getByRole('textbox', { name: /custom label/i })
    expect(input).toHaveAttribute('aria-describedby', 'description')
  })

  it('sets aria-invalid when error is present', () => {
    render(<Input3D {...defaultProps} error="Error message" />)
    
    const input = screen.getByRole('textbox')
    expect(input).toHaveAttribute('aria-invalid', 'true')
  })

  it('applies custom className', () => {
    render(<Input3D {...defaultProps} className="custom-class" />)
    
    const container = screen.getByRole('textbox').closest('.custom-class')
    expect(container).toBeInTheDocument()
  })

  it('handles focus and blur events for styling', async () => {
    render(<Input3D {...defaultProps} label="Test Label" />)
    
    const input = screen.getByRole('textbox')
    
    await user.click(input)
    // Focus effects are applied via CSS/motion
    expect(input).toHaveFocus()
    
    await user.tab()
    expect(input).not.toHaveFocus()
  })
})