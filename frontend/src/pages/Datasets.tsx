import { useEffect, useState } from 'react'
import { api } from '../lib/api'
import { Card, CardContent, CardHeader, CardTitle, Button, Input, Badge, EmptyState, Skeleton } from '../components/UI'
import { formatDate } from '../lib/utils'

export default function Datasets() {
  const [datasets, setDatasets] = useState<any[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [uploading, setUploading] = useState(false)
  const [uploadName, setUploadName] = useState('')
  const [uploadFormat, setUploadFormat] = useState('csv')
  const [uploadFile, setUploadFile] = useState<File | null>(null)
  const [uploadDesc, setUploadDesc] = useState('')
  const [uploadError, setUploadError] = useState<string | null>(null)

  const fetchDatasets = () => {
    setLoading(true)
    api.datasets.list(0, 50)
      .then(data => { setDatasets(data.items || []); setTotal(data.total) })
      .finally(() => setLoading(false))
  }

  useEffect(() => { fetchDatasets() }, [])

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!uploadFile) return
    setUploadError(null)
    setUploading(true)
    try {
      await api.datasets.upload(uploadName, uploadFormat, uploadDesc || null, uploadFile)
      setUploadName('')
      setUploadFile(null)
      setUploadDesc('')
      fetchDatasets()
    } catch (err: any) {
      setUploadError(err.message)
    } finally {
      setUploading(false)
    }
  }

  const handleDelete = async (id: string) => {
    if (!confirm('Delete this dataset?')) return
    try {
      await api.datasets.delete(id)
      fetchDatasets()
    } catch (err: any) {
      alert(err.message)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Datasets</h1>
          <p className="text-sm text-muted-foreground mt-1">{total} datasets stored</p>
        </div>
      </div>

      {/* Upload form */}
      <Card>
        <CardHeader><CardTitle>Upload Dataset</CardTitle></CardHeader>
        <CardContent>
          <form onSubmit={handleUpload} className="space-y-3">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-xs font-medium mb-1 block">Name *</label>
                <Input value={uploadName} onChange={e => setUploadName(e.target.value)} placeholder="Dataset name" required />
              </div>
              <div>
                <label className="text-xs font-medium mb-1 block">Format *</label>
                <Input value={uploadFormat} onChange={e => setUploadFormat(e.target.value)} placeholder="csv, json, npz..." />
              </div>
            </div>
            <div>
              <label className="text-xs font-medium mb-1 block">Description</label>
              <Input value={uploadDesc} onChange={e => setUploadDesc(e.target.value)} placeholder="Optional description" />
            </div>
            <div>
              <label className="text-xs font-medium mb-1 block">File *</label>
              <input type="file" onChange={e => setUploadFile(e.target.files?.[0] || null)} className="text-xs text-muted-foreground" accept=".csv,.json,.tsv,.npz,.npy,.txt,.parquet" />
            </div>
            {uploadError && <p className="text-xs text-destructive">{uploadError}</p>}
            <Button type="submit" disabled={uploading || !uploadFile || !uploadName}>
              {uploading ? 'Uploading...' : 'Upload'}
            </Button>
          </form>
        </CardContent>
      </Card>

      {/* Dataset list */}
      <Card>
        <CardHeader><CardTitle>Stored Datasets</CardTitle></CardHeader>
        <CardContent>
          {loading ? (
            <div className="space-y-2">
              {[1, 2, 3].map(i => <Skeleton key={i} className="h-12 rounded" />)}
            </div>
          ) : datasets.length === 0 ? (
            <EmptyState title="No datasets" description="Upload your first dataset to get started." />
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-border text-muted-foreground text-xs">
                    <th className="text-left pb-2 pr-4">Name</th>
                    <th className="text-left pb-2 pr-4">Format</th>
                    <th className="text-right pb-2 pr-4">Size</th>
                    <th className="text-left pb-2 pr-4">Checksum</th>
                    <th className="text-left pb-2 pr-4">Created</th>
                    <th className="text-left pb-2">Action</th>
                  </tr>
                </thead>
                <tbody>
                  {datasets.map(ds => (
                    <tr key={ds.id} className="border-b border-border/50 hover:bg-muted/50">
                      <td className="py-2 pr-4 font-medium text-xs">{ds.name}</td>
                      <td className="py-2 pr-4"><Badge variant="outline">{ds.file_format}</Badge></td>
                      <td className="py-2 pr-4 text-xs text-muted-foreground text-right">
                        {(ds.size_bytes / 1024).toFixed(1)} KB
                      </td>
                      <td className="py-2 pr-4 font-mono text-xs text-muted-foreground">{ds.checksum.slice(0, 12)}...</td>
                      <td className="py-2 pr-4 text-xs text-muted-foreground">{formatDate(ds.created_at)}</td>
                      <td className="py-2">
                        <Button variant="ghost" size="sm" className="h-6 px-2 text-xs text-red-400 hover:text-red-300" onClick={() => handleDelete(ds.id)}>
                          Delete
                        </Button>
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
