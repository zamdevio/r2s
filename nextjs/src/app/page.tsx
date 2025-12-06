'use client'

import { useState, useEffect } from 'react'
import { handleAction } from './actions'

export default function Home() {
  const [data, setData] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [theme, setTheme] = useState<'dark' | 'light'>('dark')

  useEffect(() => {
    // Check system preference
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
    setTheme(prefersDark ? 'dark' : 'light')
    document.documentElement.setAttribute('data-theme', prefersDark ? 'dark' : 'light')
  }, [])

  const toggleTheme = () => {
    const newTheme = theme === 'dark' ? 'light' : 'dark'
    setTheme(newTheme)
    document.documentElement.setAttribute('data-theme', newTheme)
  }

  async function submitForm(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault()
    setIsLoading(true)
    try {
      const formData = new FormData(e.currentTarget)
      const result = await handleAction(formData)
      setData(result)
    } catch (error) {
      console.error('Error:', error)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <main style={styles.container}>
      {/* Header */}
      <header style={styles.header}>
        <div style={styles.headerContent}>
          <div>
            <h1 style={styles.title}>
              <span style={styles.titleIcon}>⚡</span>
              R2S Arena
            </h1>
            <p style={styles.subtitle}>React2Shell Testing Platform</p>
          </div>
          <button
            onClick={toggleTheme}
            style={styles.themeButton}
            aria-label="Toggle theme"
          >
            {theme === 'dark' ? '☀️' : '🌙'}
          </button>
        </div>
        <div style={styles.badgeContainer}>
          <span style={styles.badge}>Next.js 16.0.5</span>
          <span style={{...styles.badge, ...styles.badgeDanger}}>VULNERABLE</span>
          <span style={styles.badge}>CVE-2025-55182</span>
        </div>
      </header>

      {/* Main Content */}
      <div style={styles.content}>
        {/* Test Form Card */}
        <div style={styles.card}>
          <div style={styles.cardHeader}>
            <h2 style={styles.cardTitle}>Server Action Test</h2>
            <p style={styles.cardDescription}>
              Test the vulnerable Server Action endpoint
            </p>
          </div>
          
          <form onSubmit={submitForm} style={styles.form}>
            <div style={styles.formGroup}>
              <label style={styles.label}>
                Action Type
              </label>
              <select 
                name="action" 
                style={styles.select}
                defaultValue="test"
              >
                <option value="test">Test Action</option>
                <option value="process">Process Data</option>
                <option value="validate">Validate Input</option>
              </select>
            </div>
            
            <div style={styles.formGroup}>
              <label style={styles.label}>
                Input Data
              </label>
              <input 
                type="text" 
                name="input" 
                placeholder="Enter test data..."
                style={styles.input}
                defaultValue="Hello World"
              />
            </div>
            
            <button 
              type="submit"
              style={{
                ...styles.button,
                ...(isLoading ? styles.buttonLoading : {})
              }}
              disabled={isLoading}
            >
              {isLoading ? 'Processing...' : 'Submit Action'}
            </button>
          </form>
        </div>

        {/* Response Card */}
        {data && (
          <div style={styles.card}>
            <div style={styles.cardHeader}>
              <h2 style={styles.cardTitle}>Response</h2>
            </div>
            <div style={styles.responseBox}>
              <pre style={styles.codeBlock}>
                {JSON.stringify(data, null, 2)}
              </pre>
            </div>
          </div>
        )}

        {/* Security Warning Card */}
        <div style={styles.warningCard}>
          <div style={styles.warningHeader}>
            <span style={styles.warningIcon}>⚠️</span>
            <h3 style={styles.warningTitle}>Security Notice</h3>
          </div>
          <div style={styles.warningContent}>
            <p style={styles.warningText}>
              This application is <strong>intentionally vulnerable</strong> to CVE-2025-55182 (React2Shell).
              It uses Next.js 16.0.5 which is vulnerable to Remote Code Execution (RCE) attacks.
            </p>
            <ul style={styles.warningList}>
              <li>🚫 <strong>DO NOT</strong> use in production</li>
              <li>🚫 <strong>DO NOT</strong> use with real data</li>
              <li>✅ For security testing only</li>
              <li>✅ Isolated environment recommended</li>
            </ul>
          </div>
        </div>

        {/* Info Card */}
        <div style={styles.infoCard}>
          <h3 style={styles.infoTitle}>About This Demo</h3>
          <div style={styles.infoGrid}>
            <div style={styles.infoItem}>
              <span style={styles.infoLabel}>Version:</span>
              <span style={styles.infoValue}>Next.js 16.0.5</span>
            </div>
            <div style={styles.infoItem}>
              <span style={styles.infoLabel}>Status:</span>
              <span style={{...styles.infoValue, color: 'var(--danger)'}}>Vulnerable</span>
            </div>
            <div style={styles.infoItem}>
              <span style={styles.infoLabel}>CVE:</span>
              <span style={styles.infoValue}>CVE-2025-55182</span>
            </div>
            <div style={styles.infoItem}>
              <span style={styles.infoLabel}>Purpose:</span>
              <span style={styles.infoValue}>Security Testing</span>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer style={styles.footer}>
        <p style={styles.footerText}>
          R2S Arena • React2Shell Testing Platform • For Security Testing Only
        </p>
      </footer>
    </main>
  )
}

const styles = {
  container: {
    minHeight: '100vh',
    padding: '2rem 1rem',
    maxWidth: '1200px',
    margin: '0 auto',
  },
  header: {
    marginBottom: '3rem',
    padding: '2rem',
    background: 'var(--bg-secondary)',
    borderRadius: '16px',
    border: '1px solid var(--border)',
    boxShadow: '0 4px 6px var(--shadow)',
  },
  headerContent: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '1rem',
  },
  title: {
    fontSize: '2.5rem',
    fontWeight: '700',
    background: 'linear-gradient(135deg, var(--accent) 0%, var(--accent-light) 100%)',
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent',
    backgroundClip: 'text',
    marginBottom: '0.5rem',
    display: 'flex',
    alignItems: 'center',
    gap: '0.5rem',
  },
  titleIcon: {
    fontSize: '2.5rem',
    WebkitTextFillColor: 'var(--accent)',
  },
  subtitle: {
    fontSize: '1.1rem',
    color: 'var(--text-secondary)',
    fontWeight: '400',
  },
  themeButton: {
    padding: '0.75rem 1rem',
    background: 'var(--bg-tertiary)',
    border: '1px solid var(--border)',
    borderRadius: '8px',
    cursor: 'pointer',
    fontSize: '1.5rem',
    transition: 'all 0.2s ease',
  } as React.CSSProperties,
  badgeContainer: {
    display: 'flex',
    gap: '0.75rem',
    flexWrap: 'wrap' as const,
  },
  badge: {
    padding: '0.5rem 1rem',
    background: 'var(--bg-tertiary)',
    border: '1px solid var(--border)',
    borderRadius: '6px',
    fontSize: '0.875rem',
    fontWeight: '500',
    color: 'var(--text-primary)',
  },
  badgeDanger: {
    background: 'var(--danger)',
    color: '#ffffff',
    border: 'none',
  },
  content: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: '2rem',
  },
  card: {
    background: 'var(--bg-secondary)',
    borderRadius: '16px',
    padding: '2rem',
    border: '1px solid var(--border)',
    boxShadow: '0 4px 6px var(--shadow)',
    transition: 'transform 0.2s ease, box-shadow 0.2s ease',
  },
  cardHeader: {
    marginBottom: '1.5rem',
  },
  cardTitle: {
    fontSize: '1.5rem',
    fontWeight: '600',
    color: 'var(--text-primary)',
    marginBottom: '0.5rem',
  },
  cardDescription: {
    color: 'var(--text-secondary)',
    fontSize: '0.95rem',
  },
  form: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: '1.5rem',
  },
  formGroup: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: '0.5rem',
  },
  label: {
    fontSize: '0.95rem',
    fontWeight: '500',
    color: 'var(--text-primary)',
  },
  input: {
    padding: '0.75rem 1rem',
    background: 'var(--bg-tertiary)',
    border: '1px solid var(--border)',
    borderRadius: '8px',
    fontSize: '1rem',
    color: 'var(--text-primary)',
    transition: 'all 0.2s ease',
    outline: 'none',
    width: '100%',
  } as React.CSSProperties,
  select: {
    padding: '0.75rem 1rem',
    background: 'var(--bg-tertiary)',
    border: '1px solid var(--border)',
    borderRadius: '8px',
    fontSize: '1rem',
    color: 'var(--text-primary)',
    cursor: 'pointer',
    outline: 'none',
    width: '100%',
  } as React.CSSProperties,
  button: {
    padding: '0.875rem 1.5rem',
    background: 'linear-gradient(135deg, var(--accent) 0%, var(--accent-hover) 100%)',
    color: '#ffffff',
    border: 'none',
    borderRadius: '8px',
    fontSize: '1rem',
    fontWeight: '600',
    cursor: 'pointer',
    transition: 'all 0.2s ease',
    boxShadow: '0 2px 4px var(--shadow)',
  },
  buttonLoading: {
    opacity: 0.7,
    cursor: 'not-allowed',
  },
  responseBox: {
    background: 'var(--bg-tertiary)',
    borderRadius: '8px',
    padding: '1.5rem',
    border: '1px solid var(--border)',
  },
  codeBlock: {
    color: 'var(--text-primary)',
    fontSize: '0.9rem',
    lineHeight: '1.6',
    overflow: 'auto',
    margin: 0,
    fontFamily: 'Monaco, "Courier New", monospace',
  },
  warningCard: {
    background: 'linear-gradient(135deg, rgba(245, 158, 11, 0.1) 0%, rgba(239, 68, 68, 0.1) 100%)',
    border: '2px solid var(--warning)',
    borderRadius: '16px',
    padding: '2rem',
    boxShadow: '0 4px 6px var(--shadow)',
  },
  warningHeader: {
    display: 'flex',
    alignItems: 'center',
    gap: '0.75rem',
    marginBottom: '1rem',
  },
  warningIcon: {
    fontSize: '1.5rem',
  },
  warningTitle: {
    fontSize: '1.5rem',
    fontWeight: '600',
    color: 'var(--warning)',
  },
  warningContent: {
    color: 'var(--text-primary)',
  },
  warningText: {
    marginBottom: '1rem',
    lineHeight: '1.6',
  },
  warningList: {
    listStyle: 'none',
    display: 'flex',
    flexDirection: 'column' as const,
    gap: '0.75rem',
    paddingLeft: '0',
  },
  infoCard: {
    background: 'var(--bg-secondary)',
    borderRadius: '16px',
    padding: '2rem',
    border: '1px solid var(--border)',
    boxShadow: '0 4px 6px var(--shadow)',
  },
  infoTitle: {
    fontSize: '1.25rem',
    fontWeight: '600',
    color: 'var(--text-primary)',
    marginBottom: '1.5rem',
  },
  infoGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
    gap: '1.5rem',
  },
  infoItem: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: '0.5rem',
  },
  infoLabel: {
    fontSize: '0.875rem',
    color: 'var(--text-secondary)',
    fontWeight: '500',
  },
  infoValue: {
    fontSize: '1rem',
    color: 'var(--text-primary)',
    fontWeight: '600',
  },
  footer: {
    marginTop: '3rem',
    padding: '2rem',
    textAlign: 'center' as const,
    color: 'var(--text-secondary)',
    fontSize: '0.9rem',
  },
  footerText: {
    margin: 0,
  },
} as const
