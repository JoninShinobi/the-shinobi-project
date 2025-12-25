'use client'

import { useState, useEffect } from 'react'
import { X } from 'lucide-react'

interface ContactModalProps {
  isOpen: boolean
  onClose: () => void
}

type SubmitState = 'idle' | 'loading' | 'success' | 'error'

export function ContactModal({ isOpen, onClose }: ContactModalProps) {
  const [name, setName] = useState('')
  const [businessName, setBusinessName] = useState('')
  const [email, setEmail] = useState('')
  const [submitState, setSubmitState] = useState<SubmitState>('idle')
  const [errorMessage, setErrorMessage] = useState('')

  // Reset form when modal closes
  useEffect(() => {
    if (!isOpen) {
      setTimeout(() => {
        setName('')
        setBusinessName('')
        setEmail('')
        setSubmitState('idle')
        setErrorMessage('')
      }, 300) // Wait for close animation
    }
  }, [isOpen])

  // Handle ESC key
  useEffect(() => {
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose()
      }
    }
    window.addEventListener('keydown', handleEsc)
    return () => window.removeEventListener('keydown', handleEsc)
  }, [isOpen, onClose])

  // Auto-close after success
  useEffect(() => {
    if (submitState === 'success') {
      const timer = setTimeout(() => {
        onClose()
      }, 2000)
      return () => clearTimeout(timer)
    }
  }, [submitState, onClose])

  const validateEmail = (email: string): boolean => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    return emailRegex.test(email)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    // Validation
    if (!name.trim() || !businessName.trim() || !email.trim()) {
      setErrorMessage('All fields are required')
      return
    }

    if (!validateEmail(email)) {
      setErrorMessage('Please enter a valid email address')
      return
    }

    setSubmitState('loading')
    setErrorMessage('')

    try {
      const directusUrl = process.env.NEXT_PUBLIC_DIRECTUS_URL || 'http://localhost:8055'
      const response = await fetch(`${directusUrl}/items/contact_submissions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: name.trim(),
          email: email.trim(),
          business_name: businessName.trim(),
          communication_preference: null,
          preference_collected: false
        }),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.errors?.[0]?.message || 'Submission failed')
      }

      setSubmitState('success')
    } catch (error) {
      console.error('Contact submission error:', error)
      setSubmitState('error')
      setErrorMessage(error instanceof Error ? error.message : 'Failed to submit. Please try again.')
    }
  }

  const handleBackdropClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      onClose()
    }
  }

  if (!isOpen) return null

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/90 backdrop-blur-sm"
      onClick={handleBackdropClick}
    >
      <div className="relative w-full max-w-md bg-zinc-900 border border-red-700/30 rounded-lg shadow-2xl">
        {/* Close button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-zinc-400 hover:text-white transition-colors"
          aria-label="Close modal"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Header */}
        <div className="p-6 border-b border-red-700/30">
          <h2 className="text-2xl font-bold text-white uppercase tracking-wider">
            Initiate Contact
          </h2>
          <p className="text-sm text-zinc-400 mt-2">
            Begin secure transmission
          </p>
        </div>

        {/* Content */}
        <div className="p-6">
          {submitState === 'success' ? (
            <div className="text-center py-8">
              <div className="w-16 h-16 bg-green-500/20 border-2 border-green-500 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <h3 className="text-xl font-bold text-white mb-2">Transmission Received</h3>
              <p className="text-zinc-400 text-sm">
                Check your email for next steps
              </p>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-4">
              {/* Name field */}
              <div>
                <label htmlFor="name" className="block text-sm font-medium text-zinc-300 mb-2 uppercase tracking-wider">
                  Name
                </label>
                <input
                  id="name"
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full px-4 py-3 bg-zinc-800 border border-zinc-700 rounded text-white placeholder-zinc-500 focus:outline-none focus:border-red-700 transition-colors"
                  placeholder="Enter your name"
                  disabled={submitState === 'loading'}
                  required
                />
              </div>

              {/* Name of Business field */}
              <div>
                <label htmlFor="businessName" className="block text-sm font-medium text-zinc-300 mb-2 uppercase tracking-wider">
                  Name of Business
                </label>
                <input
                  id="businessName"
                  type="text"
                  value={businessName}
                  onChange={(e) => setBusinessName(e.target.value)}
                  className="w-full px-4 py-3 bg-zinc-800 border border-zinc-700 rounded text-white placeholder-zinc-500 focus:outline-none focus:border-red-700 transition-colors"
                  placeholder="Your business name"
                  disabled={submitState === 'loading'}
                  required
                />
              </div>

              {/* Email field */}
              <div>
                <label htmlFor="email" className="block text-sm font-medium text-zinc-300 mb-2 uppercase tracking-wider">
                  Email
                </label>
                <input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full px-4 py-3 bg-zinc-800 border border-zinc-700 rounded text-white placeholder-zinc-500 focus:outline-none focus:border-red-700 transition-colors"
                  placeholder="your@email.com"
                  disabled={submitState === 'loading'}
                  required
                />
              </div>

              {/* Error message */}
              {errorMessage && (
                <div className="p-3 bg-red-900/20 border border-red-700 rounded text-red-400 text-sm">
                  {errorMessage}
                </div>
              )}

              {/* Submit button */}
              <button
                type="submit"
                disabled={submitState === 'loading'}
                className="w-full px-6 py-3 bg-red-700 text-white font-bold uppercase tracking-wider hover:bg-red-600 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {submitState === 'loading' ? 'Transmitting...' : 'Initiate Protocol'}
              </button>
            </form>
          )}
        </div>
      </div>
    </div>
  )
}
