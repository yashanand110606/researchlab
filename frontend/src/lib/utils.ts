import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatDate(iso?: string | null): string {
  if (!iso) return '—'
  return new Date(iso).toLocaleString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export function formatDuration(seconds?: number | null): string {
  if (seconds == null) return '—'
  if (seconds < 1) return `${(seconds * 1000).toFixed(0)}ms`
  if (seconds < 60) return `${seconds.toFixed(1)}s`
  const m = Math.floor(seconds / 60)
  const s = (seconds % 60).toFixed(1)
  return `${m}m ${s}s`
}

export function statusColor(status: string): string {
  switch (status) {
    case 'COMPLETED': return 'text-emerald-400'
    case 'RUNNING': return 'text-blue-400'
    case 'QUEUED': return 'text-yellow-400'
    case 'PENDING': return 'text-gray-400'
    case 'FAILED': return 'text-red-400'
    case 'CANCELLED': return 'text-gray-500'
    default: return 'text-muted-foreground'
  }
}

export function statusBadgeClass(status: string): string {
  switch (status) {
    case 'COMPLETED': return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
    case 'RUNNING': return 'bg-blue-500/10 text-blue-400 border-blue-500/20'
    case 'QUEUED': return 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20'
    case 'PENDING': return 'bg-gray-500/10 text-gray-400 border-gray-500/20'
    case 'FAILED': return 'bg-red-500/10 text-red-400 border-red-500/20'
    case 'CANCELLED': return 'bg-gray-500/10 text-gray-500 border-gray-500/20'
    default: return 'bg-muted text-muted-foreground border-border'
  }
}
