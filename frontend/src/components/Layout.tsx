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
  Sun,
  Moon,
} from 'lucide-react'
import { useState } from 'react'
import { useTheme } from '../hooks/useTheme'
import { SpaceGrid, GradientOrbs, GradientLines } from './Background'

const navItems = [
  { to: '/', label: '工作台', icon: LayoutDashboard },
  { to: '/generate', label: '生成文章', icon: Sparkles },
  { to: '/articles', label: '文章管理', icon: FolderOpen },
  { to: '/settings', label: '系统配置', icon: Settings },
]

export default function Layout() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const location = useLocation()
  const { theme, toggle } = useTheme()

  const currentPage = navItems.find(item => {
    if (item.to === '/') return location.pathname === '/'
    return location.pathname.startsWith(item.to)
  })

  return (
    <div className="flex h-screen overflow-hidden bg-surface relative">
      <SpaceGrid />
      <GradientOrbs />
      <GradientLines />

      {sidebarOpen && (
        <div
          className="fixed inset-0 z-30 bg-black/60 backdrop-blur-sm lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      <aside
        className={`
          fixed inset-y-0 left-0 z-40 w-64 flex flex-col
          border-r border-border
          transition-transform duration-300 ease-out lg:static lg:translate-x-0
          ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
        `}
        style={{ background: 'var(--sidebar-bg)', backdropFilter: 'blur(20px)' }}
      >
        <div className="flex h-16 items-center gap-3 px-5 relative z-10">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-brand via-brand-dark to-cyan shadow-lg shadow-brand-glow relative">
            <Cpu className="h-4.5 w-4.5 text-white relative z-10" />
            <div className="absolute inset-0 rounded-xl bg-gradient-to-br from-brand to-cyan opacity-50 blur-md" />
          </div>
          <div>
            <span className="text-[15px] font-bold tracking-tight text-text bg-gradient-to-r from-text to-text-2 bg-clip-text">
              AI Blog Studio
            </span>
            <p className="text-[10px] leading-none text-text-4 tracking-wider uppercase">Automated Publishing</p>
          </div>
          <button
            className="ml-auto rounded-lg p-1 text-text-4 hover:text-text-2 lg:hidden"
            onClick={() => setSidebarOpen(false)}
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <nav className="flex-1 space-y-0.5 px-3 py-4 relative z-10">
          {navItems.map(item => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === '/'}
              onClick={() => setSidebarOpen(false)}
              className={({ isActive }) =>
                `flex items-center gap-3 rounded-xl px-3.5 py-2.5 text-[13px] font-medium transition-all duration-200 ${
                  isActive
                    ? 'bg-gradient-to-r from-brand/12 to-cyan/8 text-brand-light shadow-sm shadow-brand-glow border border-brand/10'
                    : 'text-text-3 hover:bg-surface-3/60 hover:text-text-2 border border-transparent'
                }`
              }
            >
              <item.icon className="h-[18px] w-[18px]" />
              {item.label}
            </NavLink>
          ))}
        </nav>

        <div className="px-5 py-4 border-t border-border relative z-10">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <div className="relative">
                <div className="h-2 w-2 rounded-full bg-success-2" />
                <div className="absolute inset-0 h-2 w-2 rounded-full bg-success-2 animate-ping opacity-40" />
              </div>
              <p className="text-[11px] text-text-4">System Online</p>
            </div>
            <button
              onClick={toggle}
              className="flex h-8 w-8 items-center justify-center rounded-lg border border-border bg-surface-3/50 text-text-3 transition-all duration-200 hover:border-border-light hover:text-text-2 hover:bg-surface-4/50"
              title={theme === 'dark' ? '切换浅色模式' : '切换深色模式'}
            >
              {theme === 'dark' ? <Sun className="h-3.5 w-3.5" /> : <Moon className="h-3.5 w-3.5" />}
            </button>
          </div>
        </div>
      </aside>

      <div className="flex flex-1 flex-col overflow-hidden relative z-10">
        <header
          className="flex h-14 items-center gap-4 border-b border-border px-5 lg:px-8"
          style={{ background: 'var(--header-bg)', backdropFilter: 'blur(16px)' }}
        >
          <button
            className="rounded-lg p-1.5 text-text-3 hover:bg-surface-3 hover:text-text-2 lg:hidden"
            onClick={() => setSidebarOpen(true)}
          >
            <Menu className="h-5 w-5" />
          </button>
          <div className="flex items-center gap-2.5">
            <div className="h-1.5 w-1.5 rounded-full bg-gradient-to-br from-brand to-cyan animate-pulse-glow" />
            <h1 className="text-[13px] font-semibold text-text-2">
              {currentPage?.label || 'AI Blog Studio'}
            </h1>
          </div>
          <div className="ml-auto flex items-center gap-2 lg:hidden">
            <button
              onClick={toggle}
              className="flex h-8 w-8 items-center justify-center rounded-lg border border-border text-text-3 transition-all hover:text-text-2 hover:border-border-light"
            >
              {theme === 'dark' ? <Sun className="h-3.5 w-3.5" /> : <Moon className="h-3.5 w-3.5" />}
            </button>
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
