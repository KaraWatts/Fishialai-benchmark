import { useState } from 'react';
import axios from 'axios';

export default function RunTest() {
  const [environment, setEnvironment] = useState("");
  const [tasks, setTasks] = useState([
    { id: 1, name: 'Retrieve Token', status: 'pending' },
    { id: 2, name: 'Run image tests', status: 'pending' }
  ]);

  const updateTaskStatus = (id, status) => {
    setTasks(prevTasks =>
      prevTasks.map(task =>
        task.id === id ? { ...task, status } : task
      )
    );
  };

  const handleRunTest = async () => {
    if (!environment) {
      alert('Please select an environment first');
      return;
    }

    try {
      updateTaskStatus(1, 'running');
      const token = await axios.get(`http://localhost:8080/get_token/${environment}`);
      console.log(token.data);
      updateTaskStatus(1, 'success');

      updateTaskStatus(2, 'running');
      const imageURL = await axios.post(`http://localhost:8080/image_url/${environment}/8543`);
      console.log(imageURL.data);
      updateTaskStatus(2, 'success');


      alert('Tasks run successfully!');
    } catch (error) {
      alert('Failed to run tasks');
      console.error('Error:', error);
      // Update the task that failed
      setTasks(prevTasks =>
        prevTasks.map(task =>
          task.status === 'running' ? { ...task, status: 'failed' } : task
        )
      );
    }
  };

  return (
    <div className="test-environment">
      <h3>Select your test environment</h3>
      <button onClick={() => setEnvironment("production")}>Production</button>
      <button onClick={() => setEnvironment("stage")}>Staging</button>
      <hr />
      {environment !== "" && <ul>
        {tasks.map(task => (
          <li key={task.id} className={task.status}>
            {task.name} {task.status === 'success' && '✔'} {task.status === 'failed' && '✘'}
          </li>
        ))}
      </ul>}
      
      <button onClick={handleRunTest} disabled={environment === ""}>Run Test</button>
    </div>
  );
}