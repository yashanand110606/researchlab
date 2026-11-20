import { describe, it, expect, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import Dashboard from '../pages/Dashboard'

vi.mock('../lib/api', () => ({
  api: {
    health: vi.fn().mockResolvedValue({ status: 'ok', database: 'connected' }),
    ready: vi.fn().mockResolvedValue({ status: 'ready', checks: { database: 'ok' } }),
    runs: {
      list: vi.fn().mockResolvedValue({ items: [] }),
    },
  },
}))

describe('Dashboard', () => {
  it('renders the dashboard title', async () => {
    render(<Dashboard />)
    await waitFor(() => {
      expect(screen.getByText(/dashboard/i)).toBeInTheDocument()
    })
  })

  it('displays empty state when no runs exist', async () => {
    const { api } = await import('../lib/api')
    vi.mocked(api.runs.list).mockResolvedValue({ items: [], count: 0 })
    render(<Dashboard />)
    await waitFor(() => {
      expect(screen.getByText(/no runs yet/i)).toBeInTheDocument()
    })
  })
})
