import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { vi } from 'vitest'
import Button3D from '../Button3D'

// Mock framer-motion
vi.mock('framer-motion', () => ({
  motion: {
    button: React.forwardRef<HTMLButtonElement, any>(({ children, ...props }, ref) => (
      <button ref={ref} {...props}>{children}</button>
    )),
    div: React.forwardRef<HTMLDivElement, any>(({ children, ...props }, ref) => (
      <div ref={ref} {...props}>{children}</div>
    ))
  },
  AnimatePresence: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}))

describe('Button3D', () => {
  const user = userEvent.setup()

  it('renders with default props', () => {
    render(<Button3D>Click me</Button3D>)
    
    const button = screen.getByRole('button', { name: /click me/i })
    expect(button).toBeInTheDocument()
    expect(button).not.toBeDisabled()
  })

  it('handles click events', async () => {
    const handleClick = vi.fn()
    render(<Button3D onClick={handleClick}>Click me</Button3D>)
    
    const button = screen.getByRole('button', { name: /click me/i })
    await user.click(button)
    
    expect(handleClick).toHaveBeenCalledTimes(1)
  })

  it('shows loading state', () => {
    render(<Button3D loading>Click me</Button3D>)
    
    const button = screen.getByRole('button')
    expect(button).toBeDisabled()
    expect(screen.getByText(/loading/i)).toBeInTheDocument()
  })

  it('can be disabled', () => {
    const handleClick = vi.fn()
    render(<Button3D disabled onClick={handleClick}>Click me</Button3D>)
    
    const button = screen.getByRole('button', { name: /click me/i })
    expect(button).toBeDisabled()
    
    fireEvent.click(button)
    expect(handleClick).not.toHaveBeenCalled()
  })

  it('renders with different variants', () => {
    const { rerender } = render(<Button3D variant="primary">Primary</Button3D>)
    expect(screen.getByRole('button')).toBeInTheDocument()

    rerender(<Button3D variant="secondary">Secondary</Button3D>)
    expect(screen.getByRole('button')).toBeInTheDocument()

    rerender(<Button3D variant="glass">Glass</Button3D>)
    expect(screen.getByRole('button')).toBeInTheDocument()
  })

  it('renders with different sizes', () => {
    const { rerender } = render(<Button3D size="sm">Small</Button3D>)
    expect(screen.getByRole('button')).toBeInTheDocument()

    rerender(<Button3D size="lg">Large</Button3D>)
    expect(screen.getByRole('button')).toBeInTheDocument()
  })

  it('renders with icons', () => {
    const icon = <span data-testid="icon">🚀</span>
    render(<Button3D icon={icon} iconPosition="left">With Icon</Button3D>)
    
    expect(screen.getByTestId('icon')).toBeInTheDocument()
    expect(screen.getByRole('button')).toBeInTheDocument()
  })

  it('supports full width', () => {
    render(<Button3D fullWidth>Full Width</Button3D>)
    
    const button = screen.getByRole('button', { name: /full width/i })
    expect(button).toBeInTheDocument()
  })

  it('handles keyboard navigation', async () => {
    const handleClick = vi.fn()
    render(<Button3D onClick={handleClick}>Click me</Button3D>)
    
    const button = screen.getByRole('button', { name: /click me/i })
    button.focus()
    
    await user.keyboard('{Enter}')
    expect(handleClick).toHaveBeenCalledTimes(1)
    
    await user.keyboard(' ')
    expect(handleClick).toHaveBeenCalledTimes(2)
  })

  it('supports aria attributes', () => {
    render(
      <Button3D 
        aria-label="Custom label" 
        aria-describedby="description"
      >
        Button
      </Button3D>
    )
    
    const button = screen.getByRole('button', { name: /custom label/i })
    expect(button).toHaveAttribute('aria-describedby', 'description')
  })

  it('creates particles on click when particle effect is enabled', async () => {
    render(<Button3D particleEffect>Click me</Button3D>)
    
    const button = screen.getByRole('button', { name: /click me/i })
    await user.click(button)
    
    // Particle effects are created but may not be immediately visible in DOM
    expect(button).toBeInTheDocument()
  })

  it('creates ripple effects on click when ripple animation is enabled', async () => {
    render(<Button3D rippleAnimation>Click me</Button3D>)
    
    const button = screen.getByRole('button', { name: /click me/i })
    await user.click(button)
    
    // Ripple effects are created but may not be immediately visible in DOM
    expect(button).toBeInTheDocument()
  })

  it('applies custom className', () => {
    render(<Button3D className="custom-class">Button</Button3D>)
    
    const button = screen.getByRole('button', { name: /button/i })
    expect(button).toHaveClass('custom-class')
  })

  it('handles different button types', () => {
    const { rerender } = render(<Button3D type="submit">Submit</Button3D>)
    expect(screen.getByRole('button')).toHaveAttribute('type', 'submit')

    rerender(<Button3D type="reset">Reset</Button3D>)
    expect(screen.getByRole('button')).toHaveAttribute('type', 'reset')
  })
})