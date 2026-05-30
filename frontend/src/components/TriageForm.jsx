import { useState } from 'react'
import VitalsInput from './VitalsInput'
import GCSCalculator from './GCSCalculator'
import ResultCard from './ResultCard'

const BACKEND_URL = 'http://localhost:8000'

const TRIAGE_OPTIONS = [
  { cat: 'RED',    bg: '#dc2626', glow: '#fca5a5', sub: 'Immediate — Now'      },
  { cat: 'ORANGE', bg: '#ea580c', glow: '#fdba74', sub: 'Very Urgent — 10 min' },
  { cat: 'YELLOW', bg: '#ca8a04', glow: '#fde047', sub: 'Urgent — 1 hour'      },
  { cat: 'GREEN',  bg: '#16a34a', glow: '#86efac', sub: 'Routine'              },
]

// ── Section card with colored accent bar ────────────────────────────────────
const Section = ({ n, title, accent, icon, children }) => (
  <div className="bg-white rounded-3xl shadow-xl overflow-hidden border-2 border-gray-100">
    {/* Accent bar + header */}
    <div className="px-8 py-6 flex items-center gap-4 border-b-2 border-gray-100"
      style={{ borderLeft: `10px solid ${accent}` }}>
      <div className="w-14 h-14 rounded-2xl flex items-center justify-center text-white font-black text-2xl flex-shrink-0 shadow-md"
        style={{ backgroundColor: accent }}>
        {n}
      </div>
      <div>
        <h2 className="text-3xl font-extrabold text-gray-900 leading-tight">{title}</h2>
      </div>
      <span className="ml-auto text-4xl">{icon}</span>
    </div>
    <div className="p-10">{children}</div>
  </div>
)

const inputCls = [
  'w-full px-5 py-5 text-xl rounded-2xl',
  'border-[3px] border-gray-200 bg-white',
  'focus:border-blue-500 focus:outline-none focus:ring-0',
  'transition-colors placeholder-gray-300 font-medium',
].join(' ')


export default function TriageForm({ user }) {
  const [form, setForm] = useState({
    patientName: '',
    patientId:   '',
    age: '', ageUnit: 'months',
    weight: '', weightUnit: 'kg',
    vitals:    { heartRate: null, respiratoryRate: null, temperature: null,
                 systolicBP: null, diastolicBP: null, oxygenSaturation: null },
    gcs:       { eye: null, verbal: null, motor: null },
    narrative: '',
    nurseCategory: null,
  })
  const [result,     setResult]     = useState(null)
  const [submitting, setSubmitting] = useState(false)
  const [error,      setError]      = useState('')

  const set = (k, v) => setForm(f => ({ ...f, [k]: v }))

  // Convert entered age to months for backend and GCS
  const ageMonths = (() => {
    const n = parseFloat(form.age)
    if (!n) return null
    if (form.ageUnit === 'days')   return n / 30.44
    if (form.ageUnit === 'years')  return n * 12
    return n                       // months
  })()

  const ageLabel = ageMonths
    ? ageMonths < 1
      ? `${Math.round(ageMonths * 30.44)} days`
      : ageMonths < 24
        ? `${ageMonths.toFixed(1)} months`
        : `${(ageMonths / 12).toFixed(1)} years`
    : null

  const gcsTotal  = (form.gcs.eye || 0) + (form.gcs.verbal || 0) + (form.gcs.motor || 0)
  const vitalsOk  = form.vitals.heartRate && form.vitals.respiratoryRate &&
                    form.vitals.temperature && form.vitals.oxygenSaturation
  const canSubmit = (form.patientName || form.patientId) && form.age &&
                    form.narrative.trim() && form.nurseCategory && vitalsOk

  // What's still missing
  const missing = [
    !(form.patientName || form.patientId) && 'Patient name/ID',
    !form.age  && 'Age',
    !vitalsOk  && 'HR, RR, Temperature & SpO₂',
    !form.narrative.trim() && 'Clinical narrative',
    !form.nurseCategory    && 'Your triage category',
  ].filter(Boolean)

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!canSubmit) return
    setSubmitting(true)
    setError('')
    try {
      const weightKg = form.weight
        ? form.weightUnit === 'g'
          ? parseFloat(form.weight) / 1000
          : parseFloat(form.weight)
        : null

      const res = await fetch(`${BACKEND_URL}/triage`, {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          patient_id:            form.patientId || form.patientName,
          age_months:            ageMonths,
          weight_kg:             weightKg,
          vitals:                form.vitals,
          gcs:                   form.gcs,
          clinical_narrative:    form.narrative,
          nurse_triage_category: form.nurseCategory,
          nurse_id:              user?.id ?? 1,
        }),
      })
      if (!res.ok) { const d = await res.json(); setError(d.detail || 'Submission failed'); return }
      setResult(await res.json())
    } catch {
      setError('Network error — is the backend running?')
    } finally {
      setSubmitting(false)
    }
  }

  const reset = () => {
    setForm({
      patientName: '', patientId: '',
      age: '', ageUnit: 'months', weight: '', weightUnit: 'kg',
      vitals: { heartRate: null, respiratoryRate: null, temperature: null,
                systolicBP: null, diastolicBP: null, oxygenSaturation: null },
      gcs: { eye: null, verbal: null, motor: null },
      narrative: '', nurseCategory: null,
    })
    setResult(null)
    setError('')
  }

  if (result) return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 py-10">
      <ResultCard result={result} />
      <div className="mt-8 text-center">
        <button onClick={reset}
          className="px-10 py-4 rounded-2xl bg-blue-600 text-white font-bold text-lg hover:bg-blue-700 active:scale-95 transition-all shadow-md">
          ← New Triage Entry
        </button>
      </div>
    </div>
  )

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 py-10">

      {/* ── Page header ──────────────────────────────────────────── */}
      <div className="mb-10">
        <h1 className="text-4xl font-black text-gray-900 tracking-tight">New Triage Entry</h1>
        <p className="text-lg text-gray-500 mt-2">
          Complete all sections, then submit for AI-assisted triage analysis
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">

        {/* ══ SECTION 1 — Patient Details ════════════════════════ */}
        <Section n="1" title="Patient Details" accent="#2563eb" icon="🪪">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">

            {/* Name */}
            <div className="md:col-span-1">
              <label className="block text-lg font-bold text-gray-700 mb-2">Patient Name</label>
              <input
                type="text"
                value={form.patientName}
                onChange={e => set('patientName', e.target.value)}
                className={inputCls}
                placeholder="Full name"
              />
              <p className="text-sm text-gray-400 mt-1.5">For local reference — name is not sent to AI</p>
            </div>

            {/* Age */}
            <div>
              <label className="block text-lg font-bold text-gray-700 mb-2">Age <span className="text-red-500">*</span></label>
              <div className="flex gap-2">
                <input
                  type="number"
                  value={form.age}
                  onChange={e => set('age', e.target.value)}
                  min="0" step="1"
                  className={inputCls + ' flex-1'}
                  placeholder="0"
                  required
                />
                <select
                  value={form.ageUnit}
                  onChange={e => set('ageUnit', e.target.value)}
                  className="px-4 py-4 text-lg font-semibold rounded-2xl border-2 border-gray-200 bg-white focus:border-blue-500 focus:outline-none cursor-pointer">
                  <option value="days">days</option>
                  <option value="months">months</option>
                  <option value="years">years</option>
                </select>
              </div>
              {ageLabel && (
                <p className="text-sm text-blue-600 font-medium mt-1.5">≈ {ageLabel}</p>
              )}
            </div>

            {/* Weight */}
            <div>
              <label className="block text-lg font-bold text-gray-700 mb-2">Weight</label>
              <div className="flex gap-2">
                <input
                  type="number"
                  value={form.weight}
                  onChange={e => set('weight', e.target.value)}
                  min="0" step="0.1"
                  className={inputCls + ' flex-1'}
                  placeholder="0"
                />
                <select
                  value={form.weightUnit}
                  onChange={e => set('weightUnit', e.target.value)}
                  className="px-4 py-4 text-lg font-semibold rounded-2xl border-2 border-gray-200 bg-white focus:border-blue-500 focus:outline-none cursor-pointer">
                  <option value="kg">kg</option>
                  <option value="g">g</option>
                </select>
              </div>
            </div>
          </div>
        </Section>

        {/* ══ SECTION 2 — Vital Signs ═════════════════════════════ */}
        <VitalsInput
          vitals={form.vitals}
          onChange={v => set('vitals', v)}
          ageMonths={ageMonths}
        />

        {/* ══ SECTION 3 — GCS ════════════════════════════════════ */}
        <GCSCalculator
          gcsData={form.gcs}
          onChange={g => set('gcs', g)}
          ageMonths={ageMonths}
        />

        {/* ══ SECTION 4 — Clinical Narrative ═════════════════════ */}
        <Section n="4" title="Clinical Narrative" accent="#64748b" icon="📝">
          <textarea
            value={form.narrative}
            onChange={e => set('narrative', e.target.value)}
            rows={6}
            required
            placeholder='Chief complaint and brief history — e.g. "3yo girl, fever since yesterday, breathing fast, grunting while sleeping, not feeding"'
            className="w-full px-5 py-4 text-xl leading-relaxed rounded-2xl border-2 border-gray-200 focus:border-blue-500 focus:outline-none resize-none transition-colors placeholder-gray-300"
          />
          <p className="text-base text-gray-400 mt-3">
            Include presenting complaint, duration, and any red-flag phrases (e.g. "weak cry", "mottled skin", "not interacting")
          </p>
        </Section>

        {/* ══ SECTION 5 — Nurse SATS Assessment ══════════════════ */}
        <Section n="5" title="Your SATS Assessment" accent="#ea580c" icon="🩺">
          <p className="text-lg text-gray-500 mb-6">
            Select your triage category — this is recorded <strong>before</strong> the AI result is revealed
          </p>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            {TRIAGE_OPTIONS.map(({ cat, bg, glow, sub }) => {
              const sel = form.nurseCategory === cat
              return (
                <button
                  key={cat}
                  type="button"
                  onClick={() => set('nurseCategory', cat)}
                  className="relative flex flex-col items-center justify-center py-7 px-4 rounded-2xl font-black transition-all duration-150 active:scale-95"
                  style={{
                    backgroundColor: sel ? bg : bg + '18',
                    border:    `3px solid ${sel ? bg : bg + '60'}`,
                    color:     sel ? '#fff' : bg,
                    boxShadow: sel ? `0 0 0 5px ${glow}, 0 4px 20px ${bg}40` : 'none',
                    transform: sel ? 'scale(1.04)' : 'scale(1)',
                  }}>
                  {sel && <span className="absolute top-3 right-3 text-lg">✓</span>}
                  <span className="text-3xl font-black tracking-wide">{cat}</span>
                  <span className="text-sm mt-1.5 font-semibold opacity-90 text-center leading-tight">{sub}</span>
                </button>
              )
            })}
          </div>
        </Section>

        {/* Error */}
        {error && (
          <div className="px-6 py-4 rounded-2xl bg-red-50 border-2 border-red-200 text-lg text-red-700 flex items-center gap-3">
            <span className="text-2xl">⚠️</span> {error}
          </div>
        )}

        {/* ══ SUBMIT ══════════════════════════════════════════════ */}
        <div className="pb-10">
          {/* Missing fields checklist */}
          {!canSubmit && missing.length > 0 && (
            <div className="flex flex-wrap gap-2 justify-center mb-4">
              {missing.map(m => (
                <span key={m} className="text-sm bg-gray-100 text-gray-500 px-3 py-1 rounded-full">
                  ○ {m}
                </span>
              ))}
            </div>
          )}

          <button
            type="submit"
            disabled={!canSubmit || submitting}
            className="w-full py-6 rounded-3xl text-2xl font-black text-white shadow-lg transition-all duration-200 disabled:opacity-40 disabled:cursor-not-allowed active:scale-99"
            style={{
              background: canSubmit
                ? 'linear-gradient(135deg, #1e40af 0%, #2563eb 50%, #3b82f6 100%)'
                : '#d1d5db',
            }}>
            {submitting ? (
              <span className="flex items-center justify-center gap-4">
                <span className="w-7 h-7 border-4 border-white border-t-transparent rounded-full animate-spin" />
                Analysing with AI…
              </span>
            ) : (
              <span className="flex items-center justify-center gap-3">
                🤖 Submit for AI Analysis
                {gcsTotal > 0 && (
                  <span className="text-lg font-bold opacity-80 bg-white/20 px-3 py-1 rounded-full">
                    GCS {gcsTotal}/15
                  </span>
                )}
              </span>
            )}
          </button>
        </div>

      </form>
    </div>
  )
}
