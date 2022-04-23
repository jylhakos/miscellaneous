import React, { useState, useEffect } from "react";

import "./index.css";

import ListItem from './ListItem'

import Item from './Item'

import Map from './Map'

import blank from '../assets/blank.png';

const list = [
    { key: 1,
      name: "Test A",
      url: blank,
      marker: 'red',
      lat: 39.7341,
      lng: -104.9991
    },
    { key: 2,
      name: "Test B",
      url: blank,
      marker: 'red',
      lat: 39.7435,
      lng: -104.9891
    },
    { key: 3,
      name: "Test C",
      url: blank,
      marker: 'red',
      lat: 39.7355,
      lng: -104.9867
    },
    { key: 4,
      name: "Test D",
      url: blank,
      marker: 'red',
      lat: 39.7368,
      lng: -104.9855
    },
    { key: 5,
      name: "Test E",
      url: blank,
      marker: 'red',
      lat: 39.7388,
      lng: -104.9846
    },
    { key: 6,
      name: "Test F",
      url: blank,
      marker: 'red',
      lat: 39.7331,
      lng: -104.9841
    }
];

export default function Layout() {

  const [data, setData] = useState([]);

  const [item, setItem] = useState(null);

  const [info, setInfo] = useState([]);

  useEffect(() => {

    setData(list);

    console.log('setData', list);

  },[])

  useEffect(() => {

    const download = async () => {

      const url = 'https://jsonmock.hackerrank.com/api/stocks?date=5-January-2000'

      console.log('url', url)

      const response = await fetch(url);

      const result = await response.json();

      console.log('result', result)

      if (result) {

        setInfo(result.data);
      
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

  }, info);

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