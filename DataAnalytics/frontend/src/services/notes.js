import axios from 'axios'

//const baseUrl = 'http://localhost:3001/data'

const baseUrl = 'http://localhost:8001/api/sql/bill_head'

axios.defaults.withCredentials = true

const httpClient = axios.create({
  baseURL: 'http://localhost:8001',
  //timeout: 6000,
  withCredentials: true,
  //headers: {
  //  "Access-Control-Allow-Headers": "Access-Control-Allow-Headers, Origin,Accept, X-Requested-With, Content-Type, Access-Control-Request-Method, Access-Control-Request-Headers",
  //}
})

/*
const config = {
  headers: {
    Authorization: `Bearer ${token}`,
  },
}
*/

const getAll = async () => {
  const options = {
        method: 'get',
        url: '/api/sql/bill_head'
    }
  //const response = await axios.get(baseUrl, config)
  //const response = await axios.get(baseUrl, { useCredentails: true })
  const response = await httpClient(options)

  return response.data
}

const createNew = async (content) => {
  const object = { content, important: false }
  const response = await axios.post(baseUrl, object)
  return response.data
}

export default {
  getAll,
  createNew
}