import { useState, useEffect } from 'react'
import './App.css'
import axios from 'axios'
import Upload from './components/file-upload.jsx'
import RunTest from './components/run-test.jsx'


function App() {
  const fetchAPI = async () => {
    const response = await axios.get("http://127.0.0.1:8080/test")
    console.log(response.data)
  }

  useEffect(() => {
    fetchAPI()
  }, [])

    return (
      <div className="App">
        <Upload/>
        <RunTest/>
      </div>
    );
  }
  
  export default App;
  
