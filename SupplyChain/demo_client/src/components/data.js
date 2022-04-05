'use strict'

const m = require('mithril')
const ol = require('ol')
const Layer = require('ol/layer')
const Source = require('ol/source')
const Proj = require('ol/proj')
const Geom = require('ol/geom')
const Style = require('ol/style')
const Chart = require('chart.js')

const makeCoords = (coords) => {
  return Proj.fromLonLat([coords.longitude, coords.latitude])
}

const createMarker = (coords) => {
  let feature = new ol.Feature({
    geometry: new Geom.Point(
      makeCoords(coords)
    ),
    name: 'Point'
  })
  feature.setStyle(new Style.Style({
    image: new Style.Icon({
      crossOrigin: 'anonymous',
      src: '../images/location.png'
    })
  }))

  return feature
}

const LineGraphWidget = {
  view (vnode) {
    return m('canvas#graph-container', { width: '100%' })
  },

  parseUpdates (updates) {

    console.log('parseUpdates')

    return updates.map(d => ({
      t: d.timestamp * 1000,
      y: d.value,
      reporter: _.truncate(d.reporter.public_key, {length: 16})
    }))
  },

  oncreate (vnode) {
    const ctx = document.getElementById('graph-container').getContext('2d')

    vnode.state.graph = new Chart(ctx, {
      type: 'line',
      data: {
        datasets: [{
          data: this.parseUpdates(vnode.attrs.updates),
          fill: false,
          pointStyle: 'circle',
          pointRadius: 8,
          borderColor: '#ff0000',
          lineTension: 0
        }]
      },
      options: {
        legend: {
          display: false
        },
        tooltips: {
          bodyFontSize: 14,
          displayColors: false,
          custom: model => {
            if (model.body) {
              const index = model.dataPoints[0].index
              const reporter = vnode.state.graph.data.datasets[0]
                .data[index].reporter
              const value = model.body[0].lines[0]
              model.body[0].lines[0] = `${value} (from ${reporter})`
            }
          }
        },
        responsive: true,
        scales: {
          xAxes: [{
            type: 'time',
            offset: true,
            display: true,
            time: {
              minUnit: 'second',
              tooltipFormat: 'MM/DD/YYYY, h:mm:ss a'
            },
            ticks: {
              major: {
                fontStyle: 'bold',
                fontColor: '#ff0000'
              }
            }
          }],
          yAxes: [{
            type: 'linear',
            offset: true,
            display: true
          }]
        }
      }
    })
  },

  onupdate (vnode) {
    const data = this.parseUpdates(vnode.attrs.updates)
    vnode.state.graph.data.datasets[0].data = data
    vnode.state.graph.update()
  }
}

const MapWidget = {
  map: null,
  markers: [],
  line: new Geom.LineString([]),

  createMap (coordinates) {

    console.log('createMap')

    const currentLocation = coordinates[0]

    MapWidget.map = new ol.Map({
      view: new ol.View({
        center: makeCoords(currentLocation),
        zoom: 7
      }),
      layers: [
        new Layer.Tile({
          source: new Source.OSM()
        })
      ],
      target: 'map',
      controls: []
    })

    // Create markers for each location
    for ( let i = coordinates.length-1; i >= 0; i-- ) {

      console.log('createMap: ' + coordinates[i].latitude + ' ' + coordinates[i].longitude)

      MapWidget.markers.push(createMarker(coordinates[i]))



      //add coordinate to connection line
      MapWidget.line.appendCoordinate(makeCoords(coordinates[i]))
    }

    // build line feature
    let lineFeature = new ol.Feature({
      geometry: MapWidget.line,
      name: 'Line'
    })
    lineFeature.setStyle(new Style.Style({
      stroke: new Style.Stroke({
        color: "#E74C3C",
        width: 3
      })
    }))

    // Create Layer with Markers
    let markerLayer = new Layer.Vector({
      source: new Source.Vector({
        features: [lineFeature, ...MapWidget.markers]
      })
    })

    MapWidget.map.addLayer(markerLayer)
  },

  view (vnode) {
    return m('#map')
  },

  oncreate (vnode) {
    MapWidget.line.setCoordinates([])
    MapWidget.markers = []

    console.log('oncreate')

    let coordinates = vnode.attrs.coordinates.map((coord) => {
      return {latitude: coord.latitude, longitude: coord.longitude}
    })

    if (coordinates.length > 0) {
      MapWidget.createMap(coordinates.reverse())
    }
  },

  onbeforeupdate (vnode, old) {
    // Coordinates exist and have changed
    return vnode.attrs.coordinates &&
      vnode.attrs.coordinates.length !== old.attrs.coordinates.length
  },

  onupdate (vnode) {

    console.log('onupdate')

    let coordinates = vnode.attrs.coordinates.map((coord) => {

      console.log('coordinates: ' + coord.latitude + ' ' + coord.longitude)

      return {
        latitude: coord.latitude,
        longitude: coord.longitude
      }

    }).reverse()

    const currentLocation = coordinates[0]

    console.log('currentLocation: ' + currentLocation.latitude + ' ' + currentLocation.longitude)

    // initialize map if no previous locations
    if (vnode.attrs.coordinates.length === 1) {

      console.log('vnode.attrs.coordinates.length: ' + vnode.attrs.coordinates.length)

      MapWidget.createMap(coordinates)

    } else {
      // Center view on new location
      MapWidget.map.getView()
        .setCenter(makeCoords(currentLocation))

      let marker = createMarker(currentLocation)

      MapWidget.markers.push(marker)

      MapWidget.map.getLayers()
        .getArray()[1]
        .getSource()
        .addFeature(marker)

      MapWidget.line.appendCoordinate(makeCoords(currentLocation))
    }

  }
}

module.exports = {
  LineGraphWidget,
  MapWidget
}
