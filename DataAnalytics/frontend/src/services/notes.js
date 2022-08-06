import axios from 'axios'

//const baseUrl = 'http://localhost:3001/data'

const baseUrl = 'http://localhost:8001/api/sql/bill_head'

const getAll = async () => {
  const response = await axios.get(baseUrl)
  return response.data
}

const createNew = async (content) => {
  const object = { content, important: false }
  const response = await axios.post(baseUrl, object)
  return response.data
}

export default {
  getAll,
  createNew,
}