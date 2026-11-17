import React, { useState, useRef } from 'react'
import { Upload, X, FileText, CheckCircle, AlertCircle } from 'lucide-react'
import axios from 'axios'

const ACCEPTED = '.pdf,.txt,.docx,.csv,.md,.markdown'

export default function FileUpload({ onUploadSuccess }) {
  const [dragging, setDragging] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [status, setStatus] = useState(null) // { type: 'success'|'error', msg }
  const [file, setFile] = useState(null)
  const inputRef = useRef()

  const handleFile = (f) => {
    if (!f) return
    setFile(f)
    setStatus(null)
  }

  const handleUpload = async () => {
    if (!file) return
    setUploading(true)
    setStatus(null)

    const form = new FormData()
    form.append('file', file)
    form.append('collection_name', 'geetagpt')

    try {
      const { data } = await axios.post('/api/upload', form, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      setStatus({
        type: 'success',
        msg: `✓ "${data.filename}" ingested — ${data.chunks_created} chunks added`,
      })
      setFile(null)
      onUploadSuccess && onUploadSuccess(data)
    } catch (err) {
      setStatus({
        type: 'error',
        msg: err.response?.data?.detail || 'Upload failed. Please try again.',
      })
    } finally {
      setUploading(false)
    }
  }

  return (
    <div style={styles.wrapper}>
      {/* Drop Zone */}
      <div
        style={{
          ...styles.dropzone,
          borderColor: dragging ? 'var(--color-orange)' : 'var(--color-border)',
          background: dragging ? '#FFF7ED' : '#FFFFFF',
        }}
        onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
        onDragLeave={() => setDragging(false)}
        onDrop={(e) => {
          e.preventDefault()
          setDragging(false)
          handleFile(e.dataTransfer.files[0])
        }}
        onClick={() => inputRef.current.click()}
      >
        <Upload size={20} color="var(--color-primary)" />
        <p style={styles.dropText}>
          {file ? file.name : 'Click or drag file here'}
        </p>
        <p style={styles.dropHint}>PDF, DOCX, TXT, CSV, MD</p>
        <input
          ref={inputRef}
          type="file"
          accept={ACCEPTED}
          style={{ display: 'none' }}
          onChange={(e) => handleFile(e.target.files[0])}
        />
      </div>

      {/* Selected file */}
      {file && (
        <div style={styles.fileRow}>
          <FileText size={15} color="var(--color-primary)" />
          <span style={styles.fileName}>{file.name}</span>
          <button style={styles.removeBtn} onClick={() => setFile(null)}>
            <X size={14} />
          </button>
        </div>
      )}

      {/* Status */}
      {status && (
        <div style={{ ...styles.status, background: status.type === 'success' ? '#ECFDF5' : '#FEF2F2' }}>
          {status.type === 'success'
            ? <CheckCircle size={14} color="var(--color-success)" />
            : <AlertCircle size={14} color="var(--color-danger)" />}
          <span style={{ color: status.type === 'success' ? 'var(--color-success)' : 'var(--color-danger)', fontSize: 12 }}>
            {status.msg}
          </span>
        </div>
      )}

      {/* Upload Button */}
      {file && (
        <button
          style={{
            ...styles.uploadBtn,
            opacity: uploading ? 0.6 : 1,
            cursor: uploading ? 'not-allowed' : 'pointer',
          }}
          disabled={uploading}
          onClick={handleUpload}
        >
          {uploading ? 'Processing…' : 'Add to Knowledge Base'}
        </button>
      )}
    </div>
  )
}

const styles = {
  wrapper: { padding: '0' },
  dropzone: {
    border: '1.5px dashed var(--color-border)',
    borderRadius: 'var(--radius-sm)',
    padding: '16px 12px',
    textAlign: 'center',
    cursor: 'pointer',
    transition: 'all var(--transition)',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: 4,
  },
  dropText: { fontSize: 12.5, fontWeight: 500, color: 'var(--color-text)' },
  dropHint: { fontSize: 11, color: 'var(--color-text-muted)' },
  fileRow: {
    display: 'flex',
    alignItems: 'center',
    gap: 8,
    marginTop: 8,
    background: '#F1F5F9',
    borderRadius: 'var(--radius-sm)',
    padding: '6px 10px',
  },
  fileName: { fontSize: 12, color: 'var(--color-primary)', flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' },
  removeBtn: { background: 'none', border: 'none', cursor: 'pointer', color: 'var(--color-text-muted)', display: 'flex', alignItems: 'center' },
  status: {
    display: 'flex',
    alignItems: 'center',
    gap: 6,
    padding: '8px 10px',
    borderRadius: 'var(--radius-sm)',
    marginTop: 8,
  },
  uploadBtn: {
    marginTop: 8,
    width: '100%',
    padding: '8px',
    background: 'var(--color-orange)',
    color: '#FFFFFF',
    border: 'none',
    borderRadius: 'var(--radius-sm)',
    fontWeight: 600,
    fontSize: 12.5,
    cursor: 'pointer',
    fontFamily: 'var(--font-sans)',
    transition: 'background var(--transition)',
  },
}

