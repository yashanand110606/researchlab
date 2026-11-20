import { useEffect, useState } from 'react'
import { api } from '../lib/api'
import { Card, CardContent, CardHeader, CardTitle, Button, Select, Skeleton } from '../components/UI'

interface MetricItem {
  name: string
  value: number
  unit: string | null
  step: number | null
}

export default function ResultsExplorer() {
  const [selectedRun, setSelectedRun] = useState<string>('')
  const [runs, setRuns] = useState<{ id: string; name: string; status: string }[]>([])
  const [metrics, setMetrics] = useState<MetricItem[]>([])
  const [rawResults, setRawResults] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Load completed runs for selection
  useEffect(() => {
    api.runs.list({ status: 'COMPLETED', limit: '50' })
      .then(data => {
        const items: any[] = data.items || []
        setRuns(items.map((r: any) => ({
          id: r.id,
          name: `Run ${r.id.slice(0, 8)}`,
          status: r.status,
        })))
        if (items.length > 0 && !selectedRun) {
          setSelectedRun(items[0].id)
        }
      })
      .catch(() => {})
  }, [])

  const loadResults = async (runId: string) => {
    if (!runId) return
    setLoading(true)
    setError(null)
    try {
      const [metricsData, resultsData] = await Promise.all([
        api.runs.metrics(runId),
        api.runs.results(runId),
      ])
      setMetrics(metricsData.items || [])
      setRawResults(resultsData)
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (selectedRun) loadResults(selectedRun)
  }, [selectedRun])

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Results Explorer</h1>
        <p className="text-sm text-muted-foreground mt-1">View and compare experiment metrics and results.</p>
      </div>

      <Card>
        <CardHeader><CardTitle>Select Run</CardTitle></CardHeader>
        <CardContent>
          <div className="flex gap-3">
            <Select
              value={selectedRun}
              onChange={setSelectedRun}
              options={[
                { value: '', label: '— Select a run —' },
                ...runs.map(r => ({ value: r.id, label: `${r.name} (${r.status})` })),
              ]}
            />
            {selectedRun && <Button onClick={() => loadResults(selectedRun)} disabled={loading}>Load</Button>}
          </div>
        </CardContent>
      </Card>

      {error && (
        <Card>
          <CardContent className="p-4">
            <p className="text-sm text-destructive">Error loading results: {error}</p>
          </CardContent>
        </Card>
      )}

      {loading && (
        <div className="space-y-4">
          <Skeleton className="h-48 rounded-lg" />
          <Skeleton className="h-64 rounded-lg" />
        </div>
      )}

      {!loading && metrics.length > 0 && (
        <div className="grid md:grid-cols-2 gap-4">
          {/* Metrics table */}
          <Card>
            <CardHeader><CardTitle>Metrics</CardTitle></CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-border text-muted-foreground text-xs">
                      <th className="text-left pb-2 pr-4">Name</th>
                      <th className="text-right pb-2 pr-4">Value</th>
                      <th className="text-left pb-2">Unit</th>
                    </tr>
                  </thead>
                  <tbody>
                    {metrics.map(m => (
                      <tr key={m.name} className="border-b border-border/50">
                        <td className="py-2 pr-4 font-mono text-xs">{m.name}</td>
                        <td className="py-2 pr-4 text-right font-mono text-xs">
                          {typeof m.value === 'number' ? m.value.toPrecision(6) : m.value}
                        </td>
                        <td className="py-2 text-xs text-muted-foreground">{m.unit ?? '—'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>

          {/* Raw results */}
          <Card>
            <CardHeader><CardTitle>Results Summary</CardTitle></CardHeader>
            <CardContent>
              {rawResults ? (
                <pre className="text-xs font-mono overflow-x-auto max-h-[300px] overflow-y-auto bg-muted rounded p-3">
                  {JSON.stringify(rawResults, null, 2)}
                </pre>
              ) : (
                <p className="text-xs text-muted-foreground">No results available for this run.</p>
              )}
            </CardContent>
          </Card>
        </div>
      )}

      {!loading && !error && metrics.length === 0 && selectedRun && (
        <p className="text-sm text-muted-foreground text-center py-8">
          No metrics recorded for this run yet. Check back after execution completes.
        </p>
      )}
    </div>
  )
}
