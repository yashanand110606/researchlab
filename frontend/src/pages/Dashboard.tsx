import { useEffect, useState } from 'react'
import { api } from '../lib/api'
import { Card, CardContent, CardHeader, CardTitle, Skeleton } from '../components/UI'
import { statusColor } from '../lib/utils'

interface Stats {
  total: number
  running: number
  completed: number
  failed: number
}

interface RecentRun {
  id: string
  experiment_id: string
  status: string
  created_at: string
  duration_seconds: number | null
}

export default function Dashboard() {
  const [stats, setStats] = useState<Stats | null>(null)
  const [recentRuns, setRecentRuns] = useState<RecentRun[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [health, setHealth] = useState<{ status: string; database: string } | null>(null)

  useEffect(() => {
    let cancelled = false
    Promise.all([
      api.health().catch(() => null),
      api.runs.list({ limit: '10' }).catch(() => ({ items: [] })),
    ]).then(async ([h, runsData]) => {
      if (cancelled) return
      setHealth(h)
      const runs = runsData?.items ?? []
      setRecentRuns(runs.slice(0, 8))
      const s: Stats = {
        total: runs.length,
        running: runs.filter((r: any) => r.status === 'RUNNING').length,
        completed: runs.filter((r: any) => r.status === 'COMPLETED').length,
        failed: runs.filter((r: any) => r.status === 'FAILED').length,
      }
      setStats(s)
      setLoading(false)
    }).catch(err => {
      if (!cancelled) { setError(err.message); setLoading(false) }
    })
    return () => { cancelled = true }
  }, [])

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map(i => <Skeleton key={i} className="h-24 rounded-lg" />)}
        </div>
        <Skeleton className="h-64 rounded-lg" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="rounded-lg border border-destructive/30 bg-destructive/5 p-6">
        <p className="text-sm text-destructive font-medium">Failed to load dashboard</p>
        <p className="text-xs text-muted-foreground mt-1">{error}</p>
        <p className="text-xs text-muted-foreground mt-2">Make sure the backend is running on port 8000.</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-sm text-muted-foreground mt-1">
          System health: <span className={health?.database === 'connected' ? 'text-emerald-400' : 'text-red-400'}>
            {health?.database ?? 'unknown'}
          </span>
        </p>
      </div>

      {/* Stats cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard label="Total Runs" value={stats?.total ?? 0} accent="text-primary" />
        <StatCard label="Running" value={stats?.running ?? 0} accent="text-blue-400" />
        <StatCard label="Completed" value={stats?.completed ?? 0} accent="text-emerald-400" />
        <StatCard label="Failed" value={stats?.failed ?? 0} accent="text-red-400" />
      </div>

      {/* Activity + Quick Actions */}
      <div className="grid md:grid-cols-3 gap-4">
        <Card className="md:col-span-2">
          <CardHeader>
            <CardTitle>Recent Runs</CardTitle>
          </CardHeader>
          <CardContent>
            {recentRuns.length === 0 ? (
              <p className="text-xs text-muted-foreground py-8 text-center">No runs yet. Create an experiment to get started.</p>
            ) : (
              <div className="space-y-2">
                {recentRuns.map((run: RecentRun) => (
                  <div key={run.id} className="flex items-center justify-between py-2 border-b border-border last:border-0">
                    <div className="flex items-center gap-3">
                      <span className={`w-2 h-2 rounded-full ${run.status === 'COMPLETED' ? 'bg-emerald-400' : run.status === 'RUNNING' ? 'bg-blue-400' : run.status === 'FAILED' ? 'bg-red-400' : 'bg-gray-500'}`} />
                      <div>
                        <p className="text-sm font-medium truncate max-w-[200px]">Run {run.id.slice(0, 8)}</p>
                        <p className="text-xs text-muted-foreground">Experiment {run.experiment_id.slice(0, 8)}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <span className={`text-xs font-medium ${statusColor(run.status)}`}>{run.status}</span>
                      <p className="text-xs text-muted-foreground">
                        {run.duration_seconds ? `${run.duration_seconds.toFixed(1)}s` : '—'}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle>Quick Actions</CardTitle></CardHeader>
          <CardContent className="space-y-2">
            <a href="/experiments/new" className="block w-full text-left">
              <button className="w-full text-sm px-3 py-2 rounded-md border border-border hover:bg-accent transition-colors text-foreground">
                + New Experiment
              </button>
            </a>
            <a href="/experiments" className="block w-full text-left">
              <button className="w-full text-sm px-3 py-2 rounded-md border border-border hover:bg-accent transition-colors text-foreground">
                Browse Experiments
              </button>
            </a>
            <a href="/runs" className="block w-full text-left">
              <button className="w-full text-sm px-3 py-2 rounded-md border border-border hover:bg-accent transition-colors text-foreground">
                View Run Monitor
              </button>
            </a>
            <a href="/results" className="block w-full text-left">
              <button className="w-full text-sm px-3 py-2 rounded-md border border-border hover:bg-accent transition-colors text-foreground">
                Results Explorer
              </button>
            </a>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

function StatCard({ label, value, accent }: { label: string; value: number; accent: string }) {
  return (
    <Card>
      <CardContent className="p-4">
        <p className="text-xs text-muted-foreground uppercase tracking-wider">{label}</p>
        <p className={`text-2xl font-bold mt-1 ${accent}`}>{value}</p>
      </CardContent>
    </Card>
  )
}
