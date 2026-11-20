import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../lib/api'
import { Card, CardContent, CardHeader, CardTitle, Button, Input, Textarea, Select, Badge, EmptyState } from '../components/UI'

const CATEGORIES = ['general', 'physics', 'chemistry', 'biology', 'statistics', 'numerical']

const TEMPLATES: Record<string, { name: string; config: any }> = {
  numerical_integration: {
    name: 'Numerical Integration Benchmark',
    config: {
      experiment: {
        type: 'numerical_integration',
        parameters: { equation: 'exponential_decay', initial_value: 1.0, decay_constant: 0.5, time_start: 0.0, time_end: 10.0, step_size: 0.1 },
        execution: { timeout_seconds: 120, max_iterations: 100000 },
      },
    },
  },
  monte_carlo: {
    name: 'Monte Carlo Pi Estimation',
    config: {
      experiment: {
        type: 'monte_carlo',
        parameters: { num_samples: 50000, algorithm: 'basic', tolerance: 0.01 },
        execution: { timeout_seconds: 120 },
      },
    },
  },
  parameter_sweep: {
    name: 'Parameter Sweep',
    config: {
      experiment: {
        type: 'parameter_sweep',
        parameters: {
          function: 'quadratic',
          parametric_definitions: [
            { name: 'x', lower: -5.0, upper: 5.0, steps: 21 },
            { name: 'y', lower: -5.0, upper: 5.0, steps: 21 },
          ],
        },
        execution: { timeout_seconds: 300 },
      },
    },
  },
}

export default function CreateExperiment() {
  const navigate = useNavigate()
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [category, setCategory] = useState('general')
  const [configJson, setConfigJson] = useState('{}')
  const [errors, setErrors] = useState<string[]>([])
  const [saving, setSaving] = useState(false)
  const [createdId, setCreatedId] = useState<string | null>(null)

  useEffect(() => {
    api.experiments.types().then(data => {}).catch(() => {})
  }, [])

  const applyTemplate = (templateKey: string) => {
    const t = TEMPLATES[templateKey]
    if (t) {
      setConfigJson(JSON.stringify(t.config, null, 2))
      setName(t.name)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setErrors([])
    let config: any
    try {
      config = JSON.parse(configJson)
    } catch {
      setErrors(['Invalid JSON configuration'])
      return
    }

    setSaving(true)
    try {
      const result = await api.experiments.create({ name, description, category, configuration: config })
      setCreatedId(result.id)
    } catch (err: any) {
      setErrors([err.message || 'Failed to create experiment'])
    } finally {
      setSaving(false)
    }
  }

  if (createdId) {
    return (
      <div className="max-w-xl mx-auto space-y-6">
        <Card>
          <CardHeader><CardTitle>Experiment Created</CardTitle></CardHeader>
          <CardContent className="space-y-4">
            <p className="text-sm">Your experiment has been created successfully.</p>
            <div className="flex gap-3">
              <Button onClick={() => navigate(`/experiments/${createdId}`)}>View Experiment</Button>
              <Button variant="outline" onClick={() => navigate('/experiments/new')}>Create Another</Button>
              <Button variant="ghost" onClick={() => navigate('/experiments')}>Back to List</Button>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="max-w-3xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Create Experiment</h1>
        <p className="text-sm text-muted-foreground mt-1">Define a new scientific experiment with its configuration.</p>
      </div>

      {/* Templates */}
      <Card>
        <CardHeader><CardTitle>Quick Templates</CardTitle></CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2">
            {Object.entries(TEMPLATES).map(([key, t]) => (
              <Button key={key} variant="outline" size="sm" onClick={() => applyTemplate(key)}>
                {t.name}
              </Button>
            ))}
          </div>
        </CardContent>
      </Card>

      <form onSubmit={handleSubmit} className="space-y-4">
        <Card>
          <CardHeader><CardTitle>Basic Information</CardTitle></CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="text-sm font-medium mb-1 block">Name *</label>
              <Input value={name} onChange={e => setName(e.target.value)} placeholder="My experiment" required />
            </div>
            <div>
              <label className="text-sm font-medium mb-1 block">Description</label>
              <Textarea value={description} onChange={e => setDescription(e.target.value)} placeholder="Brief description of the experiment..." rows={3} />
            </div>
            <div>
              <label className="text-sm font-medium mb-1 block">Category</label>
              <Select value={category} onChange={setCategory} options={CATEGORIES.map(c => ({ value: c, label: c.charAt(0).toUpperCase() + c.slice(1) }))} />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle>Configuration (JSON)</CardTitle></CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="text-sm font-medium mb-1 block">Experiment Configuration</label>
              <pre className="bg-muted rounded-md p-3 text-xs font-mono overflow-x-auto min-h-[200px] whitespace-pre-wrap">
                <textarea
                  value={configJson}
                  onChange={e => setConfigJson(e.target.value)}
                  className="w-full h-[200px] bg-transparent resize-none outline-none font-mono text-xs"
                  spellCheck={false}
                />
              </pre>
            </div>
            {errors.length > 0 && (
              <div className="space-y-1">
                {errors.map((err, i) => (
                  <p key={i} className="text-xs text-destructive">{err}</p>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        <div className="flex gap-3 justify-end">
          <Button variant="outline" onClick={() => navigate('/experiments')}>Cancel</Button>
          <Button type="submit" disabled={saving || !name.trim()}>
            {saving ? 'Creating...' : 'Create Experiment'}
          </Button>
        </div>
      </form>
    </div>
  )
}
