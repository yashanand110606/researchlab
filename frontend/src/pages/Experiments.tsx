import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../lib/api'
import { Card, CardContent, CardHeader, CardTitle, CardDescription, Button, Input, Select, Badge, EmptyState, Skeleton } from '../components/UI'
import { formatDate, statusColor } from '../lib/utils'

const CATEGORIES = ['all', 'general', 'physics', 'chemistry', 'biology', 'statistics', 'numerical']

export default function Experiments() {
  const [experiments, setExperiments] = useState<any[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [category, setCategory] = useState('all')
  const [page, setPage] = useState(0)
  const limit = 12

  useEffect(() => {
    setLoading(true)
    const params: Record<string, string> = { skip: String(page * limit), limit: String(limit) }
    if (search) params.search = search
    if (category !== 'all') params.category = category
    api.experiments.list(params)
      .then(data => { setExperiments(data.items); setTotal(data.pagination.total) })
      .catch(() => { setExperiments([]); setTotal(0) })
      .finally(() => setLoading(false))
  }, [search, category, page])

  if (loading) {
    return (
      <div>
        <Skeleton className="h-8 w-48 mb-4" />
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[1, 2, 3, 4, 5, 6].map(i => <Skeleton key={i} className="h-32 rounded-lg" />)}
        </div>
      </div>
    )
  }

  const totalPages = Math.ceil(total / limit)

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Experiments</h1>
          <p className="text-sm text-muted-foreground mt-1">{total} experiments found</p>
        </div>
        <Link to="/experiments/new">
          <Button>+ New Experiment</Button>
        </Link>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="p-3 flex gap-3">
          <Input
            placeholder="Search experiments..."
            value={search}
            onChange={e => { setSearch(e.target.value); setPage(0) }}
            className="max-w-xs"
          />
          <Select
            value={category}
            onChange={v => { setCategory(v); setPage(0) }}
            options={CATEGORIES.map(c => ({ value: c, label: c.charAt(0).toUpperCase() + c.slice(1) }))}
          />
        </CardContent>
      </Card>

      {/* Grid */}
      {experiments.length === 0 ? (
        <EmptyState
          title="No experiments found"
          description="Get started by creating your first scientific experiment."
          action={<Link to="/experiments/new"><Button>Create Experiment</Button></Link>}
        />
      ) : (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {experiments.map(exp => (
            <Link key={exp.id} to={`/experiments/${exp.id}`} className="block">
              <Card className="h-full hover:border-primary/50 transition-colors cursor-pointer group">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <CardTitle className="group-hover:text-primary transition-colors">{exp.name}</CardTitle>
                    <Badge variant="outline">{exp.category}</Badge>
                  </div>
                  <CardDescription>
                    v{exp.configuration_version} · Created {formatDate(exp.created_at)}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <p className="text-xs text-muted-foreground line-clamp-2 min-h-[2.5em]">
                    {exp.description || 'No description provided.'}
                  </p>
                  <div className="mt-3 flex items-center gap-2 text-xs text-muted-foreground">
                    <span>Type: {String(exp.configuration?.experiment?.type || 'unknown')}</span>
                  </div>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-2">
          <Button variant="outline" size="sm" disabled={page === 0} onClick={() => setPage(p => p - 1)}>
            Previous
          </Button>
          <span className="text-xs text-muted-foreground">
            Page {page + 1} of {totalPages}
          </span>
          <Button variant="outline" size="sm" disabled={page >= totalPages - 1} onClick={() => setPage(p => p + 1)}>
            Next
          </Button>
        </div>
      )}
    </div>
  )
}
