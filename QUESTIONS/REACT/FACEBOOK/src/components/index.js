import React, { useState, useEffect } from "react";

import "./index.css";

import ListItem from './ListItem'

import Item from './Item'

import Map from './Map'

import blank from '../assets/blank.png';

const list = [{"_id":"214bda7e-7827-4ab4-975b-9a62f5015306","name":{"last":"Pace","first":"Irma"},"email":"chandra.oneill@emtrac.career","picture":"https://placebear.com/231/228","location":{"latitude":22.37,"longitude":114.01}, "marker": "red"},

{"_id":"7355c108-5302-41e9-bc41-e60a8c5e2d99","name":{"last":"Terry","first":"Jaime"},"email":"scott.richards@portaline.moe","picture":"https://placebear.com/233/166","location":{"latitude":22.34,"longitude":113.41}, "marker": "red"},

{"_id":"2ef52f10-83ca-4186-900a-ab0bc432583f","name":{"last":"Wise","first":"Solomon"},"email":"shana.velazquez@arctiq.florist","picture":"https://placebear.com/126/58","location":{"latitude":22.39,"longitude":114.17}, "marker": "red"},

{"_id":"99b9821e-9062-4fbc-a621-61ecf77f1104","name":{"last":"Gutierrez","first":"Alyson"},"email":"hahn.manning@cujo.juegos","picture":"https://placebear.com/98/52","location":{"latitude":22.39,"longitude":113.56}, "marker": "red"},

{"_id":"598e4bca-dac7-4d36-bc9c-2728f97eaef5","name":{"last":"Grant","first":"Nieves"},"email":"casey.kent@singavera.clothing","picture":"https://placebear.com/69/67","location":{"latitude":22.37,"longitude":114.02}, "marker": "red"}
];

export default function Layout() {

  const [data, setData] = useState([]);

  const [item, setItem] = useState(null);

  var single = 0;

  const download = () => {

    var url = 'https://api.json-generator.com/templates/-xdNcNKYtTFG/data'

    var bearer = 'v3srs6i1veetv3b2dolta9shrmttl72vnfzm220z'

    console.log('download', 'url', url, 'bearer', bearer);

    var headers = new Headers();

    headers.append('Content-Type', 'application/json');
      
    headers.append('Accept', 'application/json');
  
    headers.append('Authorization', 'Bearer ' + bearer);

    headers.append('Origin', 'http://localhost:8000');

    const response = fetch(url, {
      method: 'GET',
      mode: 'cors',
      headers: headers
    })
    .then((response) => response.json())
    .then((result) => {
      const data = result.map(item => ({...item, marker: 'red'}));
      console.log('data', data)
      setData(data);
    })
    .catch((error) => { console.log(error.message); setData(list) });
  }

  useEffect(() => {

    download();

    console.log('Layout', data)

  }, [single])

  return (
    <>
      <div className='layout-row mt-1'>
        <div>
            <section className='layout-row pl-2 align-items-center justify-content-center'>
              <input type='text' className='large' placeholder="5-January-2000" id="app-input" data-testid="app-input"/>
              <button className="" id="submit-button">Search</button>
            </section>
        </div>
      </div>
      <div className='layout-column mt-2' style={{ backgroundColor: 'transparent', height: "50%", width: "50%"}}>
        <div className='layout-row'>
          <ListItem data={data} setItem={setItem}/>
          <div className='layout-column mt-2'>
            <Map data={data}/>
            <Item item={item}/>
          </div>
        </div>
      </div>
    </>
  );
}