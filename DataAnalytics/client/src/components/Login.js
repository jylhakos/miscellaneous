import { useNavigate } from 'react-router-dom'
import { Button } from '@mui/material'

const Login = (props) => {

  const navigate = useNavigate()

  const onSubmit = (event) => {
    event.preventDefault()
    props.onLogin('anonymous')
    //console.log('onSubmit')
    navigate('/')
  }

  return (
    <div>
      <h2>Login</h2>
      <form onSubmit={onSubmit}>
        <div>
          Username: <input />
        </div>
        <div style={{paddingTop:"1vh"}}>
          Password: <input type='password' />
        </div>
        <div style={{paddingTop:"1vh"}}>
          <Button type="submit" variant="contained">login</Button>
        </div>
      </form>
    </div>
  )
}

export default Login