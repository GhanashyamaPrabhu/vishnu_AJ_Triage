const COLORS = { RED: '#ef4444', ORANGE: '#f97316', YELLOW: '#eab308', GREEN: '#22c55e' }
const BG     = { RED: '#fef2f2', ORANGE: '#fff7ed', YELLOW: '#fefce8', GREEN: '#f0fdf4' }
const TEXT   = { RED: '#7f1d1d', ORANGE: '#7c2d12', YELLOW: '#713f12', GREEN: '#14532d' }
const LABELS = { RED: 'Immediate', ORANGE: 'Very Urgent', YELLOW: 'Urgent', GREEN: 'Routine' }
const TIME   = { RED: 'Act NOW', ORANGE: 'Within 10 min', YELLOW: 'Within 1 hr', GREEN: 'Routine care' }

const ResultCard = ({ result }) => {
  if (!result) return null

  const ai     = result.ai_recommendation
  const nurse  = result.nurse_category
  const agree  = ai === nurse
  const conf   = Math.round((result.confidence ?? 0) * 100)

  return (
    <div className="space-y-4 animate-fade-in">

      {/* ── Big AI result banner ─────────────────────────────────── */}
      <div className="rounded-2xl overflow-hidden shadow-md border-2"
        style={{ borderColor: COLORS[ai], backgroundColor: BG[ai] }}>
        {/* Top strip */}
        <div className="px-6 py-3 flex items-center justify-between"
          style={{ backgroundColor: COLORS[ai] }}>
          <span className="text-white text-sm font-semibold tracking-wide uppercase">
            AI Triage Recommendation
          </span>
          {result.hard_rule_triggered && (
            <span className="bg-white text-red-700 text-xs font-bold px-2.5 py-1 rounded-full">
              HARD-STOP RULE
            </span>
          )}
        </div>

        {/* Main result */}
        <div className="px-6 py-5 flex items-center justify-between gap-4">
          <div>
            <p className="text-5xl font-black tracking-tight" style={{ color: COLORS[ai] }}>
              {ai}
            </p>
            <p className="text-xl font-semibold mt-1" style={{ color: TEXT[ai] }}>
              {LABELS[ai]}
            </p>
            <p className="text-base mt-0.5" style={{ color: TEXT[ai], opacity: 0.8 }}>
              {TIME[ai]}
            </p>
          </div>

          {/* Confidence ring */}
          <div className="flex flex-col items-center gap-1 flex-shrink-0">
            <svg width="72" height="72" viewBox="0 0 72 72">
              <circle cx="36" cy="36" r="28" fill="none" stroke={COLORS[ai] + '30'} strokeWidth="7" />
              <circle cx="36" cy="36" r="28" fill="none" stroke={COLORS[ai]} strokeWidth="7"
                strokeDasharray={`${2 * Math.PI * 28 * conf / 100} ${2 * Math.PI * 28 * (1 - conf / 100)}`}
                strokeLinecap="round" transform="rotate(-90 36 36)" />
              <text x="36" y="40" textAnchor="middle" fontSize="15" fontWeight="800" fill={COLORS[ai]}>
                {conf}%
              </text>
            </svg>
            <span className="text-xs font-medium" style={{ color: TEXT[ai] }}>Confidence</span>
          </div>
        </div>
      </div>

      {/* ── Nurse vs AI comparison ────────────────────────────────── */}
      <div className={`rounded-2xl p-4 border-2 flex items-center gap-4 ${
        agree ? 'bg-green-50 border-green-300' : 'bg-amber-50 border-amber-300'
      }`}>
        <div className="text-2xl">{agree ? '✅' : '⚠️'}</div>
        <div className="flex-1">
          <p className={`text-base font-bold ${agree ? 'text-green-800' : 'text-amber-800'}`}>
            {agree ? 'Nurse and AI agree' : 'Discrepancy — flagged for review'}
          </p>
          <div className="flex items-center gap-3 mt-1 text-sm">
            <span className="text-gray-600">
              Nurse: <strong style={{ color: COLORS[nurse] }}>{nurse}</strong>
            </span>
            <span className="text-gray-400">→</span>
            <span className="text-gray-600">
              AI: <strong style={{ color: COLORS[ai] }}>{ai}</strong>
            </span>
          </div>
        </div>
        <div className="text-right text-xs text-gray-400">
          <p className="font-mono">{result.case_id}</p>
          <p>{new Date(result.timestamp).toLocaleTimeString()}</p>
        </div>
      </div>

      {/* ── GCS ──────────────────────────────────────────────────── */}
      {result.gcs_total > 0 && (
        <div className="bg-white rounded-2xl border border-gray-200 px-6 py-4 flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-gray-100 flex items-center justify-center text-xl font-black text-gray-700">
            {result.gcs_total}
          </div>
          <div>
            <p className="text-base font-semibold text-gray-800">GCS {result.gcs_total} / 15</p>
            <p className="text-sm text-gray-500">
              E{result.gcs_eye} + V{result.gcs_verbal} + M{result.gcs_motor}
            </p>
          </div>
        </div>
      )}

      {/* ── Red flags ────────────────────────────────────────────── */}
      {Array.isArray(result.red_flags) && result.red_flags.length > 0 && (
        <div className="bg-white rounded-2xl border border-red-200 p-5">
          <p className="text-base font-bold text-red-800 mb-3">🚩 Red Flags Detected</p>
          <div className="flex flex-wrap gap-2">
            {result.red_flags.map((flag, i) => (
              <span key={i} className="bg-red-100 text-red-800 text-sm font-medium px-3 py-1 rounded-full">
                {flag}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* ── AI Reasoning ─────────────────────────────────────────── */}
      {result.ai_reasoning && (
        <div className="bg-purple-50 border border-purple-200 rounded-2xl p-5">
          <p className="text-sm font-bold text-purple-700 uppercase tracking-wide mb-2">AI Analysis</p>
          <p className="text-base text-purple-900 leading-relaxed">{result.ai_reasoning}</p>
        </div>
      )}

      {/* ── Primary concern + differentials ──────────────────────── */}
      {result.primary_concern && (
        <div className="bg-white rounded-2xl border border-gray-200 p-5 grid sm:grid-cols-2 gap-5">
          <div>
            <p className="text-sm font-bold text-gray-500 uppercase tracking-wide mb-1">Primary Concern</p>
            <p className="text-base font-semibold text-gray-900">{result.primary_concern}</p>
          </div>
          {result.differentials?.length > 0 && (
            <div>
              <p className="text-sm font-bold text-gray-500 uppercase tracking-wide mb-1">Differentials</p>
              <ul className="space-y-0.5">
                {result.differentials.map((d, i) => (
                  <li key={i} className="text-base text-gray-700 flex items-start gap-1.5">
                    <span className="text-gray-400 mt-0.5">·</span> {d}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* ── Recommendations ──────────────────────────────────────── */}
      {result.recommendations?.length > 0 && (
        <div className="bg-blue-50 border border-blue-200 rounded-2xl p-5">
          <p className="text-sm font-bold text-blue-700 uppercase tracking-wide mb-2">
            Recommended Actions
          </p>
          <ul className="space-y-1.5">
            {result.recommendations.map((r, i) => (
              <li key={i} className="flex items-start gap-2 text-base text-blue-900">
                <span className="text-blue-400 font-bold mt-0.5">→</span> {r}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* ── Escalation note ──────────────────────────────────────── */}
      {result.escalation_note && (
        <div className="bg-amber-50 border border-amber-200 rounded-2xl p-5">
          <p className="text-sm font-bold text-amber-700 uppercase tracking-wide mb-1">Escalation Note</p>
          <p className="text-base text-amber-900 leading-relaxed">{result.escalation_note}</p>
        </div>
      )}

      {/* Disclaimer */}
      <p className="text-center text-sm text-gray-400 pb-2">
        AI is a decision-support tool only. Final triage decision rests with the attending clinician.
      </p>
    </div>
  )
}

export default ResultCard
