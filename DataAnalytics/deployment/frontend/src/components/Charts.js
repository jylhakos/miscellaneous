import { useEffect } from 'react'

import { useSelector } from 'react-redux'

import { useNavigate } from 'react-router-dom'

import { Bar } from 'react-chartjs-2'

import { getNotes } from '../reducers/noteReducer'

//import { setUser } from '../reducers/userReducer'

import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js'

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
)

const Charts = () => {

	const state = useSelector(state => state)

	const navigate = useNavigate()

  useEffect(() => {

    console.log('state.user', state.user)

    if (state.user === null) {
      navigate('/login')
    }

  },[])

	const labels = []

	const tmp_labels = []

	const values = []

	const tmp_values = []

	/*
	for (let i = 0; i < state.notes.length; i++) {

  	labels.push(state.notes[i].ship_id)

  	values.push(state.notes[i].TotalAmount)

  	console.log(i, labels[i], values[i])
  }
  */

  for (let i = 0; i < state.notes.length; i++) {

  	tmp_labels.push(state.notes[i].ship_id)

  	tmp_values.push(parseInt(state.notes[i].TotalAmount))

  	//console.log(i, tmp_labels[i], tmp_values[i])
  }

  for (let i = 0; i < tmp_labels.length; i++) {

  		let tmp = tmp_values[i]

  		for (let j = i+1; j < tmp_labels.length; j++) {

  			if(tmp_labels[j] != null) {
	  			if (tmp_labels[i] == tmp_labels[j]) {
	  				tmp = tmp + tmp_values[j]
	  				tmp_labels[j] = null
	  			}
  			}

	    	
    	}

    	if(tmp_labels[i] != null) {

    		labels.push(tmp_labels[i])

	    	values.push(tmp)
	    }

	    //console.log(i, labels[i], values[i])
  }
	
	const data = {
		labels,
		datasets: [{
			label: 'Data',
			data: values,
			//backgroundColor: 'rgba(255, 99, 132, 0.5)',
			//backgroundColor: 'rgba(53, 162, 235, 0.5)'
			backgroundColor: 'rgba(144, 238, 144, 0.5)'
		}]
	}

	//console.log(data)

	return(<div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '75vh', margin: '5vh' }}><Bar data={data} options={{ responsive: true, maintainAspectRatio: false }} /></div>)
}

export default Charts