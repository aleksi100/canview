import { useEffect, useState } from 'react'
import './App.css'

function App() {
  const [data, setData] = useState(null)
  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch("http://localhost:8000/data");
        const jsonData = await response.json();
        const dataArray = Object.keys(jsonData).map(key => jsonData[key])
        const sortedData = dataArray.sort((a, b) => b.time - a.time)
        setData(sortedData);
      } catch (error) {
        console.error("Virhe tiedon hakemisessa:", error);
      }
    }
    // Haetaan data heti komponentin latautuessa
    fetchData();
    const interval = setInterval(fetchData, 100);
    return () => clearInterval(interval);
  }, [])
  return (
    <>
      <table>
        <tbody>
          <tr>
            <th className='name'>Name</th>
            <th className='sa'>Address</th>
            <th className='pgn'>(n)PGN</th>
            <th className="data">Data</th>

          </tr>
          {data ? (
            data.map(frame => {
              return (
                <tr>
                  <td className='name'>?</td>
                  <td className='sa'>{frame.sa}</td>
                  <td className='pgn'>
                    <div className='flex'><p className='count'>({frame.count})</p>{frame.pgn}</div>
                  </td>
                  <td className="data">{frame.data}</td>
                </tr>


              )
            })
          ) : (
            <p>no data</p>

          )}
        </tbody>
      </table>
    </>
  )
}
export default App
