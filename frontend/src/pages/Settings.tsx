import { useEffect, useState } from 'react'
import { api } from '../lib/api'
import { Card, CardContent, CardHeader, CardTitle, Skeleton } from '../components/UI'

export default function Settings() {
  const [health, setHealth] = useState<any>(null)
  const [ready, setReady] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    setLoading(true)
    Promise.all([api.health(), api.ready()])
      .then(([h, r]) => { setHealth(h); setReady(r) })
      .catch((err: any) => setError(err.message))
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-8 w-48" />
        {[1, 2, 3].map(i => <Skeleton key={i} className="h-32 rounded-lg" />)}
      </div>
    )
  }

  return (
    <div className="space-y-6 max-w-2xl">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Settings</h1>
        <p className="text-sm text-muted-foreground mt-1">Application health and system configuration.</p>
      </div>

      {error && (
        <Card>
          <CardContent className="p-4">
            <p className="text-sm text-destructive">Could not reach backend: {error}</p>
            <p className="text-xs text-muted-foreground mt-1">Make sure the backend server is running on port 8000.</p>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader><CardTitle>System Health</CardTitle></CardHeader>
        <CardContent className="space-y-3">
          <div className="flex items-center justify-between py-2 border-b border-border">
            <span className="text-sm">API Status</span>
            <span className={`text-sm font-medium ${health?.status === 'ok' ? 'text-emerald-400' : 'text-red-400'}`}>
              {health?.status ?? 'unknown'}
            </span>
          </div>
          <div className="flex items-center justify-between py-2 border-b border-border">
            <span className="text-sm">Database</span>
            <span className={`text-sm font-medium ${health?.database === 'connected' ? 'text-emerald-400' : 'text-red-400'}`}>
              {health?.database ?? 'unknown'}
            </span>
          </div>
          <div className="flex items-center justify-between py-2 border-b border-border">
            <span className="text-sm">Readiness</span>
            <span className={`text-sm font-medium ${ready?.status === 'ready' ? 'text-emerald-400' : 'text-yellow-400'}`}>
              {ready?.status ?? 'unknown'}
            </span>
          </div>
          {ready?.checks && Object.entries(ready.checks).map(([key, val]) => (
            <div key={key} className="flex items-center justify-between py-2">
              <span className="text-sm capitalize">{key}</span>
              <span className={`text-xs font-mono ${(val as string) === 'ok' ? 'text-emerald-400' : 'text-red-400'}`}>
                {(val as string)}
              </span>
            </div>
          ))}
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle>API Documentation</CardTitle></CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            Full API documentation is available at <code className="text-primary bg-muted px-1 rounded">/docs</code> (Swagger UI) and <code className="text-primary bg-muted px-1 rounded">/redoc</code>.
          </p>
          <p className="text-xs text-muted-foreground mt-2">
            OpenAPI spec: <code className="text-primary bg-muted px-1 rounded">/openapi.json</code>
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle>About ResearchLab</CardTitle></CardHeader>
        <CardContent className="space-y-2">
          <p className="text-sm">Scientific Experiment Orchestration Platform v0.1.0</p>
          <p className="text-xs text-muted-foreground">
            Built with FastAPI, SQLAlchemy, Celery, React, TypeScript. Supports numerical integration benchmarks, Monte Carlo simulations, and parameter sweeps.
          </p>
        </CardContent>
      </Card>
    </div>
  )
}
