
'use strict'

const r = require('rethinkdb')

const db = require('./')

const hasCurrentBlock = currentBlock => obj => {
  return r.and(
    obj('startBlockNum').le(currentBlock),
    obj('endBlockNum').gt(currentBlock)
  )
}

const getAttribute = attr => obj => obj(attr)
const getRecordId = getAttribute('recordId')
const getPublicKey = getAttribute('publicKey')
const getName = getAttribute('name')
const getReporters = getAttribute('reporters')
const getAuthorized = getAttribute('authorized')

const hasPublicKey = key => obj => {
  return r.eq(
    key,
    getPublicKey(obj)
  )
}

const getAssociatedAgentId = role => record => record(role).nth(-1)('agentId')
const getOwnerId = getAssociatedAgentId('owners')
const getDeliveryId = getAssociatedAgentId('deliveries')

const isAssociatedWithRecord = association => agent => record => {
  return r.eq(
    association(record),
    getPublicKey(agent)
  )
}

const isRecordOwner = isAssociatedWithRecord(getOwnerId)
const isRecordDelivery = isAssociatedWithRecord(getDeliveryId)

const isReporter = agent => property => {
  return getReporters(property)
    .filter(hasPublicKey(getPublicKey(agent)))
    .do(seq => r.branch(
      seq.isEmpty(),
      false,
      getAuthorized(seq.nth(0))
    ))
}

const getTable = (tableName, block) =>
      r.table(tableName).filter(hasCurrentBlock(block))

const listQuery = filterQuery => block => {
  return getTable('agents', block)
    .filter(filterQuery)
    .map(agent => r.expr({
      'name': getName(agent),
      'key': getPublicKey(agent),
      'owns': getTable('records', block)
        .filter(isRecordOwner(agent))
        .map(getRecordId)
        .distinct(),
      'delivery': getTable('records', block)
        .filter(isRecordDelivery(agent))
        .map(getRecordId)
        .distinct(),
      'reports': getTable('properties', block)
        .filter(isReporter(agent))
        .map(getRecordId)
        .distinct()
    })).coerceTo('array')
}

const fetchQuery = (publicKey, auth) => block => {
  return getTable('agents', block)
    .filter(hasPublicKey(publicKey))
    .pluck('name', 'publicKey')
    .nth(0)
    .do(
      agent => {
        return r.branch(
          auth,
          agent.merge(
            fetchUser(publicKey)),
          agent)
      })
}

const fetchUser = publicKey => {
  return r.table('users')
    .filter(hasPublicKey(publicKey))
    .pluck('username', 'email', 'encryptedKey')
    .nth(0)
}

const list = filterQuery => db.queryWithCurrentBlock(listQuery(filterQuery))

const fetch = (publicKey, auth) =>
      db.queryWithCurrentBlock(fetchQuery(publicKey, auth))

module.exports = {
  list,
  fetch
}
