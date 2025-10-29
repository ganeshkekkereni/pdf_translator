import React, { useState } from 'react';
import axios from 'axios';
import './App.css';  // Optional for styling

function App() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [downloadUrl, setDownloadUrl] = useState('');

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setError('');
    setDownloadUrl('');
  };

  const handleSubmit = async () => {
    if (!file) {
      setError('Please select a PDF file.');
      return;
    }
    if (!file.name.endsWith('.pdf')) {
      setError('File must be a PDF.');
      return;
    }

    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('http://localhost:5000/translate', formData, {
        responseType: 'blob',
      });
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      setDownloadUrl(url);
    } catch (err) {
      setError('Error during translation: ' + (err.response?.data?.error || err.message));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Spanish PDF to English Translator</h1>
        <input type="file" accept=".pdf" onChange={handleFileChange} />
        <button onClick={handleSubmit} disabled={loading}>
          {loading ? 'Translating...' : 'Upload and Translate'}
        </button>
        {error && <p style={{ color: 'red' }}>{error}</p>}
        {downloadUrl && (
          <a href={downloadUrl} download="translated.pdf">
            Download Translated PDF
          </a>
        )}
      </header>
    </div>
  );
}

export default App;