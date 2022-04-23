import React from "react";

import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';

import L from 'leaflet';

import 'leaflet/dist/leaflet.css';

import red from '../assets/red.png';

import blue from '../assets/blue.png';

function setIcon(marker) {

  var icon = new L.Icon({
                  iconUrl: (marker === 'red') ? red : blue,
                  iconSize: [25, 41],
                  iconAnchor: [12, 41],
                  popupAnchor: [1, -34]
  });

  return icon;
}

export default function Map(props) {

  console.log('Map', props.data);

  if (!props.data || props.data === 'undefined') {
    console.log('Map props.data null or undefined');
    return
  }

  var lat = props.data.length > 0 ? props.data[0].location.latitude : 22.34;

  var lng = props.data.length > 0 ? props.data[0].location.longitude : 113.41;

  const zoom = 10;

  const position = [lat, lng];

  console.log('lat', lat, 'lng', lng, 'props.data', props.data)

  return (
    <>
      <div style={{height: "50%", width: "95%", padding: "5px"}}>
        <MapContainer
            center={position}
            zoom={zoom}
            style={{height: "85vh", width: "85wh" }}
            scrollWheelZoom={false}
        >
        {
          props.data.map(item => (

          <Marker
            position={[item.location.latitude,item.location.longitude]}
            icon={setIcon(item.marker)}
          >

          <Popup>{item.name.first} {item.name.last}</Popup>

          </Marker>

          ))
        }

        <TileLayer
          attribution='&amp;copy <a href="http://osm.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        </MapContainer>

      </div>
    </>
  )
}