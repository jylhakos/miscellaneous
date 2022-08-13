import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useDispatch } from 'react-redux'
import { Button } from '@mui/material'
import { initializeNotes } from '../reducers/noteReducer'
import loginService from '../services/login'
import { setUser } from '../reducers/userReducer'

const Login = (props) => {

  const [username, setUsername] = useState('')
  
  const [password, setPassword] = useState('')

  const navigate = useNavigate()

  const dispatch = useDispatch()

  const login = async () => {

    console.log('login', username, password)

    await loginService.login(username, password)

    dispatch(setUser(username))

    dispatch(initializeNotes())

    navigate("/charts")
  }

  const onSubmit = (event) => {

    event.preventDefault()

    console.log('onSubmit')

    login()
  }

  return (
    <div>
      <h2>Login</h2>
      <form onSubmit={onSubmit}>
        <div>
          Username: <input value={username} onChange={(e) => setUsername(e.target.value)}/>
        </div>
        <div style={{paddingTop:"1vh"}}>
          Password: <input type='password' value={password} onChange={(e) => setPassword(e.target.value)}/>
        </div>
        <div style={{paddingTop:"1vh"}}>
          <Button type="submit" variant="contained">login</Button>
        </div>
      </form>
    </div>
  )
}

export default Login