import React from 'react';
import { FileText } from 'lucide-react';


export default function CitationCard({ citation }) {
  return (
    <div className="citation-card">
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px' }}>
        <span style={{ fontWeight: 500, color: 'var(--accent-blue)', display: 'flex', alignItems: 'center', gap: '6px' }}>
          <FileText size={13} />
          {citation.source}
        </span>
        <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
          Chunk #{citation.chunk_index} ({citation.similarity}% match)
        </span>
      </div>
      <div style={{ color: 'var(--text-secondary)', lineHeight: 1.5, fontSize: '0.81rem' }}>
        &ldquo;{citation.text}&rdquo;
      </div>
    </div>
  );
}


