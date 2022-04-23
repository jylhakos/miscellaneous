import React, { useState, useEffect } from "react";

import "./index.css";

import ListItem from './ListItem'

import Item from './Item'

import Map from './Map'

import blank from '../../assets/blank.png';

const list = [
    { key: 1,
      name: "Test A",
      url: blank,
      marker: 'red',
      lat: 39.7341,
      lng: -104.9903
    },
    { key: 2,
      name: "Test B",
      url: blank,
      marker: 'red',
      lat: 39.7351,
      lng: -104.9897
    },
    { key: 3,
      name: "Test C",
      url: blank,
      marker: 'red',
      lat: 39.7355,
      lng: -104.9885
    },
    { key: 4,
      name: "Test D",
      url: blank,
      marker: 'red',
      lat: 39.7368,
      lng: -104.9876
    }
];

export default function LayoutData() {

  const [data, setData] = useState([]);

  const [item, setItem] = useState(null);

  useEffect(() => {

    setData(list);

    console.log('setData', list);

  }, [])

  return (
    <>
      <div className='layout-row mt-5'>
        <div>
            <section className='layout-row pl-5 align-items-center justify-content-center'>
              <input type='text' className='large' placeholder="5-January-2000" id="app-input" data-testid="app-input"/>
              <button className="" id="submit-button">Search</button>
            </section>
        </div>
      </div>
      <div className='layout-column mt-5' style={{ backgroundColor: 'transparent'}}>
        <div className='layout-row'>
          <ListItem data={data} setItem={setItem}/>
          <Map data={data}/>
        </div>
      </div>
      <div className='layout-row mt-5'>
        <div style={{height: "75%", width: "75%", paddingRight: "10px", paddingTop: "5px"}}>
          <div className='layout-row pl-5'>
          <Item item={item}/>
          </div>
        </div>
      </div>
    </>
  );
}