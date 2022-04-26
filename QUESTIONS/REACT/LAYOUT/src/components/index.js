// npm install axios

import React, { useState, useEffect } from 'react';

import axios from 'axios'

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

/*const download = async (parameter) => {

    //useEffect(() => {

      //const f = async () => {

        console.log('download', parameter);

        const url = 'https://jsonmock.hackerrank.com/api/stocks?date='+parameter;

        console.log('url', url);

        const response = await fetch(url);

        const result = await response.json();

        console.log('result', result)

        if (result) {

          console.log('result.data', result.data, 'length', result.data.length); 

        }
      //}

      //const result = f();

    //}, [info]);
   
    console.log('download', result)

    return result;
}
*/

export default function Layout(props) {

  const [data, setData] = useState([]);

  const [item, setItem] = useState(null);

  const [info, setInfo] = useState([]);

  const getData = async () => {

    const parameter = '5-January-2000';

    const url = 'https://jsonmock.hackerrank.com/api/stocks?date='+parameter;

    try {

      var headers = new Headers();

      headers.append('Content-Type', 'application/json');
      
      headers.append('Accept', 'application/json');

      const response = await axios.get(url, {
        headers: headers,
      });

      console.log('getData', response.data);

      setInfo(response.data);

    } catch (error) {

      console.log(error);
    }
  }

  const download = async (parameter) => {

    //useEffect(() => {

      //const f = async () => {

        console.log('download', parameter);

        const url = 'https://jsonmock.hackerrank.com/api/stocks?date='+parameter;

        console.log('url', url);

        const response = await fetch(url);

        const result = await response.json();

        console.log('result', result)

        if (result) {

          setInfo(result)

          console.log('result.data', result.data, 'length', result.data.length); 

        }
      //}

      //const result = f();

    //}, [info]);
   
    console.log('download', result)

    //return result;
}

  useEffect(() => {

    setData(list);

    console.log('setData', list);

  },[])

  //var info = 0;

  var effect = 0;

  useEffect(() => {

    //const result = download(props.parameter);

    download(props.parameter);

    getData()

    //setInfo(result)

    console.log('Layout', info)

  //}, [props.parameter]);
  //}, []);
  }, [effect])

  /*useEffect(() => {

    const download = async () => {

      console.log('download', props.parameter);

      const url = 'https://jsonmock.hackerrank.com/api/stocks?date='+props.parameter;

      console.log('url', url);

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
  */

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