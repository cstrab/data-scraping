import './App.css';
import Plot from 'react-plotly.js';
import { useEffect, useState } from 'react';
import { environment } from './environment';

function App() {

  const DEFAULT_TIME_RANGE = 30
  const DEFAULT_LIMIT = 10
  const DEFAULT_COMMENT = ''

  const time_range_options = [
    {name: "5 Minutes", value: 5},
    {name: "15 Minutes", value: 15},
    {name: "30 Minutes", value: 30},
    {name: "1 Hour", value: 60},
    {name: "12 Hours", value: 60 * 12},
    {name: "1 Day", value: 60 * 24},
    {name: "1 Week", value: 60 * 24 * 7},
  ]

  const limit_options = [
    {name: "Top 5", value: 5},
    {name: "Top 10", value: 10},
    {name: "Top 25", value: 25},
  ]

  const [mentions, setMentions] = useState([])
  const [isRefreshing, setIsRefreshing] = useState(false)
  const [refreshTime, setRefreshTime] = useState('Never')
  const [minutes, setMinutes] = useState(DEFAULT_TIME_RANGE)
  const [limit, setLimit] = useState(DEFAULT_LIMIT)

  const [symbol, setSymbol] = useState(DEFAULT_COMMENT)
  const [comments, setComments] = useState([])
  const [liveComments, setLiveComments] = useState(false)

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

  useEffect(() => {
    const getComments = () => {
      if (!symbol) { return }
      console.log(`Getting comments for ${symbol}...`)
      // setIsRefreshing(true)
      fetch(`${environment.REACT_APP_API_URL}/symbols/${symbol}/comments?minutes=${minutes}`)
      .then(response => {
        if (response.ok) {
          return response.json()
        }
        throw response
      }).then(data => {
        console.log("Got comments:", data)
        setComments(data)
        // setRefreshTime(new Date().toLocaleTimeString())
      })
      // .finally(() => setIsRefreshing(false))
    }

    getComments();
    if (liveComments) {
      const interval = setInterval(() => {
        getComments();
      }, 5000)
  
      return () => {
        clearInterval(interval)
      };
    }
  }, [symbol, minutes, liveComments])

  const scaleValue = (x, a, b, min, max) => {
    const scaled = ((b-a)*(x-min))/(max-min) + a
    return scaled
  }

  const onTimeRangeChanged = (e) => {
    console.log('onTimeRangeChanged')
    const value = Number(e.target.value)
    setMinutes(value)
    
  }

  const onLimitChanged = (e) => {
    console.log('onLimitChanged')
    const value = Number(e.target.value)
    setLimit(value)
  }

  const onSymbolChanged = (e) => {
    console.log('onSymbolChanged')
    const value = e.target.value
    setSymbol(value)
  }

  const onLiveCommentsChanged = (e) => {
    console.log('onLiveCommentsChanged')
    const value = e.target.checked
    setLiveComments(value)
  }

  return (
    <div className='App'>
      {!isRefreshing && <p>Last Refreshed: {refreshTime}</p>}
      {isRefreshing && <p>Refreshing...</p>}
      <div>
        <p>Time Range:</p>
        <select defaultValue={DEFAULT_TIME_RANGE} onChange={onTimeRangeChanged}>
          {time_range_options.map((o, i) => <option key={`time-${i}`} value={o.value}>{o.name}</option>)}
        </select>
        <p>Limit:</p>
        <select defaultValue={DEFAULT_LIMIT} onChange={onLimitChanged}>
          {limit_options.map((o, i) => <option key={`limit-${i}`} value={o.value}>{o.name}</option>)}
        </select>
      </div>
      
      <div>
        <Plot
            data={[
              {
                type: 'bar',
                x: mentions.map(m => m.symbol),
                y: mentions.map(m => m.count),
                marker: {
                  color: mentions.map(m => {
                    return `RGB(${scaleValue(m.sentiment, 0, 255, 1, -1)}, 0, ${scaleValue(m.sentiment, 0, 255, -1, 1)})`
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
            useResizeHandler = {true}
            style = {{width: "100%", height: "100%"}}
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
                    return `RGB(${scaleValue(m.sentiment, 0, 255, 1, -1)}, 0, ${scaleValue(m.sentiment, 0, 255, -1, 1)})`
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
            useResizeHandler = {true}
            style = {{width: "100%", height: "100%"}}
        />
        {mentions.length > 0 &&
        <>
          <p>Symbol:</p>
          <select defaultValue={symbol} onChange={onSymbolChanged}>
            <option value={symbol}>{symbol || 'Select'}</option>
            {mentions.map(m => ({value: m.symbol, name: m.symbol})).filter(o => o.value !== symbol).map((o, i) => <option key={`symbol-${o.value}`} value={o.value}>{o.name}</option>)}
          </select>
        </>
        }
        { symbol && comments.length > 0 &&
        <>
          <p>Live Comments:</p>
          <input type={"checkbox"} value={liveComments} onChange={onLiveCommentsChanged}/>
          { comments.map(c => <div key={`comment${c.id}`}>
            <p><b>{c.author}</b> at {new Date(c.created*1000).toLocaleTimeString()} on {new Date(c.created*1000).toLocaleDateString()}</p>
            <p><i>{c.sentiment.toFixed(2)}</i></p>
            <p>{c.body}</p>
          </div>)}
        </>
        }
      </div>
    </div>
  );
}

export default App;
