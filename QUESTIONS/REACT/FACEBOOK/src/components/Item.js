import React from 'react';

import './item.css';

export default function Item(props) {

  console.log('Item', props.item)

  if (props.item) {

    return (
      <>
        <div className='border' style={{height: "50%", width: "95%", padding: "10px"}}>
            <div style={{color: "white", fontSize: "22px"}}>
                {props.item.name.first} {props.item.name.last}
            </div>

            <div className='align-image-center'>
              <img src={props.item.picture} alt={props.item.name.first}/>
            </div>
            <div style={{color: "white", fontSize: "20px"}}>
                {props.item.email}
            </div>
        </div>
      </>
    )
  };

  return <div></div>;
}