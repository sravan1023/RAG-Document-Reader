import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'

// This is the crucial line that was likely missing.
// It imports all the Tailwind CSS styles into your application.
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)