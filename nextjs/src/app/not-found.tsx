import Link from 'next/link'

export const metadata = {
  title: '404 - Page Not Found',
  description: 'The page you are looking for does not exist.',
}

export default function NotFound() {
  return (
    <div style={styles.body}>
        <div style={styles.container}>
          <div style={styles.content}>
            <div style={styles.iconContainer}>
              <svg 
                xmlns="http://www.w3.org/2000/svg" 
                viewBox="0 0 100 100" 
                width="120" 
                height="120"
                style={styles.icon}
              >
                <defs>
                  <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style={{stopColor:'#3b82f6', stopOpacity:1}} />
                    <stop offset="100%" style={{stopColor:'#8b5cf6', stopOpacity:1}} />
                  </linearGradient>
                </defs>
                <circle cx="50" cy="50" r="48" fill="url(#grad1)" opacity="0.2"/>
                <path d="M 50 15 L 30 25 L 30 45 Q 30 65 50 75 Q 70 65 70 45 L 70 25 Z" 
                      fill="url(#grad1)" 
                      stroke="#ffffff" 
                      strokeWidth="2"/>
                <text x="50" y="52" 
                      fontFamily="Arial, sans-serif" 
                      fontSize="20" 
                      fontWeight="bold" 
                      fill="#ffffff" 
                      textAnchor="middle">R2S</text>
              </svg>
            </div>
            
            <h1 style={styles.title}>404</h1>
            <h2 style={styles.subtitle}>Page Not Found</h2>
            <p style={styles.description}>
              The page you're looking for doesn't exist or has been moved.
            </p>
            
            <div style={styles.actions}>
              <Link href="/" style={styles.button}>
                ← Go Home
              </Link>
            </div>
            
            <div style={styles.info}>
              <p style={styles.infoText}>
                <strong>R2S Arena</strong> • React2Shell Testing Platform
              </p>
            </div>
          </div>
        </div>
    </div>
  )
}

const styles = {
  body: {
    margin: 0,
    padding: 0,
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", "Roboto", "Oxygen", "Ubuntu", "Cantarell", "Fira Sans", "Droid Sans", "Helvetica Neue", sans-serif',
    background: 'linear-gradient(135deg, var(--gradient-start, #1e1e2e) 0%, var(--gradient-end, #2d1b4e) 100%)',
    color: 'var(--text-primary, #ffffff)',
    minHeight: '100vh',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },
  container: {
    width: '100%',
    maxWidth: '600px',
    padding: '2rem',
    textAlign: 'center' as const,
  },
  content: {
    background: 'var(--bg-secondary, rgba(26, 26, 26, 0.8))',
    borderRadius: '24px',
    padding: '3rem 2rem',
    border: '1px solid var(--border, rgba(255, 255, 255, 0.1))',
    boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3)',
    backdropFilter: 'blur(10px)',
  },
  iconContainer: {
    marginBottom: '2rem',
    display: 'flex',
    justifyContent: 'center',
  },
  icon: {
    filter: 'drop-shadow(0 4px 8px rgba(59, 130, 246, 0.3))',
  },
  title: {
    fontSize: '6rem',
    fontWeight: '700',
    margin: '0 0 1rem 0',
    background: 'linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%)',
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent',
    backgroundClip: 'text',
    lineHeight: '1',
  },
  subtitle: {
    fontSize: '2rem',
    fontWeight: '600',
    margin: '0 0 1rem 0',
    color: 'var(--text-primary, #ffffff)',
  },
  description: {
    fontSize: '1.1rem',
    color: 'var(--text-secondary, rgba(255, 255, 255, 0.7))',
    margin: '0 0 2rem 0',
    lineHeight: '1.6',
  },
  actions: {
    marginTop: '2rem',
  },
  button: {
    display: 'inline-block',
    padding: '0.875rem 2rem',
    background: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)',
    color: '#ffffff',
    textDecoration: 'none',
    borderRadius: '8px',
    fontSize: '1rem',
    fontWeight: '600',
    transition: 'all 0.2s ease',
    boxShadow: '0 4px 6px rgba(0, 0, 0, 0.2)',
  },
  info: {
    marginTop: '3rem',
    paddingTop: '2rem',
    borderTop: '1px solid var(--border, rgba(255, 255, 255, 0.1))',
  },
  infoText: {
    fontSize: '0.9rem',
    color: 'var(--text-secondary, rgba(255, 255, 255, 0.6))',
    margin: 0,
  },
} as const

