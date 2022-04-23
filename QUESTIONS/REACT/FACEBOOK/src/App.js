
// $ npm install react-bootstrap bootstrap

import React from 'react';

import './App.css';

import 'h8k-components';

import Navbar from './components/Navbar'

import Layout from './components/index.js';

//import NavbarContainer from './components/NavbarContainer'

function App() {
  return (
    <div>
      <Navbar/>
      <Layout/>
    </div>
  );
}

export default App;
