import { useState } from 'react';
import axios from 'axios';
import '../stylesheets/test-runner.css';

export default function RunTest() {
  const [environment, setEnvironment] = useState("");
  const handleRunTest = async () => {
    if (!environment) {
      alert('Please select an environment first');
    }

    // import './TaskRunner.css'; // Create this CSS file for styling

    // const TaskRunner = ({ environment, image_id }) => {
    //   const [tasks, setTasks] = useState([
    //     { id: 1, name: 'Retrieve Token', status: 'pending' },
    //     { id: 2, name: 'Get Image URL', status: 'pending' },
    //     { id: 3, name: 'Upload Image', status: 'pending' },
    //   ]);
    
    //   const updateTaskStatus = (id, status) => {
    //     setTasks(prevTasks => 
    //       prevTasks.map(task => 
    //         task.id === id ? { ...task, status } : task
    //       )
    //     );
    //   };
    
    //   const runTasks = async () => {
    //     try {
    //       updateTaskStatus(1, 'running');
    //       const token = await axios.get(`http://localhost:8080/get_token/${environment}`);
    //       updateTaskStatus(1, 'success');
    
    //       updateTaskStatus(2, 'running');
    //       const imageURL = await axios.post(`http://localhost:8080/image_url/${environment}/${image_id}`);
    //       updateTaskStatus(2, 'success');
    
    //       updateTaskStatus(3, 'running');
    //       await axios.post(`http://localhost:8080/upload_image`, {
    //         'url': imageURL.data,
    //         'Content-Disposition': null,
    //         'Content_Md5': null,
    //         'Content-Type': null,
    //       });
    //       updateTaskStatus(3, 'success');
    
    //       alert('Tasks run successfully!');
    //     } catch (error) {
    //       alert('Failed to run tasks');
    //       console.error('Error:', error);
    //       // Update the task that failed
    //       setTasks(prevTasks =>
    //         prevTasks.map(task =>
    //           task.status === 'running' ? { ...task, status: 'failed' } : task
    //         )
    //       );
    //     }
    //   };
    
    //   return (
    //     <div>
    //       <ul>
    //         {tasks.map(task => (
    //           <li key={task.id} className={task.status}>
    //             {task.name} {task.status === 'success' && '✔'} {task.status === 'failed' && '✘'}
    //           </li>
    //         ))}
    //       </ul>
    //       <button onClick={runTasks}>Run Tasks</button>
    //     </div>
    //   );
    // };

  return (
    <div className="test-environment">
        <h3>Select your test environment</h3>
        <button onClick={() => setEnvironment("Production")}>Production</button>
        <button onClick={() => setEnvironment("Staging")}>Staging</button>
        <hr/>
        <button onClick={handleRunTest} disabled={(environment === "")}>Run Tests</button>
    </div>
  );
}