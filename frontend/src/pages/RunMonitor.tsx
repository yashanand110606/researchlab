import { useEffect, useState } from 'react'
import { api } from '../lib/api'
import { Card, CardContent, CardHeader, CardTitle, Button, Input, Select, Skeleton } from '../components/UI'
import { formatDate, formatDuration, statusColor } from '../lib/utils'
import { statusBadgeClass } from '../lib/utils'
import { RefreshCw } from 'lucide-react'

const STATUS_FILTERS = ['all', 'PENDING', 'QUEUED', 'RUNNING', 'COMPLETED', 'FAILED', 'CANCELLED']

export default function RunMonitor() {
  const [runs, setRuns] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('all')
  const [searchExpId, setSearchExpId] = useState('')
  const [polling, setPolling] = useState(false)

  const fetchRuns = () => {
    setLoading(true)
    const params: Record<string, string> = { limit: '50' }
    if (filter !== 'all') params.status = filter
    if (searchExpId) params.experiment_id = searchExpId
    api.runs.list(params)
      .then(data => setRuns(data.items || []))
      .finally(() => setLoading(false))
  }

  useEffect(() => { fetchRuns() }, [filter, searchExpId])

  const handleRetry = async (runId: string) => {
    try {
      await api.runs.retry(runId)
      fetchRuns()
    } catch (err: any) {
      alert(err.message)
    }
  }

  const handleCancel = async (runId: string) => {
    try {
      await api.runs.cancel(runId)
      fetchRuns()
    } catch (err: any) {
      alert(err.message)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Run Monitor</h1>
          <p className="text-sm text-muted-foreground mt-1">{runs.length} runs displayed</p>
        </div>
        <Button variant="outline" size="sm" onClick={fetchRuns} disabled={loading}>
          <RefreshCw className={`h-3 w-3 ${polling ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="p-3 flex gap-3">
          <Select
            value={filter}
            onChange={v => setFilter(v)}
            options={STATUS_FILTERS.map(s => ({ value: s, label: s === 'all' ? 'All Statuses' : s }))}
          />
          <Input
            placeholder="Filter by experiment ID..."
            value={searchExpId}
            onChange={e => setSearchExpId(e.target.value)}
            className="max-w-xs"
          />
        </CardContent>
      </Card>

      {/* Runs table */}
      <Card>
        <CardHeader><CardTitle>Experiment Runs</CardTitle></CardHeader>
        <CardContent>
          {loading ? (
            <div className="space-y-2">
              {[1, 2, 3, 4, 5].map(i => <Skeleton key={i} className="h-10 rounded" />)}
            </div>
          ) : runs.length === 0 ? (
            <p className="text-sm text-muted-foreground py-8 text-center">No runs found. Create an experiment and start a run.</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-border text-muted-foreground text-xs">
                    <th className="text-left pb-2 pr-4">ID</th>
                    <th className="text-left pb-2 pr-4">Experiment</th>
                    <th className="text-left pb-2 pr-4">Status</th>
                    <th className="text-left pb-2 pr-4">Seed</th>
                    <th className="text-left pb-2 pr-4">Started</th>
                    <th className="text-left pb-2 pr-4">Completed</th>
                    <th className="text-left pb-2 pr-4">Duration</th>
                    <th className="text-left pb-2">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {runs.map(run => (
                    <tr key={run.id} className="border-b border-border/50 hover:bg-muted/50">
                      <td className="py-3 pr-4 font-mono text-xs">{run.id.slice(0, 8)}</td>
                      <td className="py-3 pr-4">
                        <a href={`/experiments/${run.experiment_id}`} className="text-primary hover:underline text-xs">
                          {run.experiment_id.slice(0, 8)}
                        </a>
                      </td>
                      <td className="py-3 pr-4">
                        <span className={`text-xs font-medium px-2 py-0.5 rounded border ${statusBadgeClass(run.status)}`}>
                          {run.status}
                        </span>
                      </td>
                      <td className="py-3 pr-4 text-xs text-muted-foreground">{run.random_seed ?? '—'}</td>
                      <td className="py-3 pr-4 text-xs text-muted-foreground">{formatDate(run.started_at)}</td>
                      <td className="py-3 pr-4 text-xs text-muted-foreground">{formatDate(run.completed_at)}</td>
                      <td className="py-3 pr-4 text-xs text-muted-foreground">{formatDuration(run.duration_seconds)}</td>
                      <td className="py-3">
                        <div className="flex gap-1">
                          {(run.status === 'FAILED' || run.status === 'CANCELLED') && (
                            <Button variant="ghost" size="sm" className="h-6 px-2 text-xs" onClick={() => handleRetry(run.id)}>
                              Retry
                            </Button>
                          )}
                          {(run.status === 'PENDING' || run.status === 'QUEUED') && (
                            <Button variant="ghost" size="sm" className="h-6 px-2 text-xs text-red-400 hover:text-red-300" onClick={() => handleCancel(run.id)}>
                              Cancel
                            </Button>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
