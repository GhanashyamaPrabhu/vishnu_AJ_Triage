// GCS Calculator utility functions
export const GCS_SCALES = {
  STANDARD: 'standard',
  PEDIATRIC: 'pediatric'
}

export const GCS_INTERPRETATIONS = {
  NORMAL: 'Normal',
  MINOR: 'Minor',
  MODERATE: 'Moderate',
  SEVERE: 'Severe',
  CRITICAL: 'Critical'
}

// Standard GCS descriptions (age ≥ 24 months)
export const STANDARD_EYE_RESPONSES = {
  4: 'Spontaneous',
  3: 'To Voice',
  2: 'To Pain',
  1: 'None'
}

export const STANDARD_VERBAL_RESPONSES = {
  5: 'Oriented',
  4: 'Confused',
  3: 'Inappropriate Words',
  2: 'Incomprehensible Sounds',
  1: 'None'
}

// Pediatric GCS verbal responses (age < 24 months)
export const PEDIATRIC_VERBAL_RESPONSES = {
  5: 'Coos/Babbles normally',
  4: 'Irritable/Crying',
  3: 'Cries to pain only',
  2: 'Moans to pain',
  1: 'None'
}

// Motor responses (same for both scales)
export const MOTOR_RESPONSES = {
  6: 'Obeys Commands',
  5: 'Localizes Pain',
  4: 'Withdraws from Pain',
  3: 'Abnormal Flexion (Decorticate)',
  2: 'Extension (Decerebrate)',
  1: 'None'
}

/**
 * Calculate GCS total and interpretation
 * @param {number} eye - Eye opening response (1-4)
 * @param {number} verbal - Verbal response (1-5)
 * @param {number} motor - Motor response (1-6)
 * @param {number} ageMonths - Patient age in months
 * @returns {object} GCS calculation result
 */
export const calculateGCS = (eye, verbal, motor, ageMonths) => {
  // Validate inputs
  if (!Number.isInteger(eye) || eye < 1 || eye > 4) {
    throw new Error('Eye score must be an integer between 1 and 4')
  }
  if (!Number.isInteger(verbal) || verbal < 1 || verbal > 5) {
    throw new Error('Verbal score must be an integer between 1 and 5')
  }
  if (!Number.isInteger(motor) || motor < 1 || motor > 6) {
    throw new Error('Motor score must be an integer between 1 and 6')
  }
  if (typeof ageMonths !== 'number' || ageMonths < 0) {
    throw new Error('Age must be a positive number')
  }

  const total = eye + verbal + motor
  const scale = ageMonths < 24 ? GCS_SCALES.PEDIATRIC : GCS_SCALES.STANDARD
  const interpretation = interpretGCSTotal(total)
  
  return {
    eye,
    verbal,
    motor,
    total,
    scale,
    interpretation,
    description: generateGCSDescription(eye, verbal, motor, scale),
    clinicalSignificance: getClinicalSignificance(total, interpretation, ageMonths),
    minimumTriageCategory: getMinimumTriageCategory(total),
    normalRanges: getNormalRangesByAge(ageMonths)
  }
}

/**
 * Interpret GCS total score
 * @param {number} total - GCS total score
 * @returns {string} Interpretation
 */
export const interpretGCSTotal = (total) => {
  if (total === 15) return GCS_INTERPRETATIONS.NORMAL
  if (total >= 13) return GCS_INTERPRETATIONS.MINOR
  if (total >= 9) return GCS_INTERPRETATIONS.MODERATE
  if (total > 3) return GCS_INTERPRETATIONS.SEVERE
  return GCS_INTERPRETATIONS.CRITICAL
}

/**
 * Generate human-readable GCS description
 * @param {number} eye - Eye score
 * @param {number} verbal - Verbal score
 * @param {number} motor - Motor score
 * @param {string} scale - GCS scale used
 * @returns {string} Description
 */
export const generateGCSDescription = (eye, verbal, motor, scale) => {
  const eyeDesc = STANDARD_EYE_RESPONSES[eye]
  const motorDesc = MOTOR_RESPONSES[motor]
  
  const verbalResponses = scale === GCS_SCALES.PEDIATRIC 
    ? PEDIATRIC_VERBAL_RESPONSES 
    : STANDARD_VERBAL_RESPONSES
  const verbalDesc = verbalResponses[verbal]
  
  const scaleNote = scale === GCS_SCALES.PEDIATRIC ? ' (Pediatric GCS)' : ''
  
  return `E${eye} (${eyeDesc}) + V${verbal} (${verbalDesc}) + M${motor} (${motorDesc})${scaleNote}`
}

/**
 * Get clinical significance and triage implications
 * @param {number} total - GCS total
 * @param {string} interpretation - GCS interpretation
 * @param {number} ageMonths - Age in months
 * @returns {string} Clinical significance
 */
export const getClinicalSignificance = (total, interpretation, ageMonths) => {
  const ageContext = ageMonths < 24 
    ? ' In infants, even minor GCS changes are significant.' 
    : ''

  switch (interpretation) {
    case GCS_INTERPRETATIONS.NORMAL:
      return `Normal consciousness level.${ageContext}`
    
    case GCS_INTERPRETATIONS.MINOR:
      return `Mild alteration in consciousness. Monitor closely for deterioration.${ageContext}`
    
    case GCS_INTERPRETATIONS.MODERATE:
      return `Moderate brain injury. Requires urgent medical attention and frequent neurological assessment. Minimum ORANGE triage category.${ageContext}`
    
    case GCS_INTERPRETATIONS.SEVERE:
      return `Severe brain injury. Immediate medical intervention required. Automatic RED triage category. Consider airway protection.${ageContext}`
    
    case GCS_INTERPRETATIONS.CRITICAL:
      return `Critical brain injury. Immediate resuscitation required. Automatic RED triage category. Secure airway immediately.${ageContext}`
    
    default:
      return `GCS assessment complete.${ageContext}`
  }
}

/**
 * Get minimum triage category based on GCS score
 * @param {number} total - GCS total score
 * @returns {string|null} Minimum triage category
 */
export const getMinimumTriageCategory = (total) => {
  if (total <= 8) return 'RED'     // Severe/Critical
  if (total <= 12) return 'ORANGE' // Moderate - requires urgent attention
  if (total <= 14) return 'YELLOW' // Minor - but still concerning
  return null // Normal - no GCS-based triage escalation needed
}

/**
 * Get age-appropriate GCS expectations and normal ranges
 * @param {number} ageMonths - Age in months
 * @returns {object} Normal ranges and expectations
 */
export const getNormalRangesByAge = (ageMonths) => {
  if (ageMonths < 1) { // Neonate
    return {
      expectedTotal: '13-15',
      notes: 'Neonates may have lower verbal scores normally. Any GCS <13 is concerning.',
      redFlags: ['No eye opening', 'No response to voice', 'Abnormal posturing']
    }
  }
  
  if (ageMonths < 6) { // Young infant
    return {
      expectedTotal: '14-15',
      notes: 'Young infants should respond to voice and localize pain. Verbal assessment uses crying/cooing.',
      redFlags: ['No social interaction', 'Weak cry', 'Poor feeding with altered GCS']
    }
  }
  
  if (ageMonths < 24) { // Older infant/toddler
    return {
      expectedTotal: '15',
      notes: 'Should have normal eye opening, appropriate crying, and purposeful movement.',
      redFlags: ['Not recognizing parents', 'Excessive irritability', 'Lethargy']
    }
  }
  
  // Child/adolescent
  return {
    expectedTotal: '15',
    notes: 'Should be fully oriented and following commands appropriately for age.',
    redFlags: ['Confusion', 'Inappropriate responses', 'Not following simple commands']
  }
}

/**
 * Get GCS component options for UI
 * @param {string} component - 'eye', 'verbal', or 'motor'
 * @param {number} ageMonths - Age in months
 * @returns {array} Array of options with value and label
 */
export const getGCSOptions = (component, ageMonths) => {
  const scale = ageMonths < 24 ? GCS_SCALES.PEDIATRIC : GCS_SCALES.STANDARD
  
  switch (component) {
    case 'eye':
      return Object.entries(STANDARD_EYE_RESPONSES).map(([value, label]) => ({
        value: parseInt(value),
        label: `${value} - ${label}`
      })).reverse()
    
    case 'verbal':
      const verbalResponses = scale === GCS_SCALES.PEDIATRIC 
        ? PEDIATRIC_VERBAL_RESPONSES 
        : STANDARD_VERBAL_RESPONSES
      return Object.entries(verbalResponses).map(([value, label]) => ({
        value: parseInt(value),
        label: `${value} - ${label}`
      })).reverse()
    
    case 'motor':
      return Object.entries(MOTOR_RESPONSES).map(([value, label]) => ({
        value: parseInt(value),
        label: `${value} - ${label}`
      })).reverse()
    
    default:
      return []
  }
}

/**
 * Get GCS badge color class based on interpretation
 * @param {string} interpretation - GCS interpretation
 * @returns {string} CSS class name
 */
export const getGCSBadgeClass = (interpretation) => {
  switch (interpretation) {
    case GCS_INTERPRETATIONS.NORMAL:
      return 'badge-green'
    case GCS_INTERPRETATIONS.MINOR:
      return 'badge-blue'
    case GCS_INTERPRETATIONS.MODERATE:
      return 'badge-yellow'
    case GCS_INTERPRETATIONS.SEVERE:
      return 'badge-red'
    case GCS_INTERPRETATIONS.CRITICAL:
      return 'badge-red animate-pulse'
    default:
      return 'badge-gray'
  }
}

/**
 * Validate GCS input values
 * @param {object} gcsData - Object with eye, verbal, motor values
 * @returns {object} Validation result with isValid and errors
 */
export const validateGCSInput = (gcsData) => {
  const errors = []
  
  if (!gcsData.eye || gcsData.eye < 1 || gcsData.eye > 4) {
    errors.push('Eye opening score must be between 1 and 4')
  }
  
  if (!gcsData.verbal || gcsData.verbal < 1 || gcsData.verbal > 5) {
    errors.push('Verbal response score must be between 1 and 5')
  }
  
  if (!gcsData.motor || gcsData.motor < 1 || gcsData.motor > 6) {
    errors.push('Motor response score must be between 1 and 6')
  }
  
  return {
    isValid: errors.length === 0,
    errors
  }
}