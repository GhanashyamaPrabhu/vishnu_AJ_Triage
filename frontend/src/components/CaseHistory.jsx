import { useState, useEffect, useCallback } from 'react'

const BACKEND_URL = 'http://localhost:8000'
const COLORS = { RED: '#ef4444', ORANGE: '#f97316', YELLOW: '#eab308', GREEN: '#22c55e' }
const BG    = { RED: '#fef2f2', ORANGE: '#fff7ed', YELLOW: '#fefce8', GREEN: '#f0fdf4' }
const TEXT  = { RED: '#991b1b', ORANGE: '#9a3412', YELLOW: '#713f12', GREEN: '#14532d' }

const Badge = ({ cat }) => (
  <span
    className="inline-flex px-2 py-0.5 rounded-full text-xs font-bold"
    style={{ backgroundColor: BG[cat], color: TEXT[cat], border: `1px solid ${COLORS[cat]}40` }}>
    {cat}
  </span>
)

const SORT_ICONS = { asc: '↑', desc: '↓', none: '↕' }

const CaseHistory = () => {
  const [allCases, setAllCases]       = useState([])
  const [loading, setLoading]         = useState(true)
  const [error, setError]             = useState('')
  const [categoryFilter, setCategoryFilter] = useState('')
  const [agreementFilter, setAgreementFilter] = useState('')
  const [search, setSearch]           = useState('')
  const [sortKey, setSortKey]         = useState('timestamp')
  const [sortDir, setSortDir]         = useState('desc')
  const [selectedCase, setSelectedCase] = useState(null)

  const fetchCases = useCallback(async () => {
    setLoading(true)
    setError('')
    try {
      const res = await fetch(`${BACKEND_URL}/cases`)
      if (!res.ok) throw new Error('Failed to fetch cases')
      setAllCases(await res.json())
    } catch (err) {
      setError('Could not load cases. Is the backend running?')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { fetchCases() }, [fetchCases])

  // ── Filtering ──────────────────────────────────────────────────────────────
  const filtered = allCases.filter(c => {
    if (categoryFilter) {
      if (c.ai_recommendation !== categoryFilter && c.nurse_category !== categoryFilter) return false
    }
    if (agreementFilter === 'agree' && c.nurse_category !== c.ai_recommendation) return false
    if (agreementFilter === 'disagree' && c.nurse_category === c.ai_recommendation) return false
    if (search) {
      const q = search.toLowerCase()
      if (
        !c.case_id?.toLowerCase().includes(q) &&
        !c.clinical_narrative?.toLowerCase().includes(q)
      ) return false
    }
    return true
  })

  // ── Sorting ────────────────────────────────────────────────────────────────
  const sorted = [...filtered].sort((a, b) => {
    let va = a[sortKey] ?? ''
    let vb = b[sortKey] ?? ''
    if (sortKey === 'confidence') { va = parseFloat(va); vb = parseFloat(vb) }
    const cmp = va < vb ? -1 : va > vb ? 1 : 0
    return sortDir === 'asc' ? cmp : -cmp
  })

  const handleSort = (key) => {
    if (sortKey === key) setSortDir(d => d === 'asc' ? 'desc' : 'asc')
    else { setSortKey(key); setSortDir('desc') }
  }

  const SortHeader = ({ label, k }) => (
    <th
      className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wide cursor-pointer select-none hover:text-gray-800 transition-colors"
      onClick={() => handleSort(k)}>
      {label} <span className="ml-0.5 opacity-50">{sortKey === k ? SORT_ICONS[sortDir] : SORT_ICONS.none}</span>
    </th>
  )

  // ── Detail modal ──────────────────────────────────────────────────────────
  const DetailModal = ({ c, onClose }) => {
    const agree = c.nurse_category === c.ai_recommendation
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4"
        style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}
        onClick={(e) => { if (e.target === e.currentTarget) onClose() }}>
        <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
          {/* Modal header */}
          <div className="flex items-center justify-between px-6 py-4 border-b">
            <div>
              <h2 className="text-lg font-bold text-gray-900">{c.case_id}</h2>
              <p className="text-xs text-gray-500 mt-0.5">
                {new Date(c.timestamp).toLocaleString()}
              </p>
            </div>
            <button onClick={onClose}
              className="w-8 h-8 rounded-full bg-gray-100 hover:bg-gray-200 flex items-center justify-center text-gray-500 transition-colors">
              ✕
            </button>
          </div>

          <div className="p-6 space-y-5">
            {/* Triage comparison */}
            <div className="grid grid-cols-2 gap-4">
              <div className="rounded-xl p-4" style={{ backgroundColor: BG[c.nurse_category] }}>
                <p className="text-xs font-semibold text-gray-500 mb-1">Nurse Assessment</p>
                <Badge cat={c.nurse_category} />
              </div>
              <div className="rounded-xl p-4" style={{ backgroundColor: BG[c.ai_recommendation] }}>
                <p className="text-xs font-semibold text-gray-500 mb-1">AI Recommendation</p>
                <div className="flex items-center gap-2">
                  <Badge cat={c.ai_recommendation} />
                  <span className="text-xs text-gray-500">{Math.round(c.confidence * 100)}% confidence</span>
                </div>
              </div>
            </div>

            {/* Agreement banner */}
            <div className={`rounded-lg px-4 py-2.5 text-sm font-medium ${agree ? 'bg-green-50 text-green-800' : 'bg-red-50 text-red-800'}`}>
              {agree ? '✓ Nurse and AI agree on this case' : '⚠ Discrepancy — nurse and AI disagree. Flagged for Gold Standard review.'}
            </div>

            {/* Hard rule */}
            {c.hard_rule_triggered && (
              <div className="bg-red-50 border border-red-200 rounded-lg px-4 py-3">
                <p className="text-xs font-bold text-red-700 uppercase mb-0.5">Hard-Stop Rule Triggered</p>
                <p className="text-sm text-red-700">{c.ai_reasoning}</p>
              </div>
            )}

            {/* Clinical narrative */}
            <div>
              <p className="text-xs font-semibold text-gray-500 uppercase mb-1">Clinical Narrative</p>
              <div className="bg-gray-50 rounded-lg p-3 text-sm text-gray-700 leading-relaxed">
                {c.clinical_narrative || '—'}
              </div>
            </div>

            {/* AI reasoning */}
            {c.ai_reasoning && !c.hard_rule_triggered && (
              <div>
                <p className="text-xs font-semibold text-gray-500 uppercase mb-1">AI Analysis</p>
                <div className="bg-purple-50 rounded-lg p-3 text-sm text-purple-900 leading-relaxed">
                  {c.ai_reasoning}
                </div>
              </div>
            )}

            {/* Red flags */}
            {Array.isArray(c.red_flags) && c.red_flags.length > 0 && (
              <div>
                <p className="text-xs font-semibold text-gray-500 uppercase mb-2">Red Flags</p>
                <div className="flex flex-wrap gap-1.5">
                  {c.red_flags.map((flag, i) => (
                    <span key={i} className="bg-red-100 text-red-800 text-xs px-2 py-1 rounded-full">
                      {flag}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    )
  }

  // ── Summary bar ───────────────────────────────────────────────────────────
  const total = allCases.length
  const agree = allCases.filter(c => c.nurse_category === c.ai_recommendation).length

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Case History</h1>
          <p className="mt-1 text-sm text-gray-500">
            {total > 0 ? `${total} total · ${agree} agreed · ${total - agree} discrepancies` : 'No cases yet'}
          </p>
        </div>
        <button onClick={fetchCases}
          disabled={loading}
          className="px-4 py-2 rounded-lg bg-blue-600 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-60 transition-colors">
          {loading ? '⟳ Loading…' : '↺ Refresh'}
        </button>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100 mb-5 flex flex-wrap gap-3 items-center">
        {/* Search */}
        <div className="relative flex-1 min-w-48">
          <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 text-sm">🔍</span>
          <input
            type="text"
            placeholder="Search by case ID or narrative…"
            value={search}
            onChange={e => setSearch(e.target.value)}
            className="w-full pl-9 pr-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-300"
          />
        </div>

        {/* Category filter */}
        <div className="flex gap-1.5">
          {['', 'RED', 'ORANGE', 'YELLOW', 'GREEN'].map(cat => (
            <button key={cat}
              onClick={() => setCategoryFilter(cat)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
                categoryFilter === cat
                  ? cat ? 'text-white' : 'bg-gray-800 text-white'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
              style={categoryFilter === cat && cat ? { backgroundColor: COLORS[cat], color: '#fff' } : {}}>
              {cat || 'All'}
            </button>
          ))}
        </div>

        {/* Agreement filter */}
        <div className="flex gap-1.5">
          {[
            { val: '',        label: 'All' },
            { val: 'agree',   label: '✓ Match' },
            { val: 'disagree',label: '✗ Differ' },
          ].map(({ val, label }) => (
            <button key={val}
              onClick={() => setAgreementFilter(val)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
                agreementFilter === val ? 'bg-gray-800 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}>
              {label}
            </button>
          ))}
        </div>

        {/* Clear */}
        {(categoryFilter || agreementFilter || search) && (
          <button
            onClick={() => { setCategoryFilter(''); setAgreementFilter(''); setSearch('') }}
            className="px-3 py-1.5 text-xs text-gray-500 hover:text-gray-800 underline transition-colors">
            Clear filters
          </button>
        )}
      </div>

      {/* Error */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg px-4 py-3 mb-5 text-sm text-red-700 flex items-center gap-2">
          ⚠ {error}
        </div>
      )}

      {/* Table */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="flex items-center justify-between px-5 py-3 border-b border-gray-100">
          <span className="text-sm font-medium text-gray-700">
            {sorted.length === total ? `${total} cases` : `${sorted.length} of ${total} cases`}
          </span>
        </div>

        {loading ? (
          <div className="py-16 text-center text-gray-400">
            <div className="inline-block w-6 h-6 border-2 border-blue-300 border-t-blue-600 rounded-full animate-spin mb-3" />
            <p className="text-sm">Loading cases…</p>
          </div>
        ) : sorted.length === 0 ? (
          <div className="py-16 text-center text-gray-400">
            <p className="text-2xl mb-2">📭</p>
            <p className="text-sm">{total === 0 ? 'No cases submitted yet. Use the triage form to get started.' : 'No cases match the current filters.'}</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full">
              <thead className="bg-gray-50">
                <tr>
                  <SortHeader label="Case ID"    k="case_id" />
                  <SortHeader label="Nurse"      k="nurse_category" />
                  <SortHeader label="AI"         k="ai_recommendation" />
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wide">Match</th>
                  <SortHeader label="Confidence" k="confidence" />
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wide">GCS</th>
                  <SortHeader label="Time"       k="timestamp" />
                  <th className="px-4 py-3" />
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {sorted.map((c, i) => {
                  const agree = c.nurse_category === c.ai_recommendation
                  return (
                    <tr key={i}
                      onClick={() => setSelectedCase(c)}
                      className="hover:bg-blue-50 cursor-pointer transition-colors">
                      <td className="px-4 py-3 text-sm font-mono text-gray-700">{c.case_id}</td>
                      <td className="px-4 py-3"><Badge cat={c.nurse_category} /></td>
                      <td className="px-4 py-3"><Badge cat={c.ai_recommendation} /></td>
                      <td className="px-4 py-3">
                        <span className={`text-xs font-semibold px-2 py-1 rounded-full ${agree ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                          {agree ? '✓ Match' : '✗ Differ'}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-1.5">
                          <div className="w-14 bg-gray-100 rounded-full h-1.5">
                            <div className="h-1.5 rounded-full bg-purple-500"
                              style={{ width: `${Math.round(c.confidence * 100)}%` }} />
                          </div>
                          <span className="text-xs text-gray-500 w-8">{Math.round(c.confidence * 100)}%</span>
                        </div>
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-600">
                        {c.gcs_total ? `${c.gcs_total}/15` : '—'}
                      </td>
                      <td className="px-4 py-3 text-xs text-gray-400 whitespace-nowrap">
                        {new Date(c.timestamp).toLocaleString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}
                      </td>
                      <td className="px-4 py-3 text-xs text-blue-500 font-medium pr-5">View →</td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Detail modal */}
      {selectedCase && <DetailModal c={selectedCase} onClose={() => setSelectedCase(null)} />}
    </div>
  )
}

export default CaseHistory
