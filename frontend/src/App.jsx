import { useState, useEffect } from 'react';
import './index.css';
import UploadPanel from './components/UploadPanel';
import ChatWindow from './components/ChatWindow';

function App() {
  const [lastUploaded, setLastUploaded] = useState(null);

  useEffect(() => {
    // Clear the Pinecone database on startup to start a fresh session
    fetch('http://localhost:8000/clear', {
      method: 'DELETE',
    })
      .then(res => res.json())
      .then(data => console.log('Database cleared:', data))
      .catch(err => console.error('Failed to clear database:', err));
  }, []);

  const handleUploadSuccess = (data) => {
    setLastUploaded(data);
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <div className="logo-section">
          <div className="logo-icon">🧠</div>
          <h1>Multi-Modal Smart Tutor</h1>
        </div>
        <p className="subtitle">Upload your coursework and ask questions to learn faster.</p>
      </header>
      
      <main className="main-content">
        <div className="upload-section">
          <UploadPanel onUploadSuccess={handleUploadSuccess} />
        </div>
        <div className="chat-section">
          <ChatWindow lastUploaded={lastUploaded} />
        </div>
      </main>
    </div>
  );
}

export default App;
