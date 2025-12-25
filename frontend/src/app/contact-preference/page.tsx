'use client'

import { useState, useEffect } from 'react'
import { useSearchParams, useRouter } from 'next/navigation'
import { Mail, MessageCircle, Phone, CheckCircle } from 'lucide-react'
import Link from 'next/link'
import Image from 'next/image'

type PreferenceState = 'idle' | 'loading' | 'success' | 'error'
type Preference = 'email' | 'whatsapp' | 'phone'

const Logo = ({ className = "h-10", width = 200, height = 40 }: { className?: string; width?: number; height?: number }) => (
  <Image
    src="/logos/logo-light-accent.png"
    alt="The Shinobi Project"
    width={width}
    height={height}
    className={className}
    priority
  />
)

export default function ContactPreferencePage() {
  const searchParams = useSearchParams()
  const router = useRouter()
  const [state, setState] = useState<PreferenceState>('idle')
  const [errorMessage, setErrorMessage] = useState('')
  const contactId = searchParams.get('id')

  useEffect(() => {
    if (!contactId) {
      setErrorMessage('Invalid or missing contact ID')
      setState('error')
    }
  }, [contactId])

  const handlePreferenceSelect = async (preference: Preference) => {
    if (!contactId) return

    setState('loading')
    setErrorMessage('')

    try {
      const directusUrl = process.env.NEXT_PUBLIC_DIRECTUS_URL || 'http://localhost:8055'
      const response = await fetch(`${directusUrl}/items/contact_submissions/${contactId}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          communication_preference: preference,
          preference_collected: true
        }),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.errors?.[0]?.message || 'Failed to save preference')
      }

      setState('success')

      // Redirect to home after 2 seconds
      setTimeout(() => {
        router.push('/')
      }, 2000)
    } catch (error) {
      console.error('Preference save error:', error)
      setState('error')
      setErrorMessage(error instanceof Error ? error.message : 'Failed to save preference. Please try again.')
    }
  }

  const preferenceOptions = [
    {
      value: 'email' as Preference,
      icon: Mail,
      title: 'Email',
      description: 'Prefer email communication',
      color: 'red'
    },
    {
      value: 'whatsapp' as Preference,
      icon: MessageCircle,
      title: 'WhatsApp',
      description: 'Message via WhatsApp',
      color: 'green'
    },
    {
      value: 'phone' as Preference,
      icon: Phone,
      title: 'Phone Call',
      description: 'Direct phone call',
      color: 'blue'
    }
  ]

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-300 font-sans flex flex-col">
      {/* Header */}
      <nav className="w-full py-6 px-6 border-b border-zinc-800">
        <div className="container mx-auto">
          <Link href="/" className="flex items-center">
            <Logo className="h-10 w-auto" width={200} height={40} />
          </Link>
        </div>
      </nav>

      {/* Main Content */}
      <div className="flex-1 flex items-center justify-center p-6">
        <div className="w-full max-w-2xl">
          {state === 'success' ? (
            <div className="text-center py-12">
              <div className="w-20 h-20 bg-green-500/20 border-2 border-green-500 rounded-full flex items-center justify-center mx-auto mb-6">
                <CheckCircle className="w-10 h-10 text-green-500" />
              </div>
              <h1 className="text-3xl font-bold text-white mb-4">Preference Saved</h1>
              <p className="text-zinc-400 text-lg">
                Thank you. We'll be in touch soon via your preferred method.
              </p>
              <p className="text-zinc-500 text-sm mt-4">
                Redirecting to homepage...
              </p>
            </div>
          ) : (
            <>
              {/* Header */}
              <div className="text-center mb-12">
                <h1 className="text-4xl md:text-5xl font-bold text-white mb-4 tracking-tight">
                  Select Your Preferred Contact Method
                </h1>
                <div className="h-1 w-20 bg-red-700 mx-auto mb-6"></div>
                <p className="text-zinc-400 text-lg">
                  How would you like us to reach you?
                </p>
              </div>

              {/* Error Message */}
              {errorMessage && (
                <div className="mb-8 p-4 bg-red-900/20 border border-red-700 rounded text-red-400">
                  {errorMessage}
                </div>
              )}

              {/* Preference Options */}
              {state !== 'error' && (
                <div className="grid md:grid-cols-3 gap-6">
                  {preferenceOptions.map((option) => (
                    <button
                      key={option.value}
                      onClick={() => handlePreferenceSelect(option.value)}
                      disabled={state === 'loading'}
                      className="group relative bg-zinc-900 border border-zinc-800 p-8 hover:border-red-700/50 transition-all duration-300 hover:shadow-2xl hover:shadow-red-900/10 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
                        <option.icon size={64} className="text-zinc-500" />
                      </div>
                      <div className="mb-6 inline-block p-4 bg-zinc-950 border border-zinc-800 rounded-sm">
                        <option.icon className="text-red-600" size={32} />
                      </div>
                      <h3 className="text-xl font-bold text-white mb-2 group-hover:text-red-500 transition-colors">
                        {option.title}
                      </h3>
                      <p className="text-zinc-500 text-sm">
                        {option.description}
                      </p>
                    </button>
                  ))}
                </div>
              )}

              {state === 'loading' && (
                <div className="mt-8 text-center">
                  <p className="text-zinc-400 text-sm uppercase tracking-wider">
                    Saving preference...
                  </p>
                </div>
              )}
            </>
          )}
        </div>
      </div>

      {/* Footer */}
      <footer className="w-full py-8 px-6 border-t border-zinc-900">
        <div className="container mx-auto text-center text-xs text-zinc-600 uppercase tracking-widest">
          <p>&copy; {new Date().getFullYear()} The Shinobi Project</p>
        </div>
      </footer>
    </div>
  )
}
