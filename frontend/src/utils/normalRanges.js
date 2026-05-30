// Normal ranges for pediatric vital signs by age

/**
 * Get normal vital sign ranges based on age in months
 * @param {number} ageMonths - Age in months
 * @returns {object} Normal ranges for vital signs
 */
export const getNormalRanges = (ageMonths) => {
  // Convert months to years for easier calculation
  const ageYears = ageMonths / 12

  // Neonate (0-1 month)
  if (ageMonths <= 1) {
    return {
      heartRate: { min: 100, max: 160, unit: 'bpm' },
      respiratoryRate: { min: 30, max: 60, unit: '/min' },
      systolicBP: { min: 60, max: 90, unit: 'mmHg' },
      diastolicBP: { min: 20, max: 60, unit: 'mmHg' },
      temperature: { min: 97.8, max: 99.1, unit: '°F' },
      oxygenSaturation: { min: 95, max: 100, unit: '%' },
      ageGroup: 'Neonate (0-1 month)'
    }
  }

  // Infant (1-12 months)
  if (ageMonths <= 12) {
    return {
      heartRate: { min: 100, max: 150, unit: 'bpm' },
      respiratoryRate: { min: 25, max: 50, unit: '/min' },
      systolicBP: { min: 70, max: 100, unit: 'mmHg' },
      diastolicBP: { min: 50, max: 70, unit: 'mmHg' },
      temperature: { min: 97.8, max: 99.1, unit: '°F' },
      oxygenSaturation: { min: 95, max: 100, unit: '%' },
      ageGroup: 'Infant (1-12 months)'
    }
  }

  // Toddler (1-3 years)
  if (ageYears <= 3) {
    return {
      heartRate: { min: 90, max: 130, unit: 'bpm' },
      respiratoryRate: { min: 20, max: 40, unit: '/min' },
      systolicBP: { min: 80, max: 110, unit: 'mmHg' },
      diastolicBP: { min: 50, max: 80, unit: 'mmHg' },
      temperature: { min: 97.8, max: 99.1, unit: '°F' },
      oxygenSaturation: { min: 95, max: 100, unit: '%' },
      ageGroup: 'Toddler (1-3 years)'
    }
  }

  // Preschooler (3-6 years)
  if (ageYears <= 6) {
    return {
      heartRate: { min: 80, max: 120, unit: 'bpm' },
      respiratoryRate: { min: 20, max: 30, unit: '/min' },
      systolicBP: { min: 90, max: 110, unit: 'mmHg' },
      diastolicBP: { min: 50, max: 70, unit: 'mmHg' },
      temperature: { min: 97.8, max: 99.1, unit: '°F' },
      oxygenSaturation: { min: 95, max: 100, unit: '%' },
      ageGroup: 'Preschooler (3-6 years)'
    }
  }

  // School age (6-12 years)
  if (ageYears <= 12) {
    return {
      heartRate: { min: 70, max: 110, unit: 'bpm' },
      respiratoryRate: { min: 15, max: 25, unit: '/min' },
      systolicBP: { min: 90, max: 120, unit: 'mmHg' },
      diastolicBP: { min: 60, max: 80, unit: 'mmHg' },
      temperature: { min: 97.8, max: 99.1, unit: '°F' },
      oxygenSaturation: { min: 95, max: 100, unit: '%' },
      ageGroup: 'School age (6-12 years)'
    }
  }

  // Adolescent (12-18 years)
  return {
    heartRate: { min: 60, max: 100, unit: 'bpm' },
    respiratoryRate: { min: 12, max: 20, unit: '/min' },
    systolicBP: { min: 100, max: 120, unit: 'mmHg' },
    diastolicBP: { min: 60, max: 80, unit: 'mmHg' },
    temperature: { min: 97.8, max: 99.1, unit: '°F' },
    oxygenSaturation: { min: 95, max: 100, unit: '%' },
    ageGroup: 'Adolescent (12-18 years)'
  }
}

/**
 * Check if a vital sign value is within normal range
 * @param {string} vitalType - Type of vital sign
 * @param {number} value - Vital sign value
 * @param {number} ageMonths - Age in months
 * @returns {object} Status object with isNormal, category, and description
 */
export const checkVitalStatus = (vitalType, value, ageMonths) => {
  const ranges = getNormalRanges(ageMonths)
  const range = ranges[vitalType]

  if (!range || typeof value !== 'number' || isNaN(value)) {
    return {
      isNormal: false,
      category: 'unknown',
      description: 'Unable to assess',
      color: 'gray'
    }
  }

  if (value >= range.min && value <= range.max) {
    return {
      isNormal: true,
      category: 'normal',
      description: 'Normal',
      color: 'green'
    }
  }

  if (value < range.min) {
    const severity = getSeverityBelow(vitalType, value, range)
    return {
      isNormal: false,
      category: 'low',
      description: `Low (${severity})`,
      color: severity === 'critical' ? 'red' : 'blue'
    }
  }

  const severity = getSeverityAbove(vitalType, value, range)
  return {
    isNormal: false,
    category: 'high',
    description: `High (${severity})`,
    color: severity === 'critical' ? 'red' : 'orange'
  }
}

/**
 * Get severity level when value is below normal range
 * @param {string} vitalType - Type of vital sign
 * @param {number} value - Vital sign value
 * @param {object} range - Normal range object
 * @returns {string} Severity level
 */
const getSeverityBelow = (vitalType, value, range) => {
  const percentBelow = ((range.min - value) / range.min) * 100

  switch (vitalType) {
    case 'heartRate':
      if (value < range.min * 0.7) return 'critical' // >30% below
      if (value < range.min * 0.85) return 'moderate' // 15-30% below
      return 'mild'

    case 'respiratoryRate':
      if (value < range.min * 0.6) return 'critical' // >40% below
      if (value < range.min * 0.8) return 'moderate' // 20-40% below
      return 'mild'

    case 'systolicBP':
      if (value < range.min * 0.8) return 'critical' // >20% below
      if (value < range.min * 0.9) return 'moderate' // 10-20% below
      return 'mild'

    case 'oxygenSaturation':
      if (value < 90) return 'critical'
      if (value < 93) return 'moderate'
      return 'mild'

    default:
      if (percentBelow > 25) return 'critical'
      if (percentBelow > 15) return 'moderate'
      return 'mild'
  }
}

/**
 * Get severity level when value is above normal range
 * @param {string} vitalType - Type of vital sign
 * @param {number} value - Vital sign value
 * @param {object} range - Normal range object
 * @returns {string} Severity level
 */
const getSeverityAbove = (vitalType, value, range) => {
  const percentAbove = ((value - range.max) / range.max) * 100

  switch (vitalType) {
    case 'heartRate':
      if (value > range.max * 1.5) return 'critical' // >50% above
      if (value > range.max * 1.25) return 'moderate' // 25-50% above
      return 'mild'

    case 'respiratoryRate':
      if (value > range.max * 1.5) return 'critical' // >50% above
      if (value > range.max * 1.3) return 'moderate' // 30-50% above
      return 'mild'

    case 'systolicBP':
      if (value > range.max * 1.3) return 'critical' // >30% above
      if (value > range.max * 1.15) return 'moderate' // 15-30% above
      return 'mild'

    case 'temperature':
      if (value > 105.8) return 'critical' // Hyperpyrexia
      if (value > 103.0) return 'moderate' // High fever
      return 'mild'

    default:
      if (percentAbove > 30) return 'critical'
      if (percentAbove > 20) return 'moderate'
      return 'mild'
  }
}

/**
 * Get CSS class for vital sign status
 * @param {string} vitalType - Type of vital sign
 * @param {number} value - Vital sign value
 * @param {number} ageMonths - Age in months
 * @returns {string} CSS class name
 */
export const getVitalStatusClass = (vitalType, value, ageMonths) => {
  const status = checkVitalStatus(vitalType, value, ageMonths)
  
  switch (status.color) {
    case 'green':
      return 'text-green-600 bg-green-50 border-green-200'
    case 'blue':
      return 'text-blue-600 bg-blue-50 border-blue-200'
    case 'orange':
      return 'text-orange-600 bg-orange-50 border-orange-200'
    case 'red':
      return 'text-red-600 bg-red-50 border-red-200'
    default:
      return 'text-gray-600 bg-gray-50 border-gray-200'
  }
}

/**
 * Get badge class for vital sign status
 * @param {string} vitalType - Type of vital sign
 * @param {number} value - Vital sign value
 * @param {number} ageMonths - Age in months
 * @returns {string} Badge CSS class
 */
export const getVitalBadgeClass = (vitalType, value, ageMonths) => {
  const status = checkVitalStatus(vitalType, value, ageMonths)
  
  switch (status.color) {
    case 'green':
      return 'badge-green'
    case 'blue':
      return 'badge-blue'
    case 'orange':
      return 'badge-orange'
    case 'red':
      return 'badge-red'
    default:
      return 'badge-gray'
  }
}

/**
 * Get all vital signs status summary
 * @param {object} vitals - Object with vital sign values
 * @param {number} ageMonths - Age in months
 * @returns {object} Summary of all vital signs
 */
export const getVitalsStatusSummary = (vitals, ageMonths) => {
  const vitalTypes = ['heartRate', 'respiratoryRate', 'systolicBP', 'diastolicBP', 'temperature', 'oxygenSaturation']
  const statuses = {}
  let abnormalCount = 0
  let criticalCount = 0

  vitalTypes.forEach(vitalType => {
    if (vitals[vitalType] !== undefined && vitals[vitalType] !== null) {
      const status = checkVitalStatus(vitalType, vitals[vitalType], ageMonths)
      statuses[vitalType] = status
      
      if (!status.isNormal) {
        abnormalCount++
        if (status.color === 'red') {
          criticalCount++
        }
      }
    }
  })

  return {
    statuses,
    abnormalCount,
    criticalCount,
    overallStatus: criticalCount > 0 ? 'critical' : abnormalCount > 0 ? 'abnormal' : 'normal',
    ranges: getNormalRanges(ageMonths)
  }
}

/**
 * Format vital sign range for display
 * @param {object} range - Range object with min, max, unit
 * @returns {string} Formatted range string
 */
export const formatVitalRange = (range) => {
  if (!range) return 'N/A'
  return `${range.min}-${range.max} ${range.unit}`
}

/**
 * Get triage implications based on vital signs
 * @param {object} vitals - Object with vital sign values
 * @param {number} ageMonths - Age in months
 * @returns {object} Triage implications
 */
export const getTriageImplications = (vitals, ageMonths) => {
  const summary = getVitalsStatusSummary(vitals, ageMonths)
  
  if (summary.criticalCount > 0) {
    return {
      minimumCategory: 'RED',
      urgency: 'immediate',
      description: 'Critical vital signs detected - immediate intervention required'
    }
  }
  
  if (summary.abnormalCount >= 3) {
    return {
      minimumCategory: 'ORANGE',
      urgency: 'urgent',
      description: 'Multiple abnormal vital signs - urgent medical attention required'
    }
  }
  
  if (summary.abnormalCount >= 1) {
    return {
      minimumCategory: 'YELLOW',
      urgency: 'semi-urgent',
      description: 'Abnormal vital signs detected - medical evaluation needed'
    }
  }
  
  return {
    minimumCategory: null,
    urgency: 'routine',
    description: 'Vital signs within normal limits'
  }
}