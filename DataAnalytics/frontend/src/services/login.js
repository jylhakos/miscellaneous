import axios from 'axios'

const url = 'http://localhost:8001'

axios.defaults.withCredentials = true

const httpClient = axios.create({
  baseURL: url,
  withCredentials: true,
})

const login = async (username, password) => {

  console.log('login', username, password)

  const data = {"username": username, "password": password}

  const options = {
    method: 'post',
    url: '/api/user/login',
    data: data
  }

  const response = await httpClient(options)

  console.log('response', response)

  return response
}

export default {
  login
}