import axios from 'axios'

//require('dotenv').config()

//import HttpsProxyAgent from 'https-proxy-agent'

//const fs = require('fs');

//import * as fs from 'fs'

//const https = require('https')

//import https from 'https'

//const url = 'http://localhost:8001'

const url = 'https://192.168.9.97'

//const url = 'https://172.2.0.3'

//const url = 'http://localhost:8001'

axios.defaults.withCredentials = true

//const httpsAgent = new https.Agent({
//  rejectUnauthorized: false,
//  cert: fs.readFileSync('ssl.crt'),
//  key: fs.readFileSync('ssl.key'),
//})

const httpClient = axios.create({
  baseURL: url,
  withCredentials: true,
  //httpsAgent: httpsAgent
  //httpsAgent: new HttpsProxyAgent("https://192.168.9.97:443")
  //httpsAgent: new HttpsProxyAgent({
    //proxy: false,
    //protocol: 'https',
    //host: '192.168.9.97',
    //port: 443
  //})
})

const login = async (username, password) => {

  console.log('login', username, password)

  const data = {"username": username, "password": password}

  const options = {
    method: 'post',
    url: '/api/user/login',
    data: data
  }

  //console.log('process.env.REACT_APP_HTTPS_PROXY', process.env.REACT_APP_HTTPS_PROXY)

  let response = "login"

  try {

    const response = await httpClient(options)

  } catch (err) {

    if (err.response) {

        console.log('err.response', err.response)

    } else if (err.request) {

        console.log('err.request', err.request)

    } else {
        console.log('Error', err)
    }
  }

  console.log('response', response)

  return response
}

export default {
  login
}