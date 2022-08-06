import { useEffect, useState } from 'react'
import { BrowserRouter as Router, Routes, Route, Link, Navigate } from 'react-router-dom'
import NavBar from './components/NavBar'
//import NewNote from './components/NewNote'
import Login from './components/Login'
import Logout from './components/Logout'
import Notes from './components/Notes'
import Charts from './components/Charts'
import VisibilityFilter from './components/VisibilityFilter'
import { initializeNotes } from './reducers/noteReducer'
import { useDispatch } from 'react-redux'

const App = () => {

  /*
  const dispatch = useDispatch()

  useEffect(() => {

    dispatch(initializeNotes())

  },[dispatch])
  */

  return (
    <Router>
      <div>
        <NavBar />
          <Routes>
            <Route path="/" element={<Navigate to="/login" replace />} />
            <Route path="/charts" element={<Charts />} />
            <Route path="/sheets" element={<Notes />} />
            <Route path="/login" element={<Login />} />
            <Route path="/logout"/>
          </Routes>
      </div>
    </Router>
  )
}

export default App