import './App.css';
import Plot from 'react-plotly.js';
import { useEffect, useState } from 'react';
import { environment } from './environment';

function App() {

  const [mentions, setMentions] = useState([])
  const [isRefreshing, setIsRefreshing] = useState(false)
  const [refreshTime, setRefreshTime] = useState('Never')
  const [minutes, setMinutes] = useState(30)
  const [limit, setLimit] = useState(10)

  useEffect(() => {
    const getMentions = () => {
      console.log("Getting mentions...")
      setIsRefreshing(true)
      fetch(`${environment.REACT_APP_API_URL}/mentions?minutes=${minutes}&limit=${limit}`)
      .then(response => {
        if (response.ok) {
          return response.json()
        }
        throw response
      }).then(data => {
        console.log("Got mentions:", data)
        setMentions(data)
        setRefreshTime(new Date().toLocaleTimeString())
      }).finally(() => setIsRefreshing(false))
    }

    getMentions();
    const interval = setInterval(() => {
      getMentions();
    }, 5000)

    return () => clearInterval(interval);
  }, [limit, minutes])

  const scaleValue = (x, a, b, min, max) => {
    const scaled = ((b-a)*(x-min))/(max-min) + a
    return scaled
  }

  const onTimeRangeChanged = (e) => {
    const value = Number(e.target.value)
    setMinutes(value)
    
  }

  const onLimitChanged = (e) => {
    const value = Number(e.target.value)
    setLimit(value)
  }

  return (
    <div className='App'>
      {!isRefreshing && <p>Last Refreshed: {refreshTime}</p>}
      {isRefreshing && <p>Refreshing...</p>}
      <div>
        <p>Time Range:</p>
        <select onChange={onTimeRangeChanged}>
          <option value="60">60 minutes</option>
          <option value="30" selected>30 minutes</option>
          <option value="15">15 minutes</option>
          <option value="5">5 minutes</option>
        </select>
        <p>Limit:</p>
        <select onChange={onLimitChanged}>
          <option value="5">Top 5</option>
          <option value="10" selected>Top 10</option>
          <option value="25">Top 25</option>
        </select>
      </div>
      
      <Plot
          data={[
            {
              type: 'bar',
              x: mentions.map(m => m.symbol),
              y: mentions.map(m => m.count),
              marker: {
                color: mentions.map(m => {
                  return `RGB(${scaleValue(m.sentiment, 0, 255, 1, -1)}, ${scaleValue(m.sentiment, 0, 255, -1, 1)}, 0 )`
                }),
                // size: mentions.map(m => scaleValue(m.count, 1, 2, -1, 1)),
              }
            },
          ]}
          layout={{
            title: `WSB Top ${limit}`,
            xaxis: { 
              title: 'Symbol'
            },
            yaxis: { 
              title: 'Mentions'
            },
          }}
      />
      <Plot
          data={[
            {
              type: 'scatter',
              mode: 'markers',
              x: mentions.map(m => m.sentiment),
              y: mentions.map(m => m.count),
              hovertext: mentions.map(m => m.symbol),
              marker: {
                color: mentions.map(m => {
                  return `RGB(${scaleValue(m.sentiment, 0, 255, 1, -1)}, ${scaleValue(m.sentiment, 0, 255, -1, 1)}, 0 )`
                }),
                // size: mentions.map(m => scaleValue(m.count, 1, 2, -1, 1)),
              }
            },
          ]}
          layout={{
            title: `WSB Top ${limit}`,
            xaxis: { 
              title: 'Sentiment',
              range: [-1, 1] 
            },
            yaxis: { 
              title: 'Mentions'
            },
          }}
      />
    </div>
  );
}

export default App;
