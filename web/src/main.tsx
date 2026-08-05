import React from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'

import App from './App'
import './styles.css'

createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    {/* BrowserRouter gives us real URLs (/consultants, not /#/consultants). nginx.conf and the
        Vite dev server both fall back to index.html so a refresh on a deep link still works. */}
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </React.StrictMode>,
)
