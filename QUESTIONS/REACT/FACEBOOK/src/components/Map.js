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
    return null;
  }

  var lat = props.data.length > 0 ? props.data[0].location.latitude : 22.34;

  var lng = props.data.length > 0 ? props.data[0].location.longitude : 113.41;

  const zoom = 10;

  const position = [lat, lng];

  console.log('lat', lat, 'lng', lng, 'props.data', props.data)

  return (
    <>
      <div style={{display: "inline", height: "50vh", width: "70vw", padding: "5px"}}>
        <MapContainer
            center={position}
            zoom={zoom}
            style={{height: "90%", width: "100%" }}
            scrollWheelZoom={false}
        >
        {
          props.data.map(item => (

          <div key={item._id}>

          <Marker
            position={[item.location.latitude,item.location.longitude]}
            icon={setIcon(item.marker)}
          >

          <Popup>{item.name.first} {item.name.last}</Popup>

          </Marker>

          </div>

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