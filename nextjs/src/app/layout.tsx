import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: {
    default: 'R2S Arena - React2Shell Testing Platform',
    template: '%s | R2S Arena'
  },
  description: 'R2S Arena - Professional React2Shell testing platform for CVE-2025-55182 vulnerability assessment and security research. Test your Next.js applications against React2Shell attacks.',
  keywords: [
    'React2Shell',
    'R2S',
    'CVE-2025-55182',
    'Next.js security',
    'React Server Components',
    'RCE testing',
    'vulnerability assessment',
    'security testing',
    'penetration testing',
    'web security'
  ],
  authors: [{ name: 'R2S Arena Team' }],
  creator: 'R2S Arena',
  publisher: 'R2S Arena',
  formatDetection: {
    email: false,
    address: false,
    telephone: false,
  },
  metadataBase: new URL('https://r2s-arena.fly.dev'),
  alternates: {
    canonical: '/',
  },
  openGraph: {
    type: 'website',
    locale: 'en_US',
    url: 'https://r2s-arena.fly.dev',
    title: 'R2S Arena - React2Shell Testing Platform',
    description: 'Professional React2Shell testing platform for CVE-2025-55182 vulnerability assessment',
    siteName: 'R2S Arena',
    images: [
      {
        url: '/icon.svg',
        width: 512,
        height: 512,
        alt: 'R2S Arena Logo',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'R2S Arena - React2Shell Testing Platform',
    description: 'Professional React2Shell testing platform for CVE-2025-55182 vulnerability assessment',
    images: ['/icon.svg'],
    creator: '@r2sarena',
  },
  robots: {
    index: false, // Don't index - this is a test app
    follow: false,
    googleBot: {
      index: false,
      follow: false,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  icons: {
    icon: [
      { url: '/favicon.svg', type: 'image/svg+xml' },
      { url: '/icon.svg', type: 'image/svg+xml', sizes: 'any' },
    ],
    apple: [
      { url: '/apple-icon.svg', type: 'image/svg+xml' },
    ],
    shortcut: '/favicon.svg',
  },
  manifest: '/manifest.json',
  category: 'Security Testing',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" data-theme="dark">
      <head>
        <link rel="icon" href="/favicon.svg" type="image/svg+xml" />
        <link rel="apple-touch-icon" href="/apple-icon.svg" />
        <meta name="theme-color" content="#3b82f6" />
        <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=5" />
      </head>
      <body>{children}</body>
    </html>
  )
}

