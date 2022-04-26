
// $ npm install react-bootstrap bootstrap

import React from 'react';

import './App.css';

import 'h8k-components';

import Navbar from './components/Navbar'

import Layout from './components/index.js';

//import NavbarContainer from './components/NavbarContainer'

function App() {

  const parameter = '5-January-2000'

  return (
    <div>
      <Navbar/>
      <Layout parameter={parameter}/>
    </div>
  );
}

export default App;
