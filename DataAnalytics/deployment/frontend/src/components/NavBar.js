//import React, { useState } from 'react'
import React from 'react'
import { Link, useNavigate } from "react-router-dom"
import AppBar from '@mui/material/AppBar'
import Box from '@mui/material/Box'
import Toolbar from '@mui/material/Toolbar'
//import Typography from '@mui/material/Typography'
import Button from '@mui/material/Button'
import IconButton from '@mui/material/IconButton'
import MenuIcon from '@mui/icons-material/Menu'
import { useDispatch } from 'react-redux'
import { useSelector } from 'react-redux'
import { setUser } from '../reducers/userReducer'
import { setNotes } from '../reducers/noteReducer'

export default function NavBar() {

  const user = useSelector(state => state.user)

  const dispatch = useDispatch()

  const navigate = useNavigate()

  console.log('NavBar', user)

  const handleLogoutClick = () => {

    console.log('logout')

    dispatch(setUser(null))

    navigate("/login")

    dispatch(setNotes([]))
  }

  let button

  if (user) {

    button = <Button color="inherit" onClick={handleLogoutClick} >Logout</Button>

  } else {

      button = <Button color="inherit" component={Link} to="/login">Login</Button>
  }

  return (
    <Box sx={{ flexGrow: 1 }}>
      <AppBar position="static">
        <Toolbar>
          <IconButton
            size="large"
            edge="start"
            color="inherit"
            aria-label="menu"
            sx={{ mr: 2 }}
          >
          <MenuIcon />
          </IconButton>
          {user && <Button color="inherit" component={Link} to="/charts">Charts</Button>}
          {user && <Button color="inherit" component={Link} to="/sheets">Sheets</Button>}
          <Box sx={{ display: "flex", justifyContent: "flex-end", ml: 'auto' }}>
            {button}
          </Box>
        </Toolbar>
      </AppBar>
    </Box>
  )
}