import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { api } from '../lib/api'
import { Card, CardContent, CardHeader, CardTitle, CardDescription, Button, Badge, Skeleton } from '../components/UI'
import { formatDate, statusColor, statusBadgeClass } from '../lib/utils'

export default function ExperimentDetail() {
  const { id } = useParams<{ id: string }>()
  const [exp, setExp] = useState<any>(null)
  const [runs, setRuns] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [creating, setCreating] = useState(false)

  useEffect(() => {
    if (!id) return
    setLoading(true)
    Promise.all([api.experiments.get(id), api.runs.list({ experiment_id: id, limit: '20' })])
      .then(([e, r]) => { setExp(e); setRuns(r.items || []) })
      .finally(() => setLoading(false))
  }, [id])

  const handleRun = async () => {
    if (!id) return
    setCreating(true)
    try {
      const run = await api.runs.create(id)
      window.location.href = `/runs`
    } catch (err: any) {
      alert(err.message)
    } finally {
      setCreating(false)
    }
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-8 w-64" />
        <div className="grid md:grid-cols-3 gap-4">
          {[1, 2, 3].map(i => <Skeleton key={i} className="h-32 rounded-lg" />)}
        </div>
        <Skeleton className="h-64 rounded-lg" />
      </div>
    )
  }

  if (!exp) {
    return <p className="text-muted-foreground">Experiment not found.</p>
  }

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between">
        <div>
          <Link to="/experiments" className="text-xs text-muted-foreground hover:text-foreground">&larr; Back</Link>
          <h1 className="text-2xl font-bold tracking-tight mt-1">{exp.name}</h1>
          <p className="text-sm text-muted-foreground mt-1">{exp.description || 'No description.'}</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={handleRun} disabled={creating}>
            {creating ? 'Starting...' : '+ Run Experiment'}
          </Button>
          <Link to={`/experiments/${id}/edit`}>
            <Button variant="outline">Edit</Button>
          </Link>
        </div>
      </div>

      <div className="grid md:grid-cols-3 gap-4">
        <InfoCard label="Category" value={exp.category} />
        <InfoCard label="Configuration Version" value={`v${exp.configuration_version}`} />
        <InfoCard label="Created" value={formatDate(exp.created_at)} />
      </div>

      {/* Configuration */}
      <Card>
        <CardHeader><CardTitle>Configuration</CardTitle></CardHeader>
        <CardContent>
          <pre className="bg-muted rounded-md p-3 text-xs font-mono overflow-x-auto">
            {JSON.stringify(exp.configuration, null, 2)}
          </pre>
        </CardContent>
      </Card>

      {/* Runs */}
      <Card>
        <CardHeader>
          <CardTitle>Run History</CardTitle>
          <CardDescription>{runs.length} runs recorded</CardDescription>
        </CardHeader>
        <CardContent>
          {runs.length === 0 ? (
            <p className="text-xs text-muted-foreground py-4 text-center">No runs yet. Click &quot;+ Run Experiment&quot; to start one.</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-border text-muted-foreground text-xs">
                    <th className="text-left pb-2 pr-4">ID</th>
                    <th className="text-left pb-2 pr-4">Status</th>
                    <th className="text-left pb-2 pr-4">Seed</th>
                    <th className="text-left pb-2 pr-4">Started</th>
                    <th className="text-left pb-2 pr-4">Duration</th>
                    <th className="text-left pb-2">Error</th>
                  </tr>
                </thead>
                <tbody>
                  {runs.map(run => (
                    <tr key={run.id} className="border-b border-border/50 hover:bg-muted/50">
                      <td className="py-2 pr-4 font-mono text-xs">{run.id.slice(0, 8)}</td>
                      <td className="py-2 pr-4">
                        <span className={`text-xs font-medium ${statusColor(run.status)}`}>{run.status}</span>
                      </td>
                      <td className="py-2 pr-4 text-xs">{run.random_seed ?? '—'}</td>
                      <td className="py-2 pr-4 text-xs text-muted-foreground">{formatDate(run.started_at)}</td>
                      <td className="py-2 pr-4 text-xs text-muted-foreground">{run.duration_seconds ? `${run.duration_seconds.toFixed(1)}s` : '—'}</td>
                      <td className="py-2 text-xs text-muted-foreground max-w-[200px] truncate">{run.error_message ?? ''}</td>
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

function InfoCard({ label, value }: { label: string; value: string }) {
  return (
    <Card>
      <CardContent className="p-4">
        <p className="text-xs text-muted-foreground uppercase tracking-wider">{label}</p>
        <p className="text-sm font-semibold mt-1">{value}</p>
      </CardContent>
    </Card>
  )
}
