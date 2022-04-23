import React from 'react';

import './item.css';

export default function Item(props) {

  console.log('Item', props.item)

  if (props.item) {

    return (
      <>
        <div className='border' style={{height: "50%", width: "95%", padding: "10px"}}>
            <div style={{color: "white", fontSize: "22px"}}>
                {props.item.name}
            </div>

            <div className='align-image-center'>
              <img src={props.item.url} alt={props.item.name}/>
            </div>
            <div style={{color: "white", fontSize: "20px"}}>
                {props.item.url}
            </div>
        </div>
      </>
    )
  };

  return <div></div>;
}