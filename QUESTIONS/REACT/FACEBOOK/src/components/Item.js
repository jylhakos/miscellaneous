import React from 'react';

import './item.css';

export default function Item(props) {

  console.log('Item', props.item)

  if (props.item) {

    return (
      <>
        <div className='border' style={{display: "inline", height: "50vh", width: "70vw", padding: "10px", position: "relative"}}>
            <div style={{color: "white", fontSize: "24px"}} >
                {props.item.name.first} {props.item.name.last}
            </div>

            <div className='align-image-center'>
              <img src={props.item.picture} alt={props.item.name.first}/>
            </div>
            <div style={{color: "white", fontSize: "20px", position: "absolute", bottom: "0"}}>
                {props.item.email}
            </div>
        </div>
      </>
    )
  };

  return <div></div>;
}