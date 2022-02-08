import './App.css';
import Plot from 'react-plotly.js';
import { useEffect, useState } from 'react';

function App() {

  const fakeData = [
    {
      "count": 11, 
      "sentiment": 0.009956709956709957, 
      "symbol": "FB"
    }, 
    {
      "count": 6, 
      "sentiment": 0.12797619047619047, 
      "symbol": "OP"
    }, 
    {
      "count": 5, 
      "sentiment": 0.2, 
      "symbol": "TSLA"
    }, 
    {
      "count": 5, 
      "sentiment": 0.15714285714285714, 
      "symbol": "AMZN"
    }, 
    {
      "count": 4, 
      "sentiment": 0.3416666666666667, 
      "symbol": "TRUE"
    }, 
    {
      "count": 4, 
      "sentiment": 0.25773809523809527, 
      "symbol": "BABA"
    }, 
    {
      "count": 4, 
      "sentiment": 0.22454545454545455, 
      "symbol": "PTON"
    }, 
    {
      "count": 4, 
      "sentiment": 0.22321428571428573, 
      "symbol": "DD"
    }, 
    {
      "count": 4, 
      "sentiment": 0.19739583333333333, 
      "symbol": "WOW"
    }, 
    {
      "count": 4, 
      "sentiment": 0.003125, 
      "symbol": "WELL"
    }
  ]

  const [mentions, setMentions] = useState([])

  useEffect(() => {
    getMentions();
    setInterval(() => {
      getMentions();
    }, 5000);
  }, [])

  const getMentions = () => {
    console.log("Getting mentions...")
    fetch("http://localhost:5000/api/mentions").then(response => {
      if (response.ok) {
        return response.json()
      }
      throw response
    }).then(data => {
      setMentions(data)
    })
  }



  return (
    <div className='App'>
      <Plot
          data={[
            {
              type: 'bar',
              x: mentions.map(d => d.symbol),
              y: mentions.map(d => d.count),
            },
          ]}
          layout={ {title: 'WSB Top 10'} }
      />
    </div>
  );
}

export default App;
