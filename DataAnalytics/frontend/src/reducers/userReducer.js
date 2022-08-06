
const userReducer = (state = null, action) => {

  if (action) {
    console.log('userReducer', state, action)
  }

  switch (action.type) {
    case 'SET_USER':
      console.log(action)
      return action.user
    default:
      console.log(state)
      return state
  }
}

export const setUser = (user) => {

  if (user) {
    console.log('setUser', user)
  }

  return {
    type: 'SET_USER',
    user,
  }
}

export default userReducer