'use client'

import { createContext, useContext, useState, type ReactNode } from 'react'
import { ContactModal } from './ContactModal'

interface ContactModalContextType {
  isOpen: boolean
  openModal: () => void
  closeModal: () => void
}

const ContactModalContext = createContext<ContactModalContextType | undefined>(undefined)

export function useContactModal() {
  const context = useContext(ContactModalContext)
  if (!context) {
    throw new Error('useContactModal must be used within ContactModalProvider')
  }
  return context
}

interface ContactModalProviderProps {
  children: ReactNode
}

export function ContactModalProvider({ children }: ContactModalProviderProps) {
  const [isOpen, setIsOpen] = useState(false)

  const openModal = () => setIsOpen(true)
  const closeModal = () => setIsOpen(false)

  return (
    <ContactModalContext.Provider value={{ isOpen, openModal, closeModal }}>
      {children}
      <ContactModal isOpen={isOpen} onClose={closeModal} />
    </ContactModalContext.Provider>
  )
}
