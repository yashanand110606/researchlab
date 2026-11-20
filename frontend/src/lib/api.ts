const API_BASE = import.meta.env.VITE_API_URL || '/api/v1'

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(typeof err === 'string' ? err : (err.detail || res.statusText))
  }
  if (res.status === 204) return undefined as T
  return res.json()
}

export const api = {
  // Health
  health: () => request<{ status: string; database: string }>('/health'),
  ready: () => request<{ status: string; checks: Record<string, string> }>('/ready'),

  // Experiments
  experiments: {
    list: (params?: Record<string, string>) =>
      request<{ items: any[]; pagination: { total: number; skip: number; limit: number } }>(
        `/experiments?${new URLSearchParams(params ?? {}).toString()}`
      ),
    get: (id: string) => request<any>(`/experiments/${id}`),
    create: (data: any) => request<any>('/experiments', { method: 'POST', body: JSON.stringify(data) }),
    update: (id: string, data: any) => request<any>(`/experiments/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),
    delete: (id: string) => request<void>(`/experiments/${id}`, { method: 'DELETE' }),
    duplicate: (id: string) => request<any>(`/experiments/${id}/duplicate`, { method: 'POST' }),
    types: () => request<{ types: string[]; details: any[] }>('/experiments/types'),
    addTag: (id: string, tag: string) =>
      request<any>(`/experiments/${id}/tags`, { method: 'POST', body: JSON.stringify({ tag }) }),
    removeTag: (id: string, tag: string) =>
      request<any>(`/experiments/${id}/tags/${encodeURIComponent(tag)}`, { method: 'DELETE' }),
  },

  // Runs
  runs: {
    list: (params?: Record<string, string>) =>
      request<{ items: any[]; count: number }>(`/runs?${new URLSearchParams(params ?? {}).toString()}`),
    get: (id: string) => request<any>(`/runs/${id}`),
    create: (experimentId: string, seed?: number) =>
      request<any>(`/runs/experiments/${experimentId}?${seed != null ? `random_seed=${seed}` : ''}`, { method: 'POST' }),
    cancel: (id: string) => request<any>(`/runs/${id}/cancel`, { method: 'POST' }),
    retry: (id: string) => request<any>(`/runs/${id}/retry`, { method: 'POST' }),
    logs: (id: string) => request<{ items: any[]; count: number }>(`/runs/${id}/logs`),
    metrics: (id: string) => request<{ items: any[]; count: number }>(`/runs/${id}/metrics`),
    results: (id: string) => request<any>(`/runs/${id}/results`),
  },

  // Datasets
  datasets: {
    list: (skip = 0, limit = 50) =>
      request<{ items: any[]; total: number; skip: number; limit: number }>(
        `/datasets?skip=${skip}&limit=${limit}`
      ),
    upload: (name: string, format: string, description: string | null, file: File) => {
      const form = new FormData()
      form.append('name', name)
      form.append('file_format', format)
      if (description) form.append('description', description)
      form.append('file', file)
      return fetch(`${API_BASE}/datasets?name=${encodeURIComponent(name)}&file_format=${encodeURIComponent(format)}${description ? `&description=${encodeURIComponent(description)}` : ''}`, {
        method: 'POST',
        body: form,
      }).then(r => { if (!r.ok) throw new Error('Upload failed'); return r.json() })
    },
    delete: (id: string) => request<void>(`/datasets/${id}`, { method: 'DELETE' }),
  },
}
