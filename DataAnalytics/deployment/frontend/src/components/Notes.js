import { toggleImportanceOf } from '../reducers/noteReducer'
import { connect } from 'react-redux'

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