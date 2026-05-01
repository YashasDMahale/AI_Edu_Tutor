import { useState, useRef } from 'react';
import axios from 'axios';
import { UploadCloud, FileText, Image as ImageIcon, FileAudio, CheckCircle, AlertCircle } from 'lucide-react';

export default function UploadPanel({ onUploadSuccess }) {
  const [file, setFile] = useState(null);
  const [fileType, setFileType] = useState('pdf');
  const [isUploading, setIsUploading] = useState(false);
  const [status, setStatus] = useState(null); // 'success', 'error'
  const fileInputRef = useRef(null);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setStatus(null);
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);
    formData.append('file_type', fileType);

    setIsUploading(true);
    setStatus(null);

    try {
      const url = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const response = await axios.post(`${url}/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      setStatus('success');
      onUploadSuccess(response.data);
      setFile(null);
      if (fileInputRef.current) fileInputRef.current.value = "";
    } catch (error) {
      console.error(error);
      setStatus('error');
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="panel upload-panel glass-effect">
      <h2>Upload Knowledge Base</h2>
      <p className="helper-text">Add your course material here.</p>

      <div className="type-selector">
        <button 
          className={`type-btn ${fileType === 'pdf' ? 'active' : ''}`}
          onClick={() => setFileType('pdf')}
        ><FileText size={16}/> PDF</button>
        <button 
          className={`type-btn ${fileType === 'image' ? 'active' : ''}`}
          onClick={() => setFileType('image')}
        ><ImageIcon size={16}/> Image</button>
        <button 
          className={`type-btn ${fileType === 'audio' ? 'active' : ''}`}
          onClick={() => setFileType('audio')}
        ><FileAudio size={16}/> Audio</button>
      </div>

      <div 
        className={`drop-zone ${file ? 'has-file' : ''}`}
        onClick={() => fileInputRef.current.click()}
      >
        <UploadCloud size={48} className="upload-icon" />
        {file ? (
          <p className="file-name">{file.name}</p>
        ) : (
          <p>Drag & drop or <span>click to browse</span></p>
        )}
        <input 
          type="file" 
          ref={fileInputRef} 
          style={{ display: 'none' }} 
          onChange={handleFileChange}
          accept={fileType === 'pdf' ? '.pdf' : fileType === 'image' ? 'image/*': 'audio/*'}
        />
      </div>

      <button 
        className="btn-primary upload-btn" 
        onClick={handleUpload} 
        disabled={!file || isUploading}
      >
        {isUploading ? 'Processing and Indexing...' : 'Upload & Process'}
      </button>

      {status === 'success' && (
        <div className="status-msg success">
          <CheckCircle size={16}/> Uploaded and indexed successfully!
        </div>
      )}
      {status === 'error' && (
        <div className="status-msg error">
          <AlertCircle size={16}/> Failed to upload file.
        </div>
      )}
    </div>
  );
}
