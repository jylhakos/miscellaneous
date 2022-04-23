import React from "react";

import { Marker, Popup } from 'react-leaflet';

import L from 'leaflet';

import red from '../../assets/red.png';

import blue from '../../assets/blue.png';

export default function Icon(props) {

var marker = red;

if (props.item.marker === 'blue') {
	const marker = blue;
}

console.log('Icon', marker);

var icon = new L.Icon({
                iconUrl: {marker},
                iconSize: [25, 41],
                iconAnchor: [12, 41],
                popupAnchor: [1, -34]
});

console.log('lat', props.item.lat, 'lng', props.item.lng)

return (
    <>
		<Marker
            position={[props.item.lat,props.item.lng]}
            icon={icon}
        >

        <Popup>{props.item.name}</Popup>

        </Marker>
    </>
    )

}