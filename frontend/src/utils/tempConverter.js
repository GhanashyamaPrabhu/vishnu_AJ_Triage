// Temperature conversion utilities

/**
 * Convert Fahrenheit to Celsius
 * @param {number} fahrenheit - Temperature in Fahrenheit
 * @returns {number} Temperature in Celsius (rounded to 1 decimal place)
 */
export const fahrenheitToCelsius = (fahrenheit) => {
  if (typeof fahrenheit !== 'number' || isNaN(fahrenheit)) {
    return null
  }
  return Math.round(((fahrenheit - 32) * 5 / 9) * 10) / 10
}

/**
 * Convert Celsius to Fahrenheit
 * @param {number} celsius - Temperature in Celsius
 * @returns {number} Temperature in Fahrenheit (rounded to 1 decimal place)
 */
export const celsiusToFahrenheit = (celsius) => {
  if (typeof celsius !== 'number' || isNaN(celsius)) {
    return null
  }
  return Math.round(((celsius * 9 / 5) + 32) * 10) / 10
}

/**
 * Format temperature display with unit
 * @param {number} temp - Temperature value
 * @param {string} unit - 'F' or 'C'
 * @returns {string} Formatted temperature string
 */
export const formatTemperature = (temp, unit = 'F') => {
  if (typeof temp !== 'number' || isNaN(temp)) {
    return '--°' + unit
  }
  return `${temp.toFixed(1)}°${unit}`
}

/**
 * Get temperature status based on Fahrenheit value
 * @param {number} tempF - Temperature in Fahrenheit
 * @returns {object} Status object with category, color, and description
 */
export const getTemperatureStatus = (tempF) => {
  if (typeof tempF !== 'number' || isNaN(tempF)) {
    return {
      category: 'unknown',
      color: 'gray',
      description: 'Temperature not recorded'
    }
  }

  if (tempF < 95.0) {
    return {
      category: 'hypothermia',
      color: 'blue',
      description: 'Severe hypothermia'
    }
  }
  
  if (tempF < 97.8) {
    return {
      category: 'low',
      color: 'blue',
      description: 'Below normal'
    }
  }
  
  if (tempF <= 99.1) {
    return {
      category: 'normal',
      color: 'green',
      description: 'Normal'
    }
  }
  
  if (tempF <= 100.4) {
    return {
      category: 'elevated',
      color: 'yellow',
      description: 'Slightly elevated'
    }
  }
  
  if (tempF <= 103.0) {
    return {
      category: 'fever',
      color: 'orange',
      description: 'Fever'
    }
  }
  
  if (tempF <= 105.8) {
    return {
      category: 'high_fever',
      color: 'red',
      description: 'High fever'
    }
  }
  
  return {
    category: 'hyperpyrexia',
    color: 'red',
    description: 'Hyperpyrexia - DANGER'
  }
}

/**
 * Get temperature range description
 * @returns {object} Temperature ranges with descriptions
 */
export const getTemperatureRanges = () => {
  return {
    normal: {
      fahrenheit: '97.8 - 99.1°F',
      celsius: '36.6 - 37.3°C',
      description: 'Normal body temperature'
    },
    fever: {
      fahrenheit: '> 100.4°F',
      celsius: '> 38.0°C',
      description: 'Fever threshold'
    },
    highFever: {
      fahrenheit: '> 103.0°F',
      celsius: '> 39.4°C',
      description: 'High fever'
    },
    danger: {
      fahrenheit: '> 105.8°F',
      celsius: '> 41.0°C',
      description: 'Hyperpyrexia - immediate intervention required'
    }
  }
}

/**
 * Validate temperature input
 * @param {number} tempF - Temperature in Fahrenheit
 * @returns {object} Validation result
 */
export const validateTemperature = (tempF) => {
  const errors = []
  
  if (typeof tempF !== 'number' || isNaN(tempF)) {
    errors.push('Temperature must be a valid number')
    return { isValid: false, errors }
  }
  
  if (tempF < 80.0) {
    errors.push('Temperature too low (minimum 80°F)')
  }
  
  if (tempF > 115.0) {
    errors.push('Temperature too high (maximum 115°F)')
  }
  
  return {
    isValid: errors.length === 0,
    errors,
    warnings: tempF > 105.8 ? ['Hyperpyrexia - immediate medical attention required'] : []
  }
}

/**
 * Get temperature CSS class for styling
 * @param {number} tempF - Temperature in Fahrenheit
 * @returns {string} CSS class name
 */
export const getTemperatureClass = (tempF) => {
  const status = getTemperatureStatus(tempF)
  
  switch (status.category) {
    case 'hypothermia':
    case 'low':
      return 'text-blue-600 bg-blue-50'
    case 'normal':
      return 'text-green-600 bg-green-50'
    case 'elevated':
      return 'text-yellow-600 bg-yellow-50'
    case 'fever':
      return 'text-orange-600 bg-orange-50'
    case 'high_fever':
    case 'hyperpyrexia':
      return 'text-red-600 bg-red-50'
    default:
      return 'text-gray-600 bg-gray-50'
  }
}

/**
 * Get temperature badge class for display
 * @param {number} tempF - Temperature in Fahrenheit
 * @returns {string} Badge CSS class
 */
export const getTemperatureBadgeClass = (tempF) => {
  const status = getTemperatureStatus(tempF)
  
  switch (status.category) {
    case 'hypothermia':
    case 'low':
      return 'badge-blue'
    case 'normal':
      return 'badge-green'
    case 'elevated':
      return 'badge-yellow'
    case 'fever':
      return 'badge-orange'
    case 'high_fever':
    case 'hyperpyrexia':
      return 'badge-red'
    default:
      return 'badge-gray'
  }
}

/**
 * Create temperature conversion display object
 * @param {number} tempF - Temperature in Fahrenheit
 * @returns {object} Display object with both units and status
 */
export const createTemperatureDisplay = (tempF) => {
  const tempC = fahrenheitToCelsius(tempF)
  const status = getTemperatureStatus(tempF)
  const validation = validateTemperature(tempF)
  
  return {
    fahrenheit: {
      value: tempF,
      formatted: formatTemperature(tempF, 'F'),
      unit: '°F'
    },
    celsius: {
      value: tempC,
      formatted: formatTemperature(tempC, 'C'),
      unit: '°C'
    },
    status,
    validation,
    cssClass: getTemperatureClass(tempF),
    badgeClass: getTemperatureBadgeClass(tempF),
    isValid: validation.isValid,
    isCritical: status.category === 'hyperpyrexia' || status.category === 'hypothermia'
  }
}