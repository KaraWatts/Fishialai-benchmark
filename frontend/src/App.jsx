import { useState, useEffect } from 'react'
import './App.css'
import axios from 'axios'
import { Upload } from './components/file-upload'


function App() {
  const fetchAPI = async () => {
    const response = await axios.get("http://locoalhost/api/")
    print(response.data)
  }

  useEffect(() => {
    fetchAPI()
  }, [])

    return (
      <div className="App">
        <Upload/>
      </div>
    );
  }
  
  export default App;
  
