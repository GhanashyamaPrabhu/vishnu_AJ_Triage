import { useState, useEffect, useCallback } from 'react'
import {
  PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer,
  BarChart, Bar, XAxis, YAxis, CartesianGrid
} from 'recharts'

const BACKEND_URL = 'http://localhost:8000'

const COLORS = { RED: '#ef4444', ORANGE: '#f97316', YELLOW: '#eab308', GREEN: '#22c55e' }
const BG    = { RED: '#fef2f2', ORANGE: '#fff7ed', YELLOW: '#fefce8', GREEN: '#f0fdf4' }
const TEXT  = { RED: '#991b1b', ORANGE: '#9a3412', YELLOW: '#713f12', GREEN: '#14532d' }

const categoryLabel = { RED: '🔴 Red', ORANGE: '🟠 Orange', YELLOW: '🟡 Yellow', GREEN: '🟢 Green' }

const Badge = ({ cat }) => (
  <span
    className="inline-flex px-2 py-0.5 rounded-full text-xs font-bold"
    style={{ backgroundColor: BG[cat], color: TEXT[cat], border: `1px solid ${COLORS[cat]}40` }}>
    {cat}
  </span>
)

const StatCard = ({ label, value, sub, color, icon }) => (
  <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100 flex items-start gap-4">
    <div className="w-11 h-11 rounded-lg flex items-center justify-center text-xl flex-shrink-0"
      style={{ backgroundColor: color + '20' }}>
      {icon}
    </div>
    <div className="min-w-0">
      <p className="text-sm text-gray-500 font-medium">{label}</p>
      <p className="text-2xl font-bold text-gray-900 leading-tight">{value}</p>
      {sub && <p className="text-xs text-gray-400 mt-0.5">{sub}</p>}
    </div>
  </div>
)

const CustomTooltip = ({ active, payload }) => {
  if (!active || !payload?.length) return null
  const { name, value } = payload[0]
  return (
    <div className="bg-white border border-gray-200 rounded-lg px-3 py-2 shadow text-sm">
      <span className="font-semibold" style={{ color: COLORS[name] }}>{name}</span>
      <span className="text-gray-600 ml-2">{value} cases</span>
    </div>
  )
}

const AgreementBar = ({ stats }) => {
  if (!stats || stats.total_cases === 0) return null
  const total = stats.total_cases
  const agreed = Math.round(stats.agreement_rate * total / 100)
  const under = stats.under_triage_count
  const over = stats.over_triage_count

  const pct = (n) => ((n / total) * 100).toFixed(0)

  return (
    <div>
      <div className="flex h-5 rounded-full overflow-hidden gap-0.5">
        <div style={{ width: `${pct(agreed)}%`, backgroundColor: '#22c55e' }} title={`${pct(agreed)}% Agree`} />
        <div style={{ width: `${pct(under)}%`, backgroundColor: '#ef4444' }} title={`${pct(under)}% Under-triage`} />
        <div style={{ width: `${pct(over)}%`, backgroundColor: '#f97316' }} title={`${pct(over)}% Over-triage`} />
      </div>
      <div className="flex gap-4 mt-2 text-xs text-gray-600">
        <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-sm bg-green-500 inline-block" /> Agree {agreed}</span>
        <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-sm bg-red-500 inline-block" /> Under-triage {under}</span>
        <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-sm bg-orange-500 inline-block" /> Over-triage {over}</span>
      </div>
    </div>
  )
}

const AdminDashboard = () => {
  const [stats, setStats] = useState(null)
  const [recentCases, setRecentCases] = useState([])
  const [health, setHealth] = useState(null)
  const [loading, setLoading] = useState(true)
  const [lastUpdated, setLastUpdated] = useState(null)

  const fetchAll = useCallback(async () => {
    setLoading(true)
    try {
      const [statsRes, casesRes, healthRes] = await Promise.all([
        fetch(`${BACKEND_URL}/admin/stats`),
        fetch(`${BACKEND_URL}/admin/recent-cases?limit=8`),
        fetch(`${BACKEND_URL}/health`),
      ])
      if (statsRes.ok) setStats(await statsRes.json())
      if (casesRes.ok) setRecentCases(await casesRes.json())
      if (healthRes.ok) setHealth(await healthRes.json())
      setLastUpdated(new Date())
    } catch (err) {
      console.error('Dashboard fetch failed', err)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { fetchAll() }, [fetchAll])

  const pieData = stats
    ? ['RED', 'ORANGE', 'YELLOW', 'GREEN']
        .filter(cat => stats.category_distribution[cat] > 0)
        .map(cat => ({ name: cat, value: stats.category_distribution[cat] }))
    : []

  const barData = stats
    ? ['RED', 'ORANGE', 'YELLOW', 'GREEN'].map(cat => ({
        name: cat,
        Nurse: stats.nurse_distribution[cat] || 0,
        AI: stats.category_distribution[cat] || 0,
      }))
    : []

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="mt-1 text-sm text-gray-500">
            {lastUpdated ? `Updated ${lastUpdated.toLocaleTimeString()}` : 'AJ Institute SATS Co-Pilot'}
          </p>
        </div>
        <div className="flex gap-3">
          <a href={`${BACKEND_URL}/admin/export`}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-lg border border-gray-300 bg-white text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors">
            ⬇ Export CSV
          </a>
          <button onClick={fetchAll}
            disabled={loading}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-blue-600 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-60 transition-colors">
            {loading ? '⟳ Loading…' : '↺ Refresh'}
          </button>
        </div>
      </div>

      {/* Stat cards */}
      <div className="grid grid-cols-2 lg:grid-cols-5 gap-4 mb-8">
        <StatCard label="Total Cases" value={stats?.total_cases ?? '—'} icon="📋" color="#3b82f6" />
        <StatCard
          label="Agreement Rate"
          value={stats ? `${stats.agreement_rate}%` : '—'}
          sub="Nurse vs AI"
          icon="✅"
          color="#22c55e"
        />
        <StatCard
          label="Avg AI Confidence"
          value={stats ? `${stats.avg_confidence}%` : '—'}
          icon="🤖"
          color="#8b5cf6"
        />
        <StatCard
          label="Under-triage"
          value={stats?.under_triage_count ?? '—'}
          sub="AI higher than Nurse"
          icon="⚠️"
          color="#ef4444"
        />
        <StatCard
          label="Hard-Stop Rules"
          value={stats?.hard_stop_count ?? '—'}
          sub="Auto-escalated to RED"
          icon="🛑"
          color="#f97316"
        />
      </div>

      {/* Charts row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* AI Category Distribution */}
        <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
          <h3 className="font-semibold text-gray-900 mb-4">AI Category Distribution</h3>
          {pieData.length === 0 ? (
            <div className="h-48 flex items-center justify-center text-gray-400 text-sm">
              No data yet — submit a triage case to see stats
            </div>
          ) : (
            <ResponsiveContainer width="100%" height={220}>
              <PieChart>
                <Pie data={pieData} cx="50%" cy="50%" innerRadius={55} outerRadius={85}
                  dataKey="value" paddingAngle={3}>
                  {pieData.map(entry => (
                    <Cell key={entry.name} fill={COLORS[entry.name]} />
                  ))}
                </Pie>
                <Tooltip content={<CustomTooltip />} />
                <Legend formatter={(val) => categoryLabel[val] || val} />
              </PieChart>
            </ResponsiveContainer>
          )}
        </div>

        {/* Nurse vs AI comparison */}
        <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
          <h3 className="font-semibold text-gray-900 mb-4">Nurse vs AI — Category Comparison</h3>
          {!stats || stats.total_cases === 0 ? (
            <div className="h-48 flex items-center justify-center text-gray-400 text-sm">
              No data yet
            </div>
          ) : (
            <>
              <ResponsiveContainer width="100%" height={170}>
                <BarChart data={barData} barSize={14} barGap={2}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" />
                  <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                  <YAxis tick={{ fontSize: 11 }} allowDecimals={false} />
                  <Tooltip />
                  <Legend iconSize={10} wrapperStyle={{ fontSize: 12 }} />
                  <Bar dataKey="Nurse" fill="#60a5fa" radius={[3, 3, 0, 0]} />
                  <Bar dataKey="AI" fill="#8b5cf6" radius={[3, 3, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
              <div className="mt-4">
                <p className="text-xs font-medium text-gray-600 mb-2">Agreement breakdown</p>
                <AgreementBar stats={stats} />
              </div>
            </>
          )}
        </div>
      </div>

      {/* Recent cases + System status */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent cases */}
        <div className="lg:col-span-2 bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
          <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100">
            <h3 className="font-semibold text-gray-900">Recent Cases</h3>
            <a href="/history" className="text-sm text-blue-600 hover:underline">View all →</a>
          </div>

          {recentCases.length === 0 ? (
            <div className="py-12 text-center text-gray-400 text-sm">
              No cases submitted yet. Use the triage form to add cases.
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full">
                <thead>
                  <tr className="bg-gray-50 text-left">
                    {['Case ID', 'Nurse', 'AI', 'Match', 'Confidence', 'Time'].map(h => (
                      <th key={h} className="px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-50">
                  {recentCases.map((c, i) => {
                    const agree = c.nurse_category === c.ai_recommendation
                    return (
                      <tr key={i} className="hover:bg-gray-50 transition-colors">
                        <td className="px-4 py-3 text-sm font-mono text-gray-700">{c.case_id}</td>
                        <td className="px-4 py-3"><Badge cat={c.nurse_category} /></td>
                        <td className="px-4 py-3"><Badge cat={c.ai_recommendation} /></td>
                        <td className="px-4 py-3">
                          {agree
                            ? <span className="text-green-600 text-sm font-medium">✓ Match</span>
                            : <span className="text-red-600 text-sm font-medium">✗ Diff</span>}
                        </td>
                        <td className="px-4 py-3">
                          <div className="flex items-center gap-1.5">
                            <div className="w-16 bg-gray-100 rounded-full h-1.5">
                              <div className="h-1.5 rounded-full bg-purple-500"
                                style={{ width: `${Math.round(c.confidence * 100)}%` }} />
                            </div>
                            <span className="text-xs text-gray-500">{Math.round(c.confidence * 100)}%</span>
                          </div>
                        </td>
                        <td className="px-4 py-3 text-xs text-gray-400">
                          {new Date(c.timestamp).toLocaleString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Right column: System status + legend */}
        <div className="space-y-4">
          {/* System status */}
          <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
            <h3 className="font-semibold text-gray-900 mb-3">System Status</h3>
            {[
              { label: 'API Server', ok: !!health },
              { label: 'AI Service (Claude)', ok: health?.ai_service_available },
              { label: 'Database', ok: health?.database_connected },
            ].map(({ label, ok }) => (
              <div key={label} className="flex items-center justify-between py-1.5">
                <span className="text-sm text-gray-600">{label}</span>
                <span className={`flex items-center gap-1.5 text-xs font-medium ${ok ? 'text-green-600' : 'text-gray-400'}`}>
                  <span className={`w-2 h-2 rounded-full ${ok ? 'bg-green-500' : 'bg-gray-300'}`} />
                  {ok ? 'Online' : loading ? '…' : 'Offline'}
                </span>
              </div>
            ))}
            {health && (
              <p className="text-xs text-gray-400 mt-3 pt-3 border-t">
                Uptime {Math.floor(health.uptime_seconds / 60)}m · v{health.version}
              </p>
            )}
          </div>

          {/* SATS reference */}
          <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
            <h3 className="font-semibold text-gray-900 mb-3">SATS Reference</h3>
            {[
              { cat: 'RED',    label: 'Immediate',   time: 'Now'    },
              { cat: 'ORANGE', label: 'Very Urgent',  time: '10 min' },
              { cat: 'YELLOW', label: 'Urgent',       time: '1 hr'   },
              { cat: 'GREEN',  label: 'Routine',      time: 'Wait'   },
            ].map(({ cat, label, time }) => (
              <div key={cat} className="flex items-center gap-3 py-1.5">
                <span className="w-3 h-3 rounded-full flex-shrink-0" style={{ backgroundColor: COLORS[cat] }} />
                <span className="text-sm text-gray-700 flex-1">{label}</span>
                <span className="text-xs text-gray-400">{time}</span>
              </div>
            ))}
          </div>

          {/* Under-triage alert */}
          {stats && stats.under_triage_count > 0 && (
            <div className="bg-red-50 border border-red-200 rounded-xl p-5">
              <h3 className="font-semibold text-red-800 mb-1">Under-triage Alert</h3>
              <p className="text-sm text-red-700">
                <span className="font-bold text-lg">{stats.under_triage_count}</span> case{stats.under_triage_count !== 1 ? 's' : ''} where AI flagged a higher risk than the nurse.
              </p>
              <a href="/history?agreement=false"
                className="inline-block mt-2 text-xs font-medium text-red-700 underline hover:text-red-900">
                Review discrepancy cases →
              </a>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default AdminDashboard
