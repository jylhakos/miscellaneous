import React, { useState } from "react";

import "./index.css";

export default function StockData() {
  
  const [ searchValue, setSearchValue ] = useState('')

  const [ values, setValues ] = useState([])

  //const [ noresult, setNoResult ] = useState(null)

  const search = (event) => {

    event.preventDefault()

    console.log('search', event.target,'searchValue', searchValue)

    const url = 'https://jsonmock.hackerrank.com/api/stocks?date=' + searchValue

    console.log('url', url)

    fetch(url)
    .then(response => response.json())
    .then(data => { 
      console.log(data.data, 'length', data.data.length); 
      setValues(data.data);
      //if(data.data.length < 1) { setNoResult('No Results Found') }
      if(data.data.length < 1) {
        const div = document.getElementById('no-result')  
        div.innerHTML = '';  
        div.appendChild(document.createTextNode('No Results Found'));
      }
    });

  }

  const handleSearch = (event) => {

    console.log('handleSearch', event.target.value)

    setSearchValue(event.target.value)
  }

  const generateKey = (pre) => {
    return `${ pre }_${ new Date().getTime() }`;
  }

  return (
    <div className="layout-column align-items-center mt-50">
        <section className="layout-row align-items-center justify-content-center">
          <input type="text" className="large" value={searchValue} onChange={handleSearch} placeholder="5-January-2000" id="app-input" data-testid="app-input"/>
          <button className="" id="submit-button" data-testid="submit-button" onClick={search}>Search</button>
        </section>

        { 
        values.length !== 0
        ?
        <ul className="mt-50 slide-up-fade-in styled" id="stockData" data-testid="stock-data">
           {
            values.map((v,i) => 
              <>
                <li className="py-9" key={ generateKey(v.open) }> Open: {v.open}</li>
                <li className="py-9" key={ generateKey(v.close) }> Close: {v.close}</li>
                <li className="py-9" key={ generateKey(v.high) }> High: {v.high}</li>
                <li className="py-9" key={ generateKey(v.low) }> Low: {v.low}</li> 
              </>
            ) 
          }
           
        </ul>
        :
         <div className="mt-50 slide-up-fade-in" id="no-result" data-testid="no-result"></div>
        }
      </div>
  );
}
