import { NavLink, Outlet, useLocation } from 'react-router-dom'
import {
  LayoutDashboard,
  PenLine,
  FolderOpen,
  Settings,
  Sparkles,
  Menu,
  X,
  Cpu,
} from 'lucide-react'
import { useState } from 'react'

const navItems = [
  { to: '/', label: '工作台', icon: LayoutDashboard },
  { to: '/generate', label: '生成文章', icon: Sparkles },
  { to: '/articles', label: '文章管理', icon: FolderOpen },
  { to: '/settings', label: '系统配置', icon: Settings },
]

export default function Layout() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const location = useLocation()

  const currentPage = navItems.find(item => {
    if (item.to === '/') return location.pathname === '/'
    return location.pathname.startsWith(item.to)
  })

  return (
    <div className="flex h-screen overflow-hidden bg-surface">
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-30 bg-black/60 backdrop-blur-sm lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      <aside
        className={`
          fixed inset-y-0 left-0 z-40 w-64 flex flex-col
          bg-surface-2 border-r border-border
          transition-transform duration-300 ease-out lg:static lg:translate-x-0
          ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
        `}
      >
        <div className="flex h-16 items-center gap-3 px-5">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-brand to-brand-dark shadow-lg shadow-brand-glow">
            <Cpu className="h-4.5 w-4.5 text-white" />
          </div>
          <div>
            <span className="text-[15px] font-bold tracking-tight text-text">
              AI Blog Studio
            </span>
            <p className="text-[10px] leading-none text-text-4">Automated Publishing</p>
          </div>
          <button
            className="ml-auto rounded-lg p-1 text-text-4 hover:text-text-2 lg:hidden"
            onClick={() => setSidebarOpen(false)}
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <nav className="flex-1 space-y-0.5 px-3 py-4">
          {navItems.map(item => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === '/'}
              onClick={() => setSidebarOpen(false)}
              className={({ isActive }) =>
                `flex items-center gap-3 rounded-xl px-3.5 py-2.5 text-[13px] font-medium transition-all duration-200 ${
                  isActive
                    ? 'bg-brand/10 text-brand-light shadow-sm shadow-brand-glow'
                    : 'text-text-3 hover:bg-surface-3 hover:text-text-2'
                }`
              }
            >
              <item.icon className="h-[18px] w-[18px]" />
              {item.label}
            </NavLink>
          ))}
        </nav>

        <div className="px-5 py-4 border-t border-border">
          <div className="flex items-center gap-2.5">
            <div className="h-2 w-2 rounded-full bg-success-2 animate-pulse" />
            <p className="text-[11px] text-text-4">System Online</p>
          </div>
        </div>
      </aside>

      <div className="flex flex-1 flex-col overflow-hidden">
        <header className="flex h-14 items-center gap-4 border-b border-border bg-surface-2/80 backdrop-blur-md px-5 lg:px-8">
          <button
            className="rounded-lg p-1.5 text-text-3 hover:bg-surface-3 hover:text-text-2 lg:hidden"
            onClick={() => setSidebarOpen(true)}
          >
            <Menu className="h-5 w-5" />
          </button>
          <div className="flex items-center gap-2">
            <div className="h-1 w-1 rounded-full bg-brand" />
            <h1 className="text-[13px] font-semibold text-text-2">
              {currentPage?.label || 'AI Blog Studio'}
            </h1>
          </div>
        </header>

        <main className="flex-1 overflow-y-auto p-5 lg:p-8">
          <div className="animate-fade-in">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  )
}
