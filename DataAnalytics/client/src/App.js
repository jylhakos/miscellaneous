import { useEffect, useState } from 'react'
import { BrowserRouter as Router, Routes, Route, Link, Navigate } from 'react-router-dom'
import NavBar from './components/NavBar'
//import NewNote from './components/NewNote'
import Login from './components/Login'
import Notes from './components/Notes'
import Graphs from './components/Graphs'
import VisibilityFilter from './components/VisibilityFilter'
import { initializeNotes } from './reducers/noteReducer'
import { useDispatch } from 'react-redux'

const App = () => {

  const [user, setUser] = useState(null) 

  const login = (user) => {
    setUser(user)
    console.log('login')
  }

  const dispatch = useDispatch()

  useEffect(() => {

    dispatch(initializeNotes())

  },[dispatch]) 

  return (
    <Router>
      <div>
        <NavBar />
          <Routes>
            <Route path="/" element={<Navigate to="/charts" replace />} />
            <Route path="/charts" element={<Graphs />} />
            <Route path="/sheets" element={<Notes />} />
            <Route path="/login" element={<Login onLogin={login} />} />
          </Routes>
      </div>
    </Router>
  )
}

export default App