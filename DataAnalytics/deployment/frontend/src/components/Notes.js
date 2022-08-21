import { useEffect } from 'react'

import { connect, useSelector } from 'react-redux'

import { useNavigate } from 'react-router-dom'

import { toggleImportanceOf } from '../reducers/noteReducer'

const Note = (props) => {
  return(
    <tr>
        <td>{props.note.id}</td>
        <td>{props.note.bill_no}</td>
        <td>{props.note.company_id}</td>
        <td>{props.note.ship_id}</td>
        <td>{props.note.sp_no}</td>
        <td>{props.note.TotalAmount}</td>
        <td>{props.note.BillDate}</td>
    </tr>
  )
}

const Notes = (props) => {

  const state = useSelector(state => state)

  const navigate = useNavigate()

  useEffect(() => {

    console.log('state.user', state.user)

    if (state.user === null) {
      navigate('/login')
    }

  },[])

  return(
    <div style={{padding:"2vh"}}>
      <table>
        <tbody>
            <tr>
              <th>id</th>
              <th>bill_no</th>
              <th>company_id</th>
              <th>ship_id</th>
              <th>sp_no</th>
              <th>total_amount</th>
              <th>bill_date</th>
            </tr>
          {props.notes.map(note =>
            <Note key={note.id} note={note} />
          )}
        </tbody>
      </table>
    </div>
  )
}

const mapStateToProps = (state) => {
  if ( state.filter === 'ALL' ) {
    return {
      notes: state.notes
    }
  }
  return {
    notes: (state.filter  === 'IMPORTANT' 
      ? state.notes.filter(note => note.important)
      : state.notes.filter(note => !note.important)
    )
  }
}

const mapDispatchToProps = {
  toggleImportanceOf,
}

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(Notes)