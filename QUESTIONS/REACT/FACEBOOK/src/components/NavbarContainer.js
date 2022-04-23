import React from 'react';

import { Navbar, Container } from 'react-bootstrap'

import 'bootstrap/dist/css/bootstrap.min.css';

import logo from '../assets/google.png';

const title = "Layout";

export default function NavbarContainer() {
  return (
    <>
      <Navbar bg="light" variant="light">
        <Container>
          <Navbar.Brand href="">
            <img
              alt=""
              src={logo}
              width="30"
              height="30"
              className="d-inline-block align-top"
            />
          {title}
          </Navbar.Brand>
        </Container>
      </Navbar>
    </>
  );
}
