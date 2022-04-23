import React from "react";

import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';

import L from 'leaflet';

import 'leaflet/dist/leaflet.css';

//import Icon from './Icon'

import red from '../../assets/red.png';

import blue from '../../assets/blue.png';

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

  var lat = 39.7392;

  var lng = -104.9903;

  const zoom = 15;

  const position = [lat, lng];

  console.log('lat', lat, 'lng', lng, 'props.data',props.data)

  return (
    <>
      <div style={{height: "75%", width: "75%", paddingRight: "10px", paddingTop: "5px"}}>
        <MapContainer
            center={position}
            zoom={zoom}
            style={{height: "115vh", width: "100wh" }}
            scrollWheelZoom={false}
        >
        {
          props.data.map(item => (

          <Marker
            position={[item.lat,item.lng]}
            icon={setIcon(item.marker)}
          >

          <Popup>{item.name}</Popup>

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