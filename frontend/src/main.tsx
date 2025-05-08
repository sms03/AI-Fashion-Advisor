import React from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import './styles.scss'
import App from './App.tsx'

// Find the root element and create a root for React to mount on
const rootElement = document.getElementById('root')

if (!rootElement) {
  console.error('Failed to find the root element!')
} else {
  console.log('Root element found, rendering React app...')
  
  try {
    createRoot(rootElement).render(
      <React.StrictMode>
        <App />
      </React.StrictMode>
    )
    console.log('React render successful')
  } catch (error) {
    console.error('Error rendering React app:', error)
  }
}
