import React, { useState } from 'react'
import Sidebar from './components/Sidebar'
import ChatWindow from './components/ChatWindow'

export default function App() {
  const [selectedCollection, setSelectedCollection] = useState('geetagpt')

  return (
    <div style={styles.appContainer}>
      <Sidebar
        currentCollection={selectedCollection}
        onSelectCollection={setSelectedCollection}
      />
      <main style={styles.mainContent}>
        <header style={styles.topNavbar}>
          <div style={styles.topNavLeft}>
            <span style={styles.appTitle}>GeetaGPT</span>
            <span style={styles.divider}>/</span>
            <span style={styles.collectionPill}>
              {selectedCollection === 'geetagpt' ? 'Standard Library' : selectedCollection}
            </span>
          </div>
          <div style={styles.topNavRight}>
            <span style={styles.campusTag}>Panipat, Delhi NCR</span>
          </div>
        </header>
        <div style={styles.chatWrapper}>
          <ChatWindow collection={selectedCollection} />
        </div>
      </main>
    </div>
  )
}

const styles = {
  appContainer: {
    display: 'flex',
    height: '100vh',
    width: '100vw',
    overflow: 'hidden',
    backgroundColor: '#FFFFFF',
  },
  mainContent: {
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    height: '100%',
    minWidth: 0,
    backgroundColor: 'var(--color-bg)',
  },
  topNavbar: {
    height: '52px',
    backgroundColor: '#FFFFFF',
    borderBottom: '1px solid var(--color-border)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: '0 24px',
    flexShrink: 0,
  },
  topNavLeft: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
  },
  appTitle: {
    fontSize: '13.5px',
    fontWeight: 600,
    color: 'var(--color-text)',
    letterSpacing: '-0.01em',
  },
  divider: {
    color: 'var(--color-border)',
    fontSize: '14px',
  },
  collectionPill: {
    fontSize: '12px',
    color: 'var(--color-text-secondary)',
    backgroundColor: '#F1F5F9',
    padding: '2px 8px',
    borderRadius: 'var(--radius-sm)',
    fontWeight: 500,
  },
  topNavRight: {
    display: 'flex',
    alignItems: 'center',
  },
  campusTag: {
    fontSize: '11.5px',
    color: 'var(--color-text-secondary)',
    fontWeight: 500,
  },
  chatWrapper: {
    flex: 1,
    minHeight: 0,
  },
}
