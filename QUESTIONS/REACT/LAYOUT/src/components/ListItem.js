import React, { useState }  from "react";

import "./index.css";

export default function ListItem(props) {

  const handleClick = function(obj) {

    var item = {...obj};

    item.marker = 'blue';

    const data = props.data.map(d => {
      if (d.key == item.key) {
          d.marker = 'blue';
      } else {
        d.marker = 'red';
      }
    })

    props.setItem(item);

    console.log('handleClick', item);
  }

  return (
    <>
      <div style={{height: "25%", width: "25%", padding: "5px", backgroundColor: 'transparent'}}>
        {
          props.data.map(d =>
            <div style={{padding: '5px'}}>
              <button key={d.key} style={{ backgroundColor: '#E3E3E3', boxShadow: 'none', borderWidth: '1px', borderStyle: 'solid', borderColor: '#CFCFCF'}}>
                <div className='py-10 pr-10'>
                  <div onClick={(e) => {
                                        e.stopPropagation();
                                        console.log('child');
                                        handleClick(d);
                                        }}>
                  <div style={{padding: '5px'}}>
                    {d.name}
                  </div>
                  <div style={{padding: '5px'}}>
                    <img src={d.url} alt={d.name}/>
                  </div>
                  </div>
                </div>
              </button>
            </div>
          )
        }
      </div>
    </>
  )
}