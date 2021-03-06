
'use strict'

const blocks = require('../db/blocks')
const state = require('../db/state')
const protos = require('./protos')

const deltaQueue = {
  _queue: [],
  _running: false,

  add (promisedFn) {
    this._queue.push(promisedFn)
    this._runUntilEmpty()
  },

  _runUntilEmpty () {
    if (this._running) return
    this._running = true
    this._runNext()
  },

  _runNext () {
    if (this._queue.length === 0) {
      this._running = false
    } else {
      const current = this._queue.shift()
      return current().then(() => this._runNext())
    }
  }
}

const getProtoName = address => {
  const typePrefix = address.slice(6, 8)
  if (typePrefix === 'ea') {
    if (address.slice(-4) === '0000') return 'Property'
    else return 'PropertyPage'
  }

  const names = {
    ae: 'Agent',
    aa: 'Proposal',
    ec: 'Record',
    ee: 'RecordType'
  }
  if (names[typePrefix]) return names[typePrefix]

  throw new Error(`Blockchain Error: No Protobuf for prefix "${typePrefix}"`)
}

const getObjectifier = address => {
  const name = getProtoName(address)
  return stateInstance => {
    const obj = protos[name].toObject(stateInstance, {
      enums: String,  // use string names for enums
      longs: Number,  // convert int64 to Number, limiting precision to 2^53
      defaults: true  // use default for falsey values
    })
    if (name === 'PropertyPage') {
      obj.pageNum = parseInt(address.slice(-4), 16)
    }
    return obj
  }
}

const getAdder = address => {
  const addState = state[`add${getProtoName(address)}`]
  const toObject = getObjectifier(address)
  return (stateInstance, blockNum) => {
    addState(toObject(stateInstance), blockNum)
  }
}

const getEntries = ({ address, value }) => {
  return protos[`${getProtoName(address)}Container`]
    .decode(value)
    .entries
}

const handle = (block, changes) => {
  deltaQueue.add(() => {
    return Promise.all(changes.map(change => {
      const addState = getAdder(change.address)
      return Promise.all(getEntries(change).map(entry => {
        return addState(entry, block.blockNum)
      }))
    }))
      .then(() => blocks.insert(block))
  })
}

module.exports = {
  handle
}
