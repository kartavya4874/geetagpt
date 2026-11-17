import React, { useState, useEffect } from 'react'
import { Folder, Database, RefreshCw, Plus, CheckCircle2 } from 'lucide-react'
import axios from 'axios'
import FileUpload from './FileUpload'

export default function Sidebar({ currentCollection, onSelectCollection, onRefreshCollections }) {
  const [collections, setCollections] = useState([])
  const [loadingCollections, setLoadingCollections] = useState(false)

  const fetchCollections = async () => {
    setLoadingCollections(true)
    try {
      const res = await axios.get('/api/collections')
      if (res.data?.collections) {
        setCollections(res.data.collections)
      }
    } catch {
      // Backend offline or starting
    } finally {
      setLoadingCollections(false)
    }
  }

  useEffect(() => {
    fetchCollections()
  }, [])

  const handleUploadSuccess = () => {
    fetchCollections()
    if (onRefreshCollections) onRefreshCollections()
  }

  return (
    <aside style={styles.sidebar}>
      {/* Official University Header */}
      <div style={styles.brandHeader}>
        <img
          src="/logo.png"
          alt="Geeta University"
          style={styles.logoImage}
        />
        <div style={styles.brandBadge}>Academic AI Assistant</div>
      </div>

      {/* Main Content Area */}
      <div style={styles.bodyContent}>
        {/* Upload Academic Material */}
        <div style={styles.card}>
          <div style={styles.cardTitle}>Upload Study Material</div>
          <p style={styles.cardSubtitle}>
            Add PDFs, syllabus, lecture notes, or research papers to your personal knowledge base.
          </p>
          <FileUpload onUploadSuccess={handleUploadSuccess} />
        </div>

        {/* Knowledge Collections */}
        <div style={styles.collectionsWrapper}>
          <div style={styles.sectionHeader}>
            <span style={styles.sectionLabel}>Knowledge Base</span>
            <button
              onClick={fetchCollections}
              style={styles.iconBtn}
              title="Refresh"
            >
              <RefreshCw size={13} className={loadingCollections ? 'spin' : ''} />
            </button>
          </div>

          <div style={styles.collectionList}>
            {collections.length === 0 ? (
              <div style={styles.activePill}>
                <Database size={13} color="var(--color-primary)" />
                <span style={styles.collectionName}>General Knowledge</span>
                <CheckCircle2 size={12} color="var(--color-success)" style={{ marginLeft: 'auto' }} />
              </div>
            ) : (
              collections.map((name) => {
                const isActive = currentCollection === name
                return (
                  <button
                    key={name}
                    onClick={() => onSelectCollection(name)}
                    style={{
                      ...styles.collectionItem,
                      backgroundColor: isActive ? '#EFF6FF' : 'transparent',
                      color: isActive ? 'var(--color-primary)' : 'var(--color-text-secondary)',
                      borderColor: isActive ? '#BFDBFE' : 'transparent',
                      fontWeight: isActive ? 600 : 400,
                    }}
                  >
                    <Folder size={14} color={isActive ? 'var(--color-primary)' : '#94A3B8'} />
                    <span style={styles.collectionName}>{name}</span>
                    {isActive && (
                      <span style={styles.activeTag}>Active</span>
                    )}
                  </button>
                )
              })
            )}
          </div>
        </div>
      </div>

      {/* Institutional Footer */}
      <footer style={styles.footer}>
        <div style={styles.footerMotto}>Powering Education, Empowering Minds.</div>
        <div style={styles.footerSub}>Geeta University · Panipat, Delhi NCR</div>
      </footer>
    </aside>
  )
}

const styles = {
  sidebar: {
    width: '320px',
    height: '100%',
    backgroundColor: '#FFFFFF',
    borderRight: '1px solid var(--color-border)',
    display: 'flex',
    flexDirection: 'column',
    flexShrink: 0,
  },
  brandHeader: {
    padding: '24px 20px 18px',
    borderBottom: '1px solid var(--color-border)',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'flex-start',
    gap: '10px',
    backgroundColor: '#FFFFFF',
  },
  logoImage: {
    width: '100%',
    maxHeight: '54px',
    objectFit: 'contain',
    objectPosition: 'left center',
  },
  brandBadge: {
    fontSize: '11px',
    fontWeight: 600,
    letterSpacing: '0.04em',
    color: 'var(--color-primary)',
    backgroundColor: '#EFF6FF',
    border: '1px solid #DBEAFE',
    padding: '3px 10px',
    borderRadius: 'var(--radius-full)',
  },
  bodyContent: {
    flex: 1,
    overflowY: 'auto',
    padding: '16px 16px',
    display: 'flex',
    flexDirection: 'column',
    gap: '20px',
  },
  card: {
    backgroundColor: '#F8FAFC',
    border: '1px solid var(--color-border)',
    borderRadius: 'var(--radius-md)',
    padding: '14px 12px 10px',
  },
  cardTitle: {
    fontSize: '12.5px',
    fontWeight: 600,
    color: 'var(--color-text)',
    marginBottom: '4px',
  },
  cardSubtitle: {
    fontSize: '11px',
    color: 'var(--color-text-secondary)',
    lineHeight: 1.4,
    marginBottom: '10px',
  },
  collectionsWrapper: {
    display: 'flex',
    flexDirection: 'column',
    gap: '8px',
  },
  sectionHeader: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: '0 4px',
  },
  sectionLabel: {
    fontSize: '11px',
    fontWeight: 600,
    letterSpacing: '0.06em',
    textTransform: 'uppercase',
    color: 'var(--color-text-muted)',
  },
  iconBtn: {
    background: 'none',
    border: 'none',
    cursor: 'pointer',
    color: 'var(--color-text-muted)',
    display: 'flex',
    alignItems: 'center',
    padding: '3px',
    borderRadius: '4px',
    transition: 'color var(--transition)',
  },
  collectionList: {
    display: 'flex',
    flexDirection: 'column',
    gap: '4px',
  },
  collectionItem: {
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    padding: '8px 12px',
    borderRadius: 'var(--radius-sm)',
    border: '1px solid transparent',
    cursor: 'pointer',
    fontSize: '13px',
    width: '100%',
    textAlign: 'left',
    transition: 'all var(--transition)',
    fontFamily: 'var(--font-sans)',
  },
  activePill: {
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    padding: '8px 12px',
    borderRadius: 'var(--radius-sm)',
    backgroundColor: '#EFF6FF',
    border: '1px solid #BFDBFE',
    fontSize: '13px',
    color: 'var(--color-primary)',
    fontWeight: 600,
  },
  collectionName: {
    flex: 1,
    overflow: 'hidden',
    textOverflow: 'ellipsis',
    whiteSpace: 'nowrap',
  },
  activeTag: {
    fontSize: '10px',
    fontWeight: 600,
    color: 'var(--color-primary)',
    backgroundColor: '#DBEAFE',
    padding: '1px 6px',
    borderRadius: '4px',
  },
  footer: {
    padding: '14px 18px',
    borderTop: '1px solid var(--color-border)',
    backgroundColor: '#FFFFFF',
    textAlign: 'center',
  },
  footerMotto: {
    fontSize: '11px',
    fontWeight: 600,
    color: 'var(--color-text-secondary)',
  },
  footerSub: {
    fontSize: '10.5px',
    color: 'var(--color-text-muted)',
    marginTop: '2px',
  },
}
