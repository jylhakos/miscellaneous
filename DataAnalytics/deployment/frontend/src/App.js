import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import NavBar from './components/NavBar'
//import NewNote from './components/NewNote'
import Login from './components/Login'
//import Logout from './components/Logout'
import Notes from './components/Notes'
import Charts from './components/Charts'
//import VisibilityFilter from './components/VisibilityFilter'

const App = () => {

  return (
    <BrowserRouter>
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
    </BrowserRouter>
  )
}

export default App