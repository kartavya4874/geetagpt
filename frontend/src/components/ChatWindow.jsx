import React, { useState, useEffect, useRef, useCallback } from 'react'
import { ArrowUp, Trash2, Brain } from 'lucide-react'
import axios from 'axios'
import MessageBubble from './MessageBubble'

const SESSION_KEY = 'geetagpt_session_id'

function getOrCreateSessionId() {
  let sid = localStorage.getItem(SESSION_KEY)
  if (!sid) {
    sid = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    localStorage.setItem(SESSION_KEY, sid)
  }
  return sid
}

function createNewSessionId() {
  const sid = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
  localStorage.setItem(SESSION_KEY, sid)
  return sid
}

function formatTime(date) {
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

function MemoryBadge({ count }) {
  if (count === 0) return null
  return (
    <div style={styles.memoryBadge} title={`${count} messages remembered in this session`}>
      <Brain size={11} color="#10B981" />
      <span>Memory · {count} msg{count !== 1 ? 's' : ''}</span>
    </div>
  )
}

function TypingIndicator() {

  return (
    <div style={styles.typingRow}>
      <div style={styles.typingAvatar}><span>G</span></div>
      <div style={styles.typingBubble}>
        {[0, 1, 2].map((i) => (
          <span key={i} style={{ ...styles.dot, animationDelay: `${i * 0.18}s` }} />
        ))}
      </div>
    </div>
  )
}

const WELCOME_MESSAGE = {
  role: 'assistant',
  content: "**Welcome to GeetaGPT** — your official academic AI assistant.\n\nI can help you with:\n- 📖 Exploring syllabus, lecture notes, and uploaded course materials\n- 💻 Coding, technical problem-solving, and concept explanations\n- 🔍 Academic and educational web research (guided by institutional guardrails)\n\nType your question below or upload course material in the sidebar to begin.",
  agent: null,
  timestamp: formatTime(new Date()),
}

export default function ChatWindow({ collection }) {
  const [sessionId, setSessionId] = useState(getOrCreateSessionId)
  const [messages, setMessages] = useState([WELCOME_MESSAGE])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [historyLoaded, setHistoryLoaded] = useState(false)
  const [memoryCount, setMemoryCount] = useState(0)
  const bottomRef = useRef()

  // ─── Load persisted conversation on mount / when session changes ────────
  useEffect(() => {
    const loadHistory = async () => {
      try {
        const { data } = await axios.get(`/api/history/${sessionId}`)
        if (data.messages && data.messages.length > 0) {
          setMessages([WELCOME_MESSAGE, ...data.messages])
          setMemoryCount(data.messages.length)
        } else {
          setMemoryCount(0)
        }
      } catch {
        // No history yet or server not ready — start fresh
        setMemoryCount(0)
      } finally {
        setHistoryLoaded(true)
      }
    }
    loadHistory()
  }, [sessionId])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  const handleSend = useCallback(async () => {
    const q = input.trim()
    if (!q || loading) return

    const userMsg = {
      role: 'user',
      content: q,
      timestamp: formatTime(new Date()),
    }
    setMessages((prev) => [...prev, userMsg])
    setInput('')
    setLoading(true)

    try {
      const { data } = await axios.post('/api/chat', {
        query: q,
        collection_name: collection || 'geetagpt',
        top_k: 5,
        session_id: sessionId,
      })

      const assistantMsg = {
        role: 'assistant',
        content: data.answer,
        agent: data.agent,
        sources: data.sources || [],
        timestamp: formatTime(new Date()),
      }
      setMessages((prev) => [...prev, assistantMsg])
      setMemoryCount((c) => c + 2) // user + assistant turn
    } catch (err) {
      const errMsg = {
        role: 'assistant',
        content: `❌ **Error:** ${err.response?.data?.detail || err.message || 'Unable to process your request.'}`,
        agent: null,
        timestamp: formatTime(new Date()),
      }
      setMessages((prev) => [...prev, errMsg])
    } finally {
      setLoading(false)
    }
  }, [input, loading, collection, sessionId])

  const handleNewChat = async () => {
    try {
      await axios.delete(`/api/history/${sessionId}`)
    } catch { /* ignore */ }
    // Create a brand new session so old context is completely separated
    const newSid = createNewSessionId()
    setSessionId(newSid)
    setMessages([WELCOME_MESSAGE])
    setMemoryCount(0)
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div style={styles.wrapper}>
      {/* Messages Feed */}
      <div style={styles.messages}>
        <div style={styles.messagesInner}>
          {messages.map((msg, i) => (
            <MessageBubble key={i} message={msg} />
          ))}
          {loading && <TypingIndicator />}
          <div ref={bottomRef} />
        </div>
      </div>

      {/* Input Bar */}
      <div style={styles.inputArea}>
        <div style={styles.inputRow}>
          <div style={styles.inputContainer}>
            <textarea
              style={styles.textarea}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask an academic question, or explore uploaded course materials..."
              rows={1}
              disabled={loading}
            />
            <button
              style={{
                ...styles.sendBtn,
                backgroundColor: input.trim() && !loading ? 'var(--color-orange)' : '#E2E8F0',
                color: input.trim() && !loading ? '#FFFFFF' : '#94A3B8',
                cursor: input.trim() && !loading ? 'pointer' : 'default',
              }}
              onClick={loading ? undefined : handleSend}
              disabled={!input.trim() || loading}
            >
              <ArrowUp size={17} />
            </button>
          </div>
          <button
            onClick={handleNewChat}
            title="Start a new conversation"
            style={styles.newChatBtn}
          >
            <Trash2 size={15} />
            <span>New Chat</span>
          </button>
        </div>
        <div style={styles.hintRow}>
          <MemoryBadge count={memoryCount} />
          <p style={styles.hint}>
            GeetaGPT Academic Assistant · Geeta University
          </p>
        </div>
      </div>
    </div>
  )
}

const styles = {
  wrapper: {
    display: 'flex',
    flexDirection: 'column',
    height: '100%',
    backgroundColor: 'var(--color-bg)',
  },
  messages: {
    flex: 1,
    overflowY: 'auto',
    padding: '24px 20px',
    display: 'flex',
    justifyContent: 'center',
  },
  messagesInner: {
    width: '100%',
    maxWidth: '820px',
    display: 'flex',
    flexDirection: 'column',
  },
  typingRow: {
    display: 'flex',
    alignItems: 'flex-start',
    gap: '12px',
    marginBottom: '20px',
  },
  typingAvatar: {
    width: '32px', height: '32px', borderRadius: '8px',
    backgroundColor: 'var(--color-primary)', color: '#FFFFFF',
    display: 'flex', alignItems: 'center', justifyContent: 'center',
    fontWeight: 700, fontSize: '14px', flexShrink: 0, marginTop: '2px',
  },
  typingBubble: {
    backgroundColor: '#FFFFFF', border: '1px solid var(--color-border)',
    padding: '12px 18px',
    borderRadius: 'var(--radius-lg) var(--radius-lg) var(--radius-lg) 2px',
    display: 'flex', gap: '5px', alignItems: 'center',
    boxShadow: 'var(--shadow-subtle)',
  },
  dot: {
    width: '6px', height: '6px', borderRadius: '50%',
    backgroundColor: 'var(--color-primary)', display: 'inline-block',
    animation: 'bounce 1.2s infinite ease-in-out',
  },
  inputArea: {
    padding: '14px 20px 14px',
    backgroundColor: '#FFFFFF',
    borderTop: '1px solid var(--color-border)',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
  },
  inputRow: {
    display: 'flex',
    gap: '10px',
    alignItems: 'center',
    width: '100%',
    maxWidth: '820px',
  },
  inputContainer: {
    flex: 1,
    display: 'flex',
    alignItems: 'center',
    backgroundColor: '#F8FAFC',
    border: '1.5px solid var(--color-border)',
    borderRadius: 'var(--radius-md)',
    padding: '4px 6px 4px 14px',
    transition: 'border-color var(--transition)',
  },
  textarea: {
    flex: 1, border: 'none', backgroundColor: 'transparent', outline: 'none',
    resize: 'none', fontSize: '14px', fontFamily: 'var(--font-sans)',
    color: 'var(--color-text)', lineHeight: 1.5, maxHeight: '120px', padding: '6px 0',
  },
  sendBtn: {
    width: '34px', height: '34px', borderRadius: 'var(--radius-sm)', border: 'none',
    display: 'flex', alignItems: 'center', justifyContent: 'center',
    transition: 'all var(--transition)', flexShrink: 0,
  },
  newChatBtn: {
    display: 'flex', alignItems: 'center', gap: '6px',
    padding: '8px 14px', borderRadius: 'var(--radius-sm)',
    border: '1.5px solid var(--color-border)', background: '#FFFFFF',
    color: 'var(--color-text-secondary)', fontSize: '12.5px', fontWeight: 600,
    cursor: 'pointer', fontFamily: 'var(--font-sans)', whiteSpace: 'nowrap',
    transition: 'all var(--transition)',
  },
  hintRow: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '10px',
    marginTop: '7px',
    flexWrap: 'wrap',
  },
  hint: {
    fontSize: '11px', color: 'var(--color-text-muted)',
    textAlign: 'center',
  },
  memoryBadge: {
    display: 'inline-flex',
    alignItems: 'center',
    gap: '4px',
    fontSize: '11px',
    fontWeight: 600,
    color: '#10B981',
    backgroundColor: '#ECFDF5',
    border: '1px solid #A7F3D0',
    padding: '2px 8px',
    borderRadius: 'var(--radius-full)',
  },
}
