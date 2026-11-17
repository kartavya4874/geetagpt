import React from 'react'
import ReactMarkdown from 'react-markdown'
import { BookOpen, Globe, Link2, User } from 'lucide-react'

function ContextBadge({ agent }) {
  if (agent === 'rag_agent') {
    return (
      <div style={styles.badge}>
        <BookOpen size={11} color="var(--color-primary)" />
        <span>Document Reference</span>
      </div>
    )
  }
  if (agent === 'tool_agent') {
    return (
      <div style={styles.badge}>
        <Globe size={11} color="var(--color-orange)" />
        <span>Web Search</span>
      </div>
    )
  }
  return null
}

function SourceList({ sources }) {
  if (!sources || sources.length === 0) return null
  return (
    <div style={styles.sourcesContainer}>
      <span style={styles.sourcesTitle}>References:</span>
      <div style={styles.sourcesRow}>
        {sources.map((s, i) => (
          <span key={i} style={styles.sourceTag}>
            <Link2 size={11} />
            {typeof s === 'string' ? s.split('/').pop() || s : s}
          </span>
        ))}
      </div>
    </div>
  )
}

export default function MessageBubble({ message }) {
  const isUser = message.role === 'user'

  return (
    <div style={{ ...styles.row, justifyContent: isUser ? 'flex-end' : 'flex-start' }}>
      {!isUser && (
        <div style={styles.avatarAssistant}>
          <span>G</span>
        </div>
      )}

      <div style={{ maxWidth: '78%' }}>
        {/* Context Tag (if Document or Web) */}
        {!isUser && message.agent && (
          <ContextBadge agent={message.agent} />
        )}

        {/* Message Bubble */}
        <div style={{
          ...styles.bubble,
          backgroundColor: isUser ? 'var(--color-primary)' : '#FFFFFF',
          color: isUser ? '#FFFFFF' : 'var(--color-text)',
          border: isUser ? 'none' : '1px solid var(--color-border)',
          borderRadius: isUser
            ? 'var(--radius-lg) var(--radius-lg) 2px var(--radius-lg)'
            : 'var(--radius-lg) var(--radius-lg) var(--radius-lg) 2px',
        }}>
          {isUser ? (
            <p style={{ margin: 0, fontSize: '14px', whiteSpace: 'pre-wrap' }}>{message.content}</p>
          ) : (
            <div style={styles.markdown}>
              <ReactMarkdown>{message.content}</ReactMarkdown>
            </div>
          )}
        </div>

        {/* Document Citations */}
        {!isUser && <SourceList sources={message.sources} />}

        {/* Timestamp */}
        <p style={{ ...styles.timestamp, textAlign: isUser ? 'right' : 'left' }}>
          {message.timestamp}
        </p>
      </div>

      {isUser && (
        <div style={styles.avatarUser}>
          <User size={14} color="#FFFFFF" />
        </div>
      )}
    </div>
  )
}

const styles = {
  row: {
    display: 'flex',
    alignItems: 'flex-start',
    gap: '12px',
    marginBottom: '22px',
  },
  avatarAssistant: {
    width: '32px',
    height: '32px',
    borderRadius: '8px',
    backgroundColor: 'var(--color-primary)',
    color: '#FFFFFF',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontWeight: 700,
    fontSize: '14px',
    flexShrink: 0,
    marginTop: '2px',
  },
  avatarUser: {
    width: '32px',
    height: '32px',
    borderRadius: '8px',
    backgroundColor: '#64748B',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    flexShrink: 0,
    marginTop: '2px',
  },
  badge: {
    display: 'inline-flex',
    alignItems: 'center',
    gap: '5px',
    fontSize: '11px',
    fontWeight: 600,
    color: 'var(--color-text-secondary)',
    marginBottom: '5px',
    padding: '2px 8px',
    borderRadius: 'var(--radius-sm)',
    backgroundColor: '#F1F5F9',
  },
  bubble: {
    padding: '14px 18px',
    boxShadow: 'var(--shadow-subtle)',
    fontSize: '14px',
    lineHeight: 1.6,
  },
  markdown: {
    fontSize: '14px',
    color: 'var(--color-text)',
    '& p': {
      marginBottom: '10px',
    },
    '& pre': {
      backgroundColor: '#0F172A',
      color: '#F8FAFC',
      padding: '12px 14px',
      borderRadius: 'var(--radius-sm)',
      overflowX: 'auto',
      fontSize: '13px',
      margin: '10px 0',
    },
    '& code': {
      backgroundColor: '#F1F5F9',
      padding: '2px 5px',
      borderRadius: '4px',
      fontSize: '12.5px',
      fontFamily: 'monospace',
    },
  },
  sourcesContainer: {
    marginTop: '6px',
    display: 'flex',
    flexDirection: 'column',
    gap: '4px',
  },
  sourcesTitle: {
    fontSize: '11px',
    fontWeight: 600,
    color: 'var(--color-text-muted)',
    textTransform: 'uppercase',
    letterSpacing: '0.04em',
  },
  sourcesRow: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: '6px',
  },
  sourceTag: {
    display: 'inline-flex',
    alignItems: 'center',
    gap: '4px',
    fontSize: '11.5px',
    color: 'var(--color-primary)',
    backgroundColor: '#EFF6FF',
    border: '1px solid #DBEAFE',
    padding: '3px 8px',
    borderRadius: 'var(--radius-sm)',
  },
  timestamp: {
    fontSize: '11px',
    color: 'var(--color-text-muted)',
    marginTop: '4px',
    padding: '0 2px',
  },
}
