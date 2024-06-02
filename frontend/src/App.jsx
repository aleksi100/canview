import { useEffect, useState } from 'react'
import './App.css'
import Display from "./Display.jsx"

const BackendUrlInput = ({ setUrl }) => {
  const handleKey = (e) => {
    if (e.key == "Enter") {
      setUrl(e.target.value)
    }
  }
  return (
    <div className="m-10">
      <label className="text-3xl mr-4" htmlFor="url_input">Backend url:</label>
      <input type="text" name='url_input'
        className="h-10 border w-4/6 text-2xl p-2"
        placeholder='Ex. http://localhost:8000/data'
        onKeyDown={handleKey} />
    </div>
  )
}
function App() {
  const [url, setUrl] = useState(null)
  return (
    <>
      {!url ? <BackendUrlInput setUrl={setUrl} /> : <Display url={url} />}
    </>
  )
}

export default App
