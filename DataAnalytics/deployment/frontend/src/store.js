import { configureStore } from '@reduxjs/toolkit'

import noteReducer from './reducers/noteReducer'

import filterReducer from './reducers/filterReducer'

import userReducer from './reducers/userReducer'

const store = configureStore({
  reducer: {
    notes: noteReducer,
    filter: filterReducer,
    user: userReducer
  }
})

export default store