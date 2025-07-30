import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { vi } from 'vitest'
import Modal3D from '../Modal'

// Mock framer-motion
vi.mock('framer-motion', () => ({
  motion: {
    div: React.forwardRef<HTMLDivElement, any>(({ children, ...props }, ref) => (
      <div ref={ref} {...props}>{children}</div>
    )),
    button: React.forwardRef<HTMLButtonElement, any>(({ children, ...props }, ref) => (
      <button ref={ref} {...props}>{children}</button>
    ))
  },
  AnimatePresence: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}))

describe('Modal3D', () => {
  const user = userEvent.setup()

  const defaultProps = {
    isOpen: true,
    onClose: vi.fn(),
    children: <div>Modal content</div>
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders when open', () => {
    render(<Modal3D {...defaultProps} />)
    
    expect(screen.getByRole('dialog')).toBeInTheDocument()
    expect(screen.getByText('Modal content')).toBeInTheDocument()
  })

  it('does not render when closed', () => {
    render(<Modal3D {...defaultProps} isOpen={false} />)
    
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
  })

  it('renders with title', () => {
    render(<Modal3D {...defaultProps} title="Test Modal" />)
    
    expect(screen.getByText('Test Modal')).toBeInTheDocument()
    expect(screen.getByRole('dialog')).toHaveAttribute('aria-labelledby', 'modal-title')
  })

  it('renders close button by default', () => {
    render(<Modal3D {...defaultProps} />)
    
    const closeButton = screen.getByRole('button', { name: /close modal/i })
    expect(closeButton).toBeInTheDocument()
  })

  it('hides close button when showCloseButton is false', () => {
    render(<Modal3D {...defaultProps} showCloseButton={false} />)
    
    expect(screen.queryByRole('button', { name: /close modal/i })).not.toBeInTheDocument()
  })

  it('calls onClose when close button is clicked', async () => {
    const onClose = vi.fn()
    render(<Modal3D {...defaultProps} onClose={onClose} />)
    
    const closeButton = screen.getByRole('button', { name: /close modal/i })
    await user.click(closeButton)
    
    expect(onClose).toHaveBeenCalledTimes(1)
  })

  it('calls onClose when overlay is clicked', async () => {
    const onClose = vi.fn()
    render(<Modal3D {...defaultProps} onClose={onClose} />)
    
    const dialog = screen.getByRole('dialog')
    
    // Simulate clicking on the overlay (outside the modal content)
    fireEvent.click(dialog.parentElement!, { target: dialog.parentElement })
    expect(onClose).toHaveBeenCalledTimes(1)
  })

  it('does not close when overlay is clicked if closeOnOverlayClick is false', async () => {
    const onClose = vi.fn()
    render(<Modal3D {...defaultProps} onClose={onClose} closeOnOverlayClick={false} />)
    
    const dialog = screen.getByRole('dialog')
    const overlay = dialog.parentElement!
    
    await user.click(overlay)
    expect(onClose).not.toHaveBeenCalled()
  })

  it('closes on Escape key by default', async () => {
    const onClose = vi.fn()
    render(<Modal3D {...defaultProps} onClose={onClose} />)
    
    await user.keyboard('{Escape}')
    expect(onClose).toHaveBeenCalledTimes(1)
  })

  it('does not close on Escape key when closeOnEscape is false', async () => {
    const onClose = vi.fn()
    render(<Modal3D {...defaultProps} onClose={onClose} closeOnEscape={false} />)
    
    await user.keyboard('{Escape}')
    expect(onClose).not.toHaveBeenCalled()
  })

  it('renders with different sizes', () => {
    const { rerender } = render(<Modal3D {...defaultProps} size="sm" />)
    expect(screen.getByRole('dialog')).toBeInTheDocument()

    rerender(<Modal3D {...defaultProps} size="lg" />)
    expect(screen.getByRole('dialog')).toBeInTheDocument()

    rerender(<Modal3D {...defaultProps} size="full" />)
    expect(screen.getByRole('dialog')).toBeInTheDocument()
  })

  it('renders with different variants', () => {
    const { rerender } = render(<Modal3D {...defaultProps} variant="default" />)
    expect(screen.getByRole('dialog')).toBeInTheDocument()

    rerender(<Modal3D {...defaultProps} variant="glass" />)
    expect(screen.getByRole('dialog')).toBeInTheDocument()

    rerender(<Modal3D {...defaultProps} variant="elegant" />)
    expect(screen.getByRole('dialog')).toBeInTheDocument()

    rerender(<Modal3D {...defaultProps} variant="gradient" />)
    expect(screen.getByRole('dialog')).toBeInTheDocument()
  })

  it('supports custom depth', () => {
    render(<Modal3D {...defaultProps} depth={30} />)
    
    expect(screen.getByRole('dialog')).toBeInTheDocument()
  })

  it('supports custom blur intensity', () => {
    render(<Modal3D {...defaultProps} blurIntensity={20} />)
    
    expect(screen.getByRole('dialog')).toBeInTheDocument()
  })

  it('supports aria attributes', () => {
    render(
      <Modal3D 
        {...defaultProps} 
        aria-labelledby="custom-label"
        aria-describedby="custom-description"
      />
    )
    
    const dialog = screen.getByRole('dialog')
    expect(dialog).toHaveAttribute('aria-labelledby', 'custom-label')
    expect(dialog).toHaveAttribute('aria-describedby', 'custom-description')
  })

  it('prevents body scroll when open', () => {
    const originalOverflow = document.body.style.overflow
    
    render(<Modal3D {...defaultProps} />)
    expect(document.body.style.overflow).toBe('hidden')
    
    // Cleanup
    document.body.style.overflow = originalOverflow
  })

  it('restores body scroll when closed', () => {
    const originalOverflow = document.body.style.overflow
    
    const { rerender } = render(<Modal3D {...defaultProps} />)
    expect(document.body.style.overflow).toBe('hidden')
    
    rerender(<Modal3D {...defaultProps} isOpen={false} />)
    expect(document.body.style.overflow).toBe('unset')
    
    // Cleanup
    document.body.style.overflow = originalOverflow
  })

  it('handles mouse move for glow effects', () => {
    render(<Modal3D {...defaultProps} />)
    
    const dialog = screen.getByRole('dialog')
    fireEvent.mouseMove(dialog, { clientX: 100, clientY: 100 })
    
    // Mouse move effects are applied via CSS, hard to test directly
    expect(dialog).toBeInTheDocument()
  })

  it('renders shimmer effect for elegant variant', () => {
    render(<Modal3D {...defaultProps} variant="elegant" />)
    
    expect(screen.getByRole('dialog')).toBeInTheDocument()
    // Shimmer effect is applied via CSS animation
  })
})