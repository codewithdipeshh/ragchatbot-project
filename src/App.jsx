import React, { useState, useEffect, useRef } from 'react';
import { ArrowUp } from 'lucide-react';
import Navbar from './components/Navbar';
import Sidebar from './components/Sidebar';
import MessageList from './components/MessageList';


const API_BASE_URL = 'http://localhost:8000/api';


export default function App() {
  const [messages, setMessages] = useState([]);
  const [inputQuery, setInputQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [health, setHealth] = useState(null);
  const [sources, setSources] = useState([]);
  const [isIngesting, setIsIngesting] = useState(false);
  const [uploadStatus, setUploadStatus] = useState(null);


  const messagesEndRef = useRef(null);


  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };


  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);


  const fetchHealthAndSources = async () => {
    try {
      const hRes = await fetch(`${API_BASE_URL}/health`);
      if (hRes.ok) {
        const hData = await hRes.json();
        setHealth(hData);
      }
      const sRes = await fetch(`${API_BASE_URL}/sources`);
      if (sRes.ok) {
        const sData = await sRes.json();
        setSources(sData.indexed_sources || []);
      }
    } catch (err) {
      console.warn('Could not reach backend health/sources endpoints yet:', err);
    }
  };


  useEffect(() => {
    fetchHealthAndSources();
  }, []);


  const handleNewChat = () => {
    setMessages([]);
    setInputQuery('');
  };


  const handleUploadFile = async (file) => {
    setUploadStatus(null);
    const formData = new FormData();
    formData.append('file', file);


    try {
      const res = await fetch(`${API_BASE_URL}/upload`, {
        method: 'POST',
        body: formData,
      });


      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Upload failed');
      }


      const data = await res.json();
      setUploadStatus({
        type: 'success',
        text: `Indexed ${file.name} (${data.chunks_indexed} chunks)`
      });
      await fetchHealthAndSources();
    } catch (err) {
      setUploadStatus({
        type: 'error',
        text: err.message || 'Error extracting document'
      });
    }
  };


  const handleTriggerIngest = async () => {
    setIsIngesting(true);
    setUploadStatus(null);
    try {
      const res = await fetch(`${API_BASE_URL}/ingest`, { method: 'POST' });
      if (res.ok) {
        setUploadStatus({ type: 'success', text: 'Knowledge base synced successfully' });
        await fetchHealthAndSources();
      }
    } catch (err) {
      setUploadStatus({ type: 'error', text: 'Ingestion failed' });
    } finally {
      setIsIngesting(false);
    }
  };


  const handleSendQuery = async (queryText) => {
    const text = queryText || inputQuery;
    if (!text.trim() || loading) return;


    const userMessage = {
      role: 'user',
      content: text,
      latency_ms: 0,
      sources: []
    };


    setMessages((prev) => [...prev, userMessage]);
    setInputQuery('');
    setLoading(true);


    try {
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: text })
      });


      if (!response.ok) {
        throw new Error(`Server returned ${response.status}`);
      }


      const data = await response.json();
      const aiMessage = {
        role: 'ai',
        content: data.answer,
        latency_ms: data.latency_ms,
        sources: data.sources || []
      };


      setMessages((prev) => [...prev, aiMessage]);
    } catch (err) {
      const errorMessage = {
        role: 'ai',
        content: `Could not reach backend (${err.message}). Please ensure FastAPI server is running on port 8000.`,
        latency_ms: 0,
        sources: []
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };


  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendQuery();
    }
  };


  return (
    <div className="app-container">
      <Sidebar
        onNewChat={handleNewChat}
        health={health}
        sources={sources}
        isIngesting={isIngesting}
        onTriggerIngest={handleTriggerIngest}
        onUploadFile={handleUploadFile}
        uploadStatus={uploadStatus}
      />


      <main className="chat-main">
        <Navbar health={health} />


        <MessageList
          messages={messages}
          loading={loading}
          onSelectSuggestion={(text) => handleSendQuery(text)}
        />


        <div ref={messagesEndRef} />


        <div className="input-dock">
          <div className="input-wrapper">
            <input
              type="text"
              className="chat-input"
              placeholder="Ask Dipesh's Knowledge Hub..."
              value={inputQuery}
              onChange={(e) => setInputQuery(e.target.value)}
              onKeyDown={handleKeyDown}
            />
            <button
              className="send-btn"
              onClick={() => handleSendQuery()}
              disabled={!inputQuery.trim() || loading}
            >
              <ArrowUp size={16} strokeWidth={2.5} />
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}
