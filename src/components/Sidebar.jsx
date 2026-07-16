import React, { useState } from 'react';
import { Plus, Upload, FileText, Database, RefreshCw, CheckCircle, AlertCircle } from 'lucide-react';


export default function Sidebar({
  onNewChat,
  health,
  sources,
  isIngesting,
  onTriggerIngest,
  onUploadFile,
  uploadStatus
}) {
  const [uploading, setUploading] = useState(false);


  const handleFileChange = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;


    setUploading(true);
    await onUploadFile(file);
    setUploading(false);
    e.target.value = '';
  };


  return (
    <aside className="sidebar">
      {/* + New chat button */}
      <button className="new-chat-btn" onClick={onNewChat}>
        <span style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <Plus size={16} />
          New chat
        </span>
      </button>


      <div className="sidebar-scroll">
        {/* Document Upload Area */}
        <div>
          <div className="section-label">Knowledge Base Upload</div>
          <div className="upload-dropzone">
            <input
              type="file"
              accept=".pdf,.docx,.txt,.md"
              className="file-input"
              onChange={handleFileChange}
              disabled={uploading}
            />
            <Upload size={18} color="var(--text-secondary)" style={{ margin: '0 auto 6px' }} />
            <div style={{ fontSize: '0.82rem', fontWeight: 500 }}>
              {uploading ? 'Parsing & Indexing...' : 'Upload PDF / DOCX'}
            </div>
            <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '2px' }}>
              Indexed automatically into vector store
            </div>
          </div>


          {uploadStatus && (
            <div
              style={{
                marginTop: '8px',
                padding: '6px 8px',
                borderRadius: '6px',
                fontSize: '0.75rem',
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                backgroundColor: uploadStatus.type === 'success' ? 'rgba(16, 185, 129, 0.12)' : 'rgba(239, 68, 68, 0.12)',
                color: uploadStatus.type === 'success' ? '#10b981' : '#ef4444'
              }}
            >
              {uploadStatus.type === 'success' ? <CheckCircle size={13} /> : <AlertCircle size={13} />}
              <span>{uploadStatus.text}</span>
            </div>
          )}
        </div>


        {/* Indexed Documents List */}
        <div>
          <div className="section-label" style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span>Indexed Files ({sources.length})</span>
            <span>{health?.chroma_db_indexed_chunks || 0} chunks</span>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
            {sources.length === 0 ? (
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', padding: '4px 8px' }}>
                No documents indexed.
              </div>
            ) : (
              sources.map((src, idx) => (
                <div
                  key={idx}
                  style={{
                    padding: '7px 10px',
                    borderRadius: '6px',
                    fontSize: '0.8rem',
                    color: 'var(--text-secondary)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between'
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', overflow: 'hidden' }}>
                    <FileText size={14} />
                    <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {src.filename}
                    </span>
                  </div>
                  <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                    {src.chunks_count}
                  </span>
                </div>
              ))
            )}
          </div>
        </div>
      </div>


      <div className="sidebar-footer">
        <button
          className="btn-subtle"
          onClick={onTriggerIngest}
          disabled={isIngesting}
        >
          <RefreshCw size={14} />
          {isIngesting ? 'Syncing...' : 'Sync S3 / Staging Files'}
        </button>
      </div>
    </aside>
  );
}


