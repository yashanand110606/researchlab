import { z } from 'zod'

export const experimentCreateSchema = z.object({
  name: z.string().min(1, 'Name is required').max(255),
  description: z.string().optional(),
  category: z.string().default('general'),
  configuration: z.record(z.unknown()),
})

export type ExperimentCreateInput = z.infer<typeof experimentCreateSchema>

export interface Experiment {
  id: string
  name: string
  description: string | null
  category: string
  configuration: Record<string, unknown>
  configuration_version: number
  created_at: string
  updated_at: string
}

export interface ExperimentRun {
  id: string
  experiment_id: string
  status: 'PENDING' | 'QUEUED' | 'RUNNING' | 'COMPLETED' | 'FAILED' | 'CANCELLED'
  configuration_snapshot: Record<string, unknown>
  random_seed: number | null
  started_at: string | null
  completed_at: string | null
  duration_seconds: number | null
  error_message: string | null
  worker_id: string | null
  created_at: string
}

export interface Metric {
  id: string
  run_id: string
  name: string
  value: number
  unit: string | null
  recorded_at: string
  step: number | null
  metadata: Record<string, unknown> | null
}

export interface LogEntry {
  id: string
  run_id: string
  timestamp: string
  level: string
  message: string
  metadata: Record<string, unknown> | null
}

export interface Dataset {
  id: string
  name: string
  description: string | null
  filename: string
  file_format: string
  checksum: string
  size_bytes: number
  created_at: string
}

export interface PaginationMeta {
  total: number
  skip: number
  limit: number
}
