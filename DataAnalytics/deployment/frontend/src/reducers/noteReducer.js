import { createSlice } from '@reduxjs/toolkit'
import noteService from '../services/notes'

const noteSlice = createSlice({
  name: 'notes',
  initialState: [],
  reducers: {
    toggleImportanceOf(state, action) {
      const id = action.payload
      const noteToChange = state.find(n => n.id === id)
      const changedNote = { 
        ...noteToChange, 
        important: !noteToChange.important 
      }
      return state.map(note =>
        note.id !== id ? note : changedNote 
      )     
    },
    appendNote(state, action) {
      state.push(action.payload)
    },
    setNotes(state, action) {
      console.log('setNotes', state, action)
      return action.payload
    }
  },
})

export const getNotes = () => {
  return async (dispatch) => {
    const notes = await noteService.getAll()
    console.log('getAll', notes.data)
    dispatch(setNotes(notes.data))
  }
}

export const createNote = (content) => {
  return async dispatch => {
    const newNote = await noteService.createNew(content)
    dispatch(appendNote(newNote))
  }
}

export const { toggleImportanceOf, appendNote, setNotes } = noteSlice.actions

export default noteSlice.reducer