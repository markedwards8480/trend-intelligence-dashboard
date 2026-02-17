import { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { Menu, X, LayoutDashboard, PlusCircle, Globe, Image, Radio, BarChart3, TrendingUp, Users, Sparkles } from 'lucide-react'

export default function Layout({ children }: { children: React.ReactNode }) {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const location = useLocation()

  const navItems = [
    { icon: LayoutDashboard, label: 'Dashboard', href: '/' },
    { icon: Users, label: 'People', href: '/people' },
    { icon: Sparkles, label: 'Trend Feed', href: '/feed' },
    { icon: Globe, label: 'Sources', href: '/sources' },
    { icon: PlusCircle, label: 'Submit Trend', href: '/submit' },
    { icon: Image, label: 'Mood Boards', href: '/moodboards' },
    { icon: Radio, label: 'Monitoring', href: '/monitoring' },
    { icon: BarChart3, label: 'Analytics', href: '/analytics' },
  ]

  const isActive = (href: string) => location.pathname === href

  return (
    <div className="flex h-screen bg-white">
      {/* Sidebar */}
      <div
        className={`${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        } fixed inset-y-0 left-0 z-40 w-64 bg-white border-r border-accent-100 transition-transform duration-300 lg:translate-x-0 lg:static overflow-y-auto`}
      >
        {/* Logo/Branding */}
        <div className="p-6 border-b border-accent-100">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-primary-400 to-primary-600 rounded-lg flex items-center justify-center">
              <TrendingUp className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="font-display font-bold text-accent-900 text-lg">MEA Trends</h1>
              <p className="text-xs text-accent-500">Mark Edwards</p>
            </div>
          </div>
        </div>

        {/* Navigation */}
        <nav className="p-4">
          <div className="space-y-2">
            {navItems.map((item) => {
              const Icon = item.icon
              return (
                <Link
                  key={item.href}
                  to={item.href}
                  onClick={() => setSidebarOpen(false)}
                  className={`flex items-center gap-3 px-4 py-3 rounded-lg font-medium transition-all duration-200 ${
                    isActive(item.href)
                      ? 'bg-primary-50 text-primary-700 border-l-4 border-primary-600'
                      : 'text-accent-600 hover:bg-accent-50'
                  }`}
                >
                  <Icon className="w-5 h-5" />
                  <span>{item.label}</span>
                </Link>
              )
            })}
          </div>
        </nav>

        {/* Footer */}
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-accent-100">
          <p className="text-xs text-accent-500">
            v1.0.0 • Trend Intelligence
          </p>
        </div>
      </div>

      {/* Overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-30 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <header className="bg-white border-b border-accent-100 h-16 flex items-center justify-between px-6 lg:px-8">
          <button
            onClick={() => setSidebarOpen(true)}
            className="lg:hidden p-2 hover:bg-accent-50 rounded-lg transition-colors"
          >
            <Menu className="w-6 h-6 text-accent-900" />
          </button>

          <div className="flex-1 lg:flex-none" />

          <div className="flex items-center gap-4">
            <div className="hidden sm:flex items-center gap-2 px-4 py-2 bg-accent-50 rounded-lg">
              <div className="w-8 h-8 bg-gradient-to-br from-primary-300 to-primary-500 rounded-full" />
              <div>
                <p className="text-sm font-medium text-accent-900">Mark Edwards</p>
                <p className="text-xs text-accent-500">Apparel</p>
              </div>
            </div>
            <button className="p-2 hover:bg-accent-50 rounded-lg transition-colors lg:hidden">
              <X className="w-6 h-6 text-accent-900" onClick={() => setSidebarOpen(false)} />
            </button>
          </div>
        </header>

        {/* Content */}
        <main className="flex-1 overflow-auto bg-gradient-to-br from-white via-primary-50 to-white">
          <div className="max-w-7xl mx-auto">
            {children}
          </div>
        </main>
      </div>
    </div>
  )
}
