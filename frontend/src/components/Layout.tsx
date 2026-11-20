import { Link, useLocation } from 'react-router-dom'
import { FlaskConical, LayoutDashboard, PlayCircle, BarChart3, Database, Settings, Beaker } from 'lucide-react'
import { cn } from '../lib/utils'

const navItems = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/experiments', label: 'Experiments', icon: FlaskConical },
  { to: '/runs', label: 'Runs', icon: PlayCircle },
  { to: '/results', label: 'Results', icon: BarChart3 },
  { to: '/datasets', label: 'Datasets', icon: Database },
  { to: '/settings', label: 'Settings', icon: Settings },
]

interface Props {
  children: React.ReactNode
}

export default function Layout({ children }: Props) {
  const location = useLocation()

  return (
    <div className="min-h-screen bg-background flex">
      {/* Sidebar */}
      <aside className="w-56 border-r border-border bg-card flex flex-col fixed h-full z-20">
        <div className="p-4 border-b border-border">
          <Link to="/" className="flex items-center gap-2 text-primary font-bold text-lg">
            <Beaker className="h-5 w-5" />
            ResearchLab
          </Link>
        </div>
        <nav className="flex-1 p-2 space-y-1">
          {navItems.map(item => {
            const active = location.pathname.startsWith(item.to) || (item.to === '/' && location.pathname === '/')
            return (
              <Link
                key={item.to}
                to={item.to}
                className={cn(
                  'flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-colors',
                  active
                    ? 'bg-primary/10 text-primary font-medium'
                    : 'text-muted-foreground hover:text-foreground hover:bg-accent',
                )}
              >
                <item.icon className="h-4 w-4 shrink-0" />
                {item.label}
              </Link>
            )
          })}
        </nav>
        <div className="p-3 border-t border-border text-xs text-muted-foreground">
          v0.1.0 · Scientific Orchestration
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 ml-56 min-h-screen">
        <div className="max-w-7xl mx-auto px-6 py-6">
          {children}
        </div>
      </main>
    </div>
  )
}
