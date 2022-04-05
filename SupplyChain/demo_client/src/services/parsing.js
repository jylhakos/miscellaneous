
'use strict'

const _ = require('lodash')
const moment = require('moment')
//const { FLOAT_PRECISION } = require('./payloads')
const FLOAT_PRECISION = 1000000

/*const STRINGIFIERS = {
  LOCATION: v => `${v.latitude}, ${v.longitude}`,
  tilt: v => `X: ${v.x}, Y: ${v.y}`,
  shock: v => `Accel: ${v.accel}, Duration: ${v.duration}`,
  '*': v => JSON.stringify(v, null, 1).replace(/[{}"]/g, '')
}*/

const STRINGIFIERS = {
  //LOCATION: v => `${v.latitude / FLOAT_PRECISION}, ${v.longitude / FLOAT_PRECISION}`,
  LOCATION: v => `${v.latitude}, ${v.longitude}`,
  '*': v => JSON.stringify(v, null, 1).replace(/[{}"]/g, '')
}

/**
 * Parses a property value by its name or type, returning a string for display
 */
const stringifyValue = (value, type, name) => {
  if (STRINGIFIERS[type]) {
    return STRINGIFIERS[type](value)
  }
  if (STRINGIFIERS[name]) {
    return STRINGIFIERS[name](value)
  }
  return STRINGIFIERS['*'](value)
}

/**
 * Simple functions that turn numbers or number-like strings to
 * an integer (in millionths) or back to a float.
 */
const toFloat = num => parseInt(num) / FLOAT_PRECISION
const toInt = num => parseInt(parseFloat(num) * FLOAT_PRECISION)

/**
 * Calls toFloat on a property value, or it's sub-values in the case of
 * location, tilt, or shock
 */
const floatifyValue = value => {
  if (_.isString(value)) value = JSON.parse(value)
  if (_.isObject(value)) return _.mapValues(value, toFloat)
  return toFloat(value)
}

/**
 * Parses seconds into a date/time string
 */
const formatTimestamp = sec => {
  if (!sec) {
    sec = Date.now() / 1000
  }
  return moment.unix(sec).format('MM/DD/YYYY, h:mm:ss a')
}

module.exports = {
  toInt,
  toFloat,
  stringifyValue,
  floatifyValue,
  formatTimestamp
}
