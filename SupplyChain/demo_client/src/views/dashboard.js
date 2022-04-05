
'use strict'

const m = require('mithril')

const Dashboard = {
  view (vnode) {
    return [
      m('.header.text-center.mb-4',
        m('h4', 'Blockchain'),
        m('h1.mb-3', 'Supply Chain'),
        m('h5',
          m('em',
            'Powered by ',
            m('strong', 'Sawtooth')))),
      m('.blurb',  
        m('p',
          'Click the link in the navigation bar to login or signup ',
          'on the page and you will be able to view products or ',
          'transfer ownership of products in the  ',
          m('em', 'blockchain '),
          'and track the location of products on the world map. '))
    ]
  }
}

module.exports = Dashboard
