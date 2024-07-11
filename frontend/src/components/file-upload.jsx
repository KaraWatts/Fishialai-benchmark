import { useState } from 'react';
import axios from 'axios';

export default function Upload() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [data, setData] = useState([]);
  const [selectedData, setSelectedData] = useState("");

  const handleFileChange = (event) => {
    setSelectedFile(event.target.files[0]);
  };

  const handleItemClick = (fileName) => {
    setSelectedData(fileName);
  };

  const handleFileUpload = async () => {
    if (!selectedFile) {
      alert('Please select a file first');
      return;
    }

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const reponse = await axios.post('http://localhost:8080/upload_test_data', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      const responseData = reponse.data
      setData([...data, responseData.filename])
      alert('File uploaded successfully!');
    } catch (error) {
      alert('Failed to upload file');
      console.error('Error:', error);
    }
  };

  return (
    <div className='datasetList'>
      <h1>Upload COCO File</h1>
      <input type="file" accept=".json" onChange={handleFileChange} />
      <button onClick={handleFileUpload}>Upload</button>
      <h3>Select Dataset to Run Tests</h3>
      {data ? 
          <ul>
            {data.map((fileName, index) => (
              <li key={index}>
              <button onClick={() => handleItemClick(fileName)}>
              {fileName}
              </button>
              </li>
            ))}
          </ul> : 
          <p>No files uploaded yet</p>
      }
      <p>{selectedData}</p>
    </div>
  );
}