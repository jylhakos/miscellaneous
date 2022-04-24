import React from 'react';

import logo from '../assets/google.png';

import './navbar.css';

const title = "Facebook";

export default function Navbar() {
	return (
    <>
    <div className='navbar_header' style={{height: "10px", width: "100%"}}>
	    <div className='styles.navbar_title'>
	      <img src={logo} alt={title} style={{height: "20%", width: "20%", padding: "2px"}}/>
	    </div>
	    <div className='styles.navbar_text' style={{color: "white", paddingRight: "45%", fontWeight: "800", fontSize: "28px"}}>
	        {title}
	    </div>
    </div>
    </>
  );
}
