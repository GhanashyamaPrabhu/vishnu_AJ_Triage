import { useEffect, useState } from 'react'
import { calculateGCS, getGCSOptions } from '../utils/gcsCalculator'

const INTERP_STYLE = {
  Normal:   { bg: '#f0fdf4', border: '#16a34a', text: '#14532d', badge: 'bg-green-100 text-green-800'  },
  Minor:    { bg: '#eff6ff', border: '#2563eb', text: '#1e3a8a', badge: 'bg-blue-100 text-blue-800'    },
  Moderate: { bg: '#fff7ed', border: '#ea580c', text: '#7c2d12', badge: 'bg-orange-100 text-orange-800' },
  Severe:   { bg: '#fef2f2', border: '#dc2626', text: '#7f1d1d', badge: 'bg-red-100 text-red-800'      },
  Critical: { bg: '#fef2f2', border: '#991b1b', text: '#450a0a', badge: 'bg-red-200 text-red-900'      },
}

const COLS = [
  { key: 'eye',    label: 'Eye Opening',    code: 'E' },
  { key: 'verbal', label: 'Verbal Response', code: 'V' },
  { key: 'motor',  label: 'Motor Response',  code: 'M' },
]

export default function GCSCalculator({ gcsData, onChange, ageMonths }) {
  const [result, setResult] = useState(null)

  useEffect(() => {
    const { eye, verbal, motor } = gcsData
    if (eye && verbal && motor && ageMonths != null) {
      try   { setResult(calculateGCS(eye, verbal, motor, ageMonths)) }
      catch { setResult(null) }
    } else { setResult(null) }
  }, [gcsData, ageMonths])

  const set   = (key, val) => onChange({ ...gcsData, [key]: val })
  const total = (gcsData.eye || 0) + (gcsData.verbal || 0) + (gcsData.motor || 0)
  const interp = result?.interpretation
  const style  = interp ? INTERP_STYLE[interp] : null
  const isPediatric = ageMonths != null && ageMonths < 24

  return (
    <div className="bg-white rounded-3xl shadow-xl overflow-hidden border-2 border-gray-100">
      {/* Section header */}
      <div className="px-8 py-6 flex items-center gap-4 border-b-2 border-gray-100"
        style={{ borderLeft: '10px solid #7c3aed' }}>
        <div className="w-14 h-14 rounded-2xl flex items-center justify-center text-white font-black text-2xl flex-shrink-0 shadow-md"
          style={{ backgroundColor: '#7c3aed' }}>
          3
        </div>
        <div className="flex-1">
          <h2 className="text-3xl font-extrabold text-gray-900">Glasgow Coma Scale (GCS)</h2>
          {isPediatric && (
            <span className="text-sm text-purple-700 font-semibold">Pediatric scale — age &lt; 24 months</span>
          )}
        </div>

        {/* Live GCS total */}
        <div className="flex items-center gap-3">
          <div className="text-right">
            <div
              className="text-4xl font-black"
              style={{ color: style?.border ?? '#9ca3af' }}>
              {total > 0 ? `${total}` : '—'}<span className="text-2xl text-gray-400">/15</span>
            </div>
            {interp && (
              <span className={`text-sm font-bold px-2 py-0.5 rounded-full ${style?.badge}`}>
                {interp}
              </span>
            )}
          </div>
        </div>
        <span className="text-3xl ml-2">🧠</span>
      </div>

      {ageMonths == null && (
        <div className="mx-8 mt-6 p-4 bg-amber-50 border-2 border-amber-200 rounded-2xl text-base text-amber-700 font-medium">
          ℹ Enter patient age to load the correct GCS scale (standard or pediatric)
        </div>
      )}

      {/* E / V / M columns */}
      {ageMonths != null && (
        <div className="grid grid-cols-1 lg:grid-cols-3 divide-y lg:divide-y-0 lg:divide-x divide-gray-100">
          {COLS.map(({ key, label, code }) => {
            const options  = getGCSOptions(key, ageMonths)
            const selected = gcsData[key]

            return (
              <div key={key} className="p-7">
                {/* Column header */}
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <span className="text-xl font-extrabold text-gray-900">{label}</span>
                    <span className="text-base text-gray-400 ml-2 font-semibold">({code})</span>
                  </div>
                  {selected && (
                    <span className="w-10 h-10 rounded-xl bg-purple-600 text-white flex items-center justify-center text-xl font-black shadow">
                      {selected}
                    </span>
                  )}
                </div>

                {/* Options */}
                <div className="space-y-2">
                  {options.map(opt => {
                    const isSel = selected === opt.value
                    return (
                      <button
                        key={opt.value}
                        type="button"
                        onClick={() => set(key, opt.value)}
                        className="w-full flex items-center gap-4 px-5 py-4 rounded-2xl text-left transition-all duration-100 active:scale-98"
                        style={{
                          border:          `3px solid ${isSel ? '#7c3aed' : '#e5e7eb'}`,
                          backgroundColor: isSel ? '#f5f3ff' : '#fff',
                          boxShadow:       isSel ? '0 2px 8px #7c3aed30' : '0 1px 3px #0000000d',
                        }}>
                        <span
                          className="w-11 h-11 rounded-xl flex items-center justify-center text-xl font-black flex-shrink-0"
                          style={{
                            backgroundColor: isSel ? '#7c3aed' : '#f3f4f6',
                            color:           isSel ? '#fff'    : '#6b7280',
                          }}>
                          {opt.value}
                        </span>
                        <span className={`text-base leading-snug ${isSel ? 'text-purple-900 font-bold' : 'text-gray-700 font-medium'}`}>
                          {opt.label}
                        </span>
                      </button>
                    )
                  })}
                </div>
              </div>
            )
          })}
        </div>
      )}

      {/* Summary when all 3 scored */}
      {result && style && (
        <div className="mx-8 mb-8 mt-2">
          <div className="rounded-2xl p-5 border-2" style={{ backgroundColor: style.bg, borderColor: style.border }}>
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="text-lg font-extrabold" style={{ color: style.text }}>
                  GCS {total}/15 — {result.interpretation}
                </p>
                <p className="text-base mt-1" style={{ color: style.text, opacity: 0.85 }}>
                  {result.clinicalSignificance}
                </p>
              </div>
              {result.minimumTriageCategory && (
                <span className="flex-shrink-0 text-sm font-black px-3 py-2 rounded-xl bg-red-600 text-white shadow">
                  Min triage: {result.minimumTriageCategory}
                </span>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
