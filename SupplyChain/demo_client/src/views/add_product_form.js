
const m = require('mithril')

const api = require('../services/api')
const payloads = require('../services/payloads')
const transactions = require('../services/transactions')
const parsing = require('../services/parsing')
const {MultiSelect} = require('../components/forms')
const layout = require('../components/layout')

/**
 * Possible selection options
 */
/*const authorizableProperties = [
  ['location', 'Location'],
  ['temperature', 'Temperature'],
  ['tilt', 'Tilt'],
  ['shock', 'Shock']
]*/

const authorizableProperties = [
  ['product_location', 'Location']
]

/**
 * The Form for tracking a new product.
 */
const AddProductForm = {
  oninit (vnode) {
    // Initialize the empty reporters fields
    vnode.state.reporters = [
      {
        reporterKey: '',
        properties: []
      }
    ]
    api.get('agents')
      .then(agents => {
        const publicKey = api.getPublicKey()
        vnode.state.agents = agents.filter(agent => agent.key !== publicKey)
      })
  },

  view (vnode) {
    return m('.product_form',
             m('form', {
               onsubmit: (e) => {
                 e.preventDefault()
                 _handleSubmit(vnode.attrs.signingKey, vnode.state)
               }
             },
             m('legend', 'Track New Product'),
             _formGroup('Serial Number', m('input.form-control', {
               type: 'text',
               oninput: m.withAttr('value', (value) => {
                 vnode.state.serialNumber = value
               }),
               value: vnode.state.serialNumber
             })),
             _formGroup('Category', m('input.form-control', {
               type: 'text',
               oninput: m.withAttr('value', (value) => {
                 vnode.state.category = value
               }),
               value: vnode.state.category
             })),

             /*layout.row([
               _formGroup('Color', m('input.form-control', {
                 type: 'number',
                 min: 0,
                 step: 'any',
                 oninput: m.withAttr('value', (value) => {
                   vnode.state.lengthInCM = value
                 }),
                 value: vnode.state.lengthInCM
               })),*/
               layout.row([
               _formGroup('Color', m('input.form-control', {
                 type: 'text',
                 oninput: m.withAttr('value', (value) => {
                   vnode.state.product_color_state = value
                 }),
                 value: vnode.state.product_color_state
               })),
               _formGroup('Weight (kg)', m('input.form-control', {
                 type: 'number',
                 step: 'any',
                 oninput: m.withAttr('value', (value) => {
                   vnode.state.weightInKg = value
                 }),
                 value: vnode.state.weightInKg
               }))
             ]),

             layout.row([
               _formGroup('Latitude', m('input.form-control', {
                 type: 'number',
                 step: 'any',
                 min: -90,
                 max: 90,
                 oninput: m.withAttr('value', (value) => {
                   vnode.state.latitude = value
                 }),
                 value: vnode.state.latitude
               })),
               _formGroup('Longitude', m('input.form-control', {
                 type: 'number',
                 step: 'any',
                 min: -180,
                 max: 180,
                 oninput: m.withAttr('value', (value) => {
                   vnode.state.longitude = value
                 }),
                 value: vnode.state.longitude
               }))
             ]),

             m('.reporters.form-group',
               m('label', 'Authorize Reporters'),

               vnode.state.reporters.map((reporter, i) =>
                 m('.row.mb-2',
                   m('.col-sm-8',
                     m('input.form-control', {
                       type: 'text',
                       placeholder: 'Add reporter by name or public key...',
                       oninput: m.withAttr('value', (value) => {
                         // clear any previously matched values
                         vnode.state.reporters[i].reporterKey = null
                         const reporter = vnode.state.agents.find(agent => {
                           return agent.name === value || agent.key === value
                         })
                         if (reporter) {
                           vnode.state.reporters[i].reporterKey = reporter.key
                         }
                       }),
                       onblur: () => _updateReporters(vnode, i)
                     })),

                   m('.col-sm-4',
                     m(MultiSelect, {
                       label: 'Select Fields',
                       options: authorizableProperties,
                       selected: reporter.properties,
                       onchange: (selection) => {
                         vnode.state.reporters[i].properties = selection
                       }
                     }))))),

             m('.row.justify-content-end.align-items-end',
               m('col-2',
                 m('button.btn.btn-primary',
                   'Create Record')))))
  }
}

/**
 * Update the reporter's values after a change occurs in the name of the
 * reporter at the given reporterIndex. If it is empty, and not the only
 * reporter in the list, remove it.  If it is not empty and the last item
 * in the list, add a new, empty reporter to the end of the list.
 */
const _updateReporters = (vnode, reporterIndex) => {
  let reporterInfo = vnode.state.reporters[reporterIndex]
  let lastIdx = vnode.state.reporters.length - 1
  if (!reporterInfo.reporterKey && reporterIndex !== lastIdx) {
    vnode.state.reporters.splice(reporterIndex, 1)
  } else if (reporterInfo.reporterKey && reporterIndex === lastIdx) {
    vnode.state.reporters.push({
      reporterKey: '',
      properties: []
    })
  }
}

/**
 * Handle the form submission.
 *
 * Extract the appropriate values to pass to the create record transaction.
 */
const _handleSubmit = (signingKey, state) => {
  const recordPayload = payloads.createRecord({
    recordId: state.serialNumber,
    recordType: 'product',
    properties: [
      {
        name: 'product_category',
        stringValue: state.category,
        dataType: payloads.createRecord.enum.STRING
      },
      /*{
        name: 'product_color',
        intValue: parsing.toInt(state.lengthInCM),
        dataType: payloads.createRecord.enum.INT
      },*/
      {
        name: 'product_color',
        stringValue: state.product_color_state,
        dataType: payloads.createRecord.enum.STRING
      },
      {
        name: 'product_weight',
        intValue: parsing.toInt(state.weightInKg),
        dataType: payloads.createRecord.enum.INT
      },
      {
        name: 'product_location',
        locationValue: {
          latitude: parsing.toInt(state.latitude),
          longitude: parsing.toInt(state.longitude)
          //latitude: parseFloat(state.latitude) * 1000000,
          //longitude: parseFloat(state.longitude) * 1000000
        },
        dataType: payloads.createRecord.enum.LOCATION
      }
    ]
  })

  const reporterPayloads = state.reporters
    .filter((reporter) => !!reporter.reporterKey)
    .map((reporter) => payloads.createProposal({
      recordId: state.serialNumber,
      receivingAgent: reporter.reporterKey,
      role: payloads.createProposal.enum.REPORTER,
      properties: reporter.properties
    }))

  transactions.submit([recordPayload].concat(reporterPayloads), true)
    .then(() => m.route.set(`/product/${state.serialNumber}`))
}

/**
 * Create a form group (this is a styled form-group with a label).
 */
const _formGroup = (label, formEl) =>
  m('.form-group',
    m('label', label),
    formEl)

module.exports = AddProductForm
