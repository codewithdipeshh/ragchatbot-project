import React from 'react';


export default function Navbar({ health }) {
  return (
    <header className="chat-topbar">
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <span style={{ fontWeight: 600, color: 'var(--text-primary)' }}>Enterprise RAG</span>
        <span style={{ color: 'var(--text-muted)' }}>/</span>
        <span>{health?.groq_model || 'Llama 3.3 70B'}</span>
      </div>


      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
        <span style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', fontSize: '0.78rem', color: '#10b981' }}>
          <span style={{ width: '6px', height: '6px', borderRadius: '50%', backgroundColor: '#10b981' }}></span>
          Ready
        </span>
      </div>
    </header>
  );
}
