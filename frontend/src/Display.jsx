
import { useEffect, useState } from 'react'
import './App.css'
function Display({ url }) {
  const [data, setData] = useState(null)
  useEffect(() => {
    const fetchData = async () => {

        try {

          const response = await fetch(url);
          let jsonData = await response.json();
          // const dataArray = jsonData.map(key => jsonData[key])
          const sortedData = jsonData.sort((a, b) => b.time - a.time)
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
      <div className='m-2 text-2xl'>

      <h2>To request name:</h2>
      <code>$cansend [can0/vcan0] 00eaff00#00ee00</code>
      </div>
        <table className='m-2'>
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
                  <tr key={frame.time}>
                    <td className='name'>{frame.name_id}</td>
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
export default Display
