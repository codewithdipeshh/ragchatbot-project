import React from 'react';
import CitationCard from './CitationCard';


export default function MessageList({ messages, loading, onSelectSuggestion }) {
  if (messages.length === 0) {
    return (
      <div className="messages-area">
        <div className="welcome-container">
          <h1 className="welcome-title">How can I help you today?</h1>
          <div className="suggestions-grid">
            <button
              className="suggestion-card"
              onClick={() => onSelectSuggestion('Tell me about NovaCloud security and zero-trust policies')}
            >
              <span style={{ fontWeight: 500, color: 'var(--text-primary)' }}>NovaCloud Security &amp; Zero-Trust</span>
              <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Check mTLS 1.3 and SOC 2 Type II controls</span>
            </button>


            <button
              className="suggestion-card"
              onClick={() => onSelectSuggestion('Summarize employee 401(k) matching and PTO leave policies')}
            >
              <span style={{ fontWeight: 500, color: 'var(--text-primary)' }}>401(k) &amp; Employee Benefits</span>
              <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Review dollar-for-dollar match and 24 days PTO</span>
            </button>


            <button
              className="suggestion-card"
              onClick={() => onSelectSuggestion('What are the AI Model Governance and PII scrubbing rules?')}
            >
              <span style={{ fontWeight: 500, color: 'var(--text-primary)' }}>AI Governance SOP</span>
              <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Inspect groundedness SLA &gt; 97.5%</span>
            </button>


            <button
              className="suggestion-card"
              onClick={() => onSelectSuggestion('What are the API rate limits and throttling response codes?')}
            >
              <span style={{ fontWeight: 500, color: 'var(--text-primary)' }}>API Rate Limits &amp; SLA</span>
              <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Check HTTP 429 and 99.99% uptime SLA</span>
            </button>
          </div>
        </div>
      </div>
    );
  }


  return (
    <div className="messages-area">
      <div className="messages-list">
        {messages.map((msg, idx) => (
          <div key={idx} className="message-row">
            <div className={`avatar ${msg.role === 'user' ? 'avatar-user' : 'avatar-ai'}`}>
              {msg.role === 'user' ? 'Y' : 'AI'}
            </div>


            <div className="message-body">
              <div className="message-author">
                {msg.role === 'user' ? 'You' : 'Enterprise RAG Assistant of '}
                {msg.latency_ms > 0 && (
                  <span style={{ fontWeight: 400, color: 'var(--text-muted)', marginLeft: '8px' }}>
                    {msg.latency_ms} ms
                  </span>
                )}
              </div>


              <div style={{ whiteSpace: 'pre-wrap' }}>{msg.content}</div>


              {msg.sources && msg.sources.length > 0 && (
                <div className="citations-box">
                  <div style={{ fontSize: '0.74rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase' }}>
                    Sources ({msg.sources.length})
                  </div>
                  {msg.sources.map((cit, cIdx) => (
                    <CitationCard key={cIdx} citation={cit} />
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}


        {loading && (
          <div className="message-row">
            <div className="avatar avatar-ai">AI</div>
            <div className="message-body" style={{ color: 'var(--text-secondary)' }}>
              Searching knowledge base &amp; synthesizing answer...
            </div>
          </div>
        )}
      </div>
    </div>
  );
}


