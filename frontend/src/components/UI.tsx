import React from 'react'
import { cn } from '../lib/utils'

// Button
export function Button({
  children, variant = 'default', size = 'md', className, ...props
}: {
  children: React.ReactNode
  variant?: 'default' | 'outline' | 'ghost' | 'destructive'
  size?: 'sm' | 'md' | 'lg'
  className?: string
} & React.ButtonHTMLAttributes<HTMLButtonElement>) {
  const base = 'inline-flex items-center justify-center gap-2 rounded-md font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50'
  const variants: Record<string, string> = {
    default: 'bg-primary text-primary-foreground hover:bg-primary/90',
    outline: 'border border-border bg-background hover:bg-accent hover:text-accent-foreground',
    ghost: 'hover:bg-accent hover:text-accent-foreground',
    destructive: 'bg-destructive text-destructive-foreground hover:bg-destructive/90',
  }
  const sizes: Record<string, string> = {
    sm: 'h-8 px-3 text-xs',
    md: 'h-9 px-4 text-sm',
    lg: 'h-11 px-6 text-base',
  }
  return (
    <button className={cn(base, variants[variant], sizes[size], className)} {...props}>
      {children}
    </button>
  )
}

// Card
export function Card({ className, children, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div className={cn('rounded-lg border border-border bg-card text-foreground shadow-sm', className)} {...props}>
      {children}
    </div>
  )
}

export function CardHeader({ className, children }: React.HTMLAttributes<HTMLDivElement>) {
  return <div className={cn('flex flex-col space-y-1.5 p-4', className)}>{children}</div>
}

export function CardTitle({ className, children }: React.HTMLAttributes<HTMLHeadingElement>) {
  return <h3 className={cn('text-sm font-semibold leading-none tracking-tight', className)}>{children}</h3>
}

export function CardDescription({ className, children }: React.HTMLAttributes<HTMLParagraphElement>) {
  return <p className={cn('text-xs text-muted-foreground', className)}>{children}</p>
}

export function CardContent({ className, children }: React.HTMLAttributes<HTMLDivElement>) {
  return <div className={cn('p-4 pt-0', className)}>{children}</div>
}

// Badge
export function Badge({ children, variant = 'default', className }: {
  children: React.ReactNode
  variant?: 'default' | 'secondary' | 'outline' | 'destructive'
  className?: string
}) {
  const variants: Record<string, string> = {
    default: 'bg-primary/10 text-primary border-primary/20',
    secondary: 'bg-secondary text-secondary-foreground border-transparent',
    outline: 'border border-border text-muted-foreground',
    destructive: 'bg-destructive/10 text-destructive border-destructive/20',
  }
  return (
    <span className={cn('inline-flex items-center rounded border px-2 py-0.5 text-xs font-medium', variants[variant], className)}>
      {children}
    </span>
  )
}

// Input
export function Input({ className, ...props }: React.InputHTMLAttributes<HTMLInputElement>) {
  return (
    <input
      className={cn(
        'flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm transition-colors file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50',
        className,
      )}
      {...props}
    />
  )
}

// Textarea
export function Textarea({ className, ...props }: React.TextareaHTMLAttributes<HTMLTextAreaElement>) {
  return (
    <textarea
      className={cn(
        'flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm shadow-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50',
        className,
      )}
      {...props}
    />
  )
}

// Select
export function Select({ value, onChange, options, className }: {
  value: string
  onChange: (v: string) => void
  options: { value: string; label: string }[]
  className?: string
}) {
  return (
    <select
      value={value}
      onChange={e => onChange(e.target.value)}
      className={cn('flex h-9 rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring', className)}
    >
      {options.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
    </select>
  )
}

// Skeleton
export function Skeleton({ className }: { className?: string }) {
  return <div className={cn('animate-pulse rounded-md bg-muted', className)} />
}

// Empty state
export function EmptyState({ title, description, action }: {
  title: string
  description: string
  action?: React.ReactNode
}) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center">
      <div className="mx-auto h-12 w-12 rounded-full bg-muted flex items-center justify-center mb-4">
        <span className="text-2xl">∅</span>
      </div>
      <h3 className="text-sm font-semibold mb-1">{title}</h3>
      <p className="text-xs text-muted-foreground max-w-sm mb-4">{description}</p>
      {action}
    </div>
  )
}

// Error boundary
export class ErrorBoundary extends React.Component<{ children: React.ReactNode }, { error: string }> {
  state = { error: '' }
  static getDerivedStateFromError(e: Error) {
    return { error: e.message }
  }
  render() {
    if (this.state.error) {
      return (
        <div className="rounded-lg border border-destructive/30 bg-destructive/5 p-4">
          <p className="text-sm text-destructive font-medium">Error</p>
          <p className="text-xs text-muted-foreground mt-1">{this.state.error}</p>
        </div>
      )
    }
    return this.props.children
  }
}
