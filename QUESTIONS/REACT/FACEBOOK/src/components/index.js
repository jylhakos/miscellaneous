import React, { useState, useEffect } from "react";

import "./index.css";

import ListItem from './ListItem'

import Item from './Item'

import Map from './Map'

import blank from '../assets/blank.png';

const list = [{"_id":"214bda7e-7827-4ab4-975b-9a62f5015306","name":{"last":"Pace","first":"Irma"},"email":"chandra.oneill@emtrac.career","picture":"https://placebear.com/231/228","location":{"latitude":22.37,"longitude":114.01}},

{"_id":"7355c108-5302-41e9-bc41-e60a8c5e2d99","name":{"last":"Terry","first":"Jaime"},"email":"scott.richards@portaline.moe","picture":"https://placebear.com/233/166","location":{"latitude":22.34,"longitude":113.41}},

{"_id":"2ef52f10-83ca-4186-900a-ab0bc432583f","name":{"last":"Wise","first":"Solomon"},"email":"shana.velazquez@arctiq.florist","picture":"https://placebear.com/126/58","location":{"latitude":22.39,"longitude":114.17}},

{"_id":"99b9821e-9062-4fbc-a621-61ecf77f1104","name":{"last":"Gutierrez","first":"Alyson"},"email":"hahn.manning@cujo.juegos","picture":"https://placebear.com/98/52","location":{"latitude":22.39,"longitude":113.56}},

{"_id":"598e4bca-dac7-4d36-bc9c-2728f97eaef5","name":{"last":"Grant","first":"Nieves"},"email":"casey.kent@singavera.clothing","picture":"https://placebear.com/69/67","location":{"latitude":22.37,"longitude":114.02}}
];

//TODO: REPLACE url WITH picture

export default function Layout() {

  const [data, setData] = useState([]);

  const [item, setItem] = useState(null);

  //const [info, setInfo] = useState([]);

  /*useEffect(() => {

    console.log('useEffect', list);

    setData(list);

    console.log('setData', list);

  },[])*/

  useEffect(() => {

    const download = async () => {

      //const url = 'https://jsonmock.hackerrank.com/api/stocks?date=5-January-2000'

      var url = 'https://api.json-generator.com/templates/-xdNcNKYtTFG/data'

      var bearer = 'v3srs6i1veetv3b2dolta9shrmttl72vnfzm220z'

      console.log('url', url, 'bearer', bearer);

      var headers = new Headers();

      headers.append('Content-Type', 'application/json');
      
      headers.append('Accept', 'application/json');
    
      headers.append('Authorization', 'Bearer ' + bearer);

      headers.append('Origin', 'http://localhost:8000');

      //const response = await fetch(url);

      const response = await fetch(url, {
        method: 'GET',
        mode: 'cors',
        //withCredentials: true,
        //credentials: 'include',
        headers: headers
        //headers: {
        //    'Authorization': bearer,
        //    'Content-Type': 'application/json'
        //}
      })

      const result = await response.json();

      console.log('result', result)

      if (result) {

        //setInfo(result.data);

        setData(result);
      
        console.log('result.data', result.data, 'length', result.data.length); 
          
        if(result.data.length < 1) {
          //const div = document.getElementById('no-result')  
          //div.innerHTML = '';  
          //div.appendChild(document.createTextNode('No Results'));
        }

        return true;
      }

      return false;

    }

    const result = download();

    console.log(result);

   }, data);

  //}, info);

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
      <div className='layout-column mt-2' style={{ backgroundColor: 'transparent'}}>
        <div className='layout-row'>
          <ListItem data={data} setItem={setItem}/>
          <div className='layout-column mt-2' style={{height: "75%", width: "75%"}}>
            <Map data={data}/>
            <Item item={item}/>
          </div>
        </div>
      </div>
    </>
  );
}