import { useState, useEffect } from 'react'
import { fahrenheitToCelsius } from '../utils/tempConverter'
import { getNormalRanges, checkVitalStatus } from '../utils/normalRanges'

const VITALS = [
  { key: 'heartRate',        label: 'Heart Rate',  unit: 'bpm',  icon: '❤️',  min: 30,  max: 300, step: 1   },
  { key: 'respiratoryRate',  label: 'Resp. Rate',  unit: '/min', icon: '🫁',  min: 5,   max: 100, step: 1   },
  { key: 'temperature',      label: 'Temperature', unit: '°F',   icon: '🌡️', min: 86,  max: 115, step: 0.1 },
  { key: 'oxygenSaturation', label: 'SpO₂',        unit: '%',    icon: '💨',  min: 50,  max: 100, step: 1   },
]

const STATUS = {
  normal:   { border: '#16a34a', bg: '#f0fdf4', chip: 'bg-green-100 text-green-700',  label: 'Normal'   },
  warning:  { border: '#ea580c', bg: '#fff7ed', chip: 'bg-orange-100 text-orange-700', label: 'High'     },
  critical: { border: '#dc2626', bg: '#fef2f2', chip: 'bg-red-100 text-red-700',      label: 'Critical' },
  empty:    { border: '#e5e7eb', bg: '#ffffff', chip: '',                              label: ''         },
}

function getStatus(key, value, ageMonths) {
  if (!value || !ageMonths) return 'empty'
  const s = checkVitalStatus(key, value, ageMonths)
  if (!s) return 'empty'
  if (s.color === 'red')    return 'critical'
  if (s.color === 'orange') return 'warning'
  return 'normal'
}

export default function VitalsInput({ vitals, onChange, ageMonths }) {
  const [ranges, setRanges] = useState(null)

  useEffect(() => {
    setRanges(ageMonths ? getNormalRanges(ageMonths) : null)
  }, [ageMonths])

  const set = (key, raw) => {
    const v = raw === '' ? null : parseFloat(raw)
    onChange({ ...vitals, [key]: isNaN(v) ? null : v })
  }

  const hasCritical = ageMonths && VITALS.some(({ key }) => getStatus(key, vitals[key], ageMonths) === 'critical')

  return (
    <div className="bg-white rounded-3xl shadow-xl overflow-hidden border-2 border-gray-100">
      {/* Section header */}
      <div className="px-8 py-6 flex items-center gap-4 border-b-2 border-gray-100"
        style={{ borderLeft: '10px solid #059669' }}>
        <div className="w-14 h-14 rounded-2xl flex items-center justify-center text-white font-black text-2xl flex-shrink-0 shadow-md"
          style={{ backgroundColor: '#059669' }}>
          2
        </div>
        <div className="flex-1">
          <h2 className="text-3xl font-extrabold text-gray-900">Vital Signs</h2>
        </div>
        {ranges && (
          <span className="text-base text-gray-500 bg-gray-100 rounded-full px-4 py-1.5 font-medium">
            {ranges.ageGroup}
          </span>
        )}
        <span className="text-3xl ml-2">🩺</span>
      </div>

      {!ageMonths && (
        <div className="mx-8 mt-6 p-4 bg-amber-50 border-2 border-amber-200 rounded-2xl text-base text-amber-700 font-medium">
          ℹ Enter patient age in Section 1 to see age-appropriate normal ranges
        </div>
      )}

      {/* Vital boxes */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-6 p-8">
        {VITALS.map(({ key, label, unit, icon, min, max, step }) => {
          const val    = vitals[key]
          const status = getStatus(key, val, ageMonths)
          const style  = STATUS[status]
          const range  = ranges?.[key]

          return (
            <div key={key}
              className="rounded-2xl p-7 transition-all duration-200 flex flex-col gap-4 shadow-md"
              style={{ border: `4px solid ${style.border}`, backgroundColor: style.bg }}>

              {/* Label + status */}
              <div className="flex items-center justify-between">
                <span className="text-base font-bold text-gray-600">{icon} {label}</span>
                {val && status !== 'empty' && (
                  <span className={`text-sm font-bold px-2.5 py-0.5 rounded-full ${style.chip}`}>
                    {style.label}
                  </span>
                )}
              </div>

              {/* Big number input */}
              <div className="flex items-end gap-2">
                <input
                  type="number"
                  value={val ?? ''}
                  onChange={e => set(key, e.target.value)}
                  min={min} max={max} step={step}
                  placeholder="—"
                  className="flex-1 bg-transparent text-6xl font-black text-gray-900 placeholder-gray-200 focus:outline-none border-none p-0 w-0 leading-none"
                  style={{ MozAppearance: 'textfield' }}
                />
                <span className="text-xl font-semibold text-gray-400 pb-1">{unit}</span>
              </div>

              {/* Normal range */}
              {range && (
                <p className="text-sm text-gray-400 font-medium">
                  Normal: {range.min}–{range.max} {unit}
                </p>
              )}

              {/* Celsius conversion for temperature */}
              {key === 'temperature' && val && (
                <p className="text-sm text-gray-500 font-medium">
                  = {fahrenheitToCelsius(val).toFixed(1)} °C
                </p>
              )}
            </div>
          )
        })}
      </div>

      {/* Critical alert */}
      {hasCritical && (
        <div className="mx-8 mb-8 p-4 bg-red-50 border-2 border-red-200 rounded-2xl flex items-center gap-3 text-base text-red-700 font-semibold">
          <span className="text-2xl">🛑</span>
          Critical vital sign detected — consider immediate escalation to RED
        </div>
      )}
    </div>
  )
}
