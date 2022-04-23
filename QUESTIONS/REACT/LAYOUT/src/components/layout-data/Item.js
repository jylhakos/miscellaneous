import React from "react";

import "./index.css";

export default function Item(props) {

  console.log('Item', props.item)

  if (props.item) {

    return (
      <>
        <div style={{height: "75%", width: "75%", paddingLeft: "10px", paddingRight: "5px"}}>
            <div>
                {props.item.name}
            </div>

            <div style={{padding: '5px'}}>
              <img src={props.item.url} alt={props.item.name}/>
            </div>
            <div>
                {props.item.url}
            </div>
        </div>
      </>
    )
  };

  return <div></div>;
}