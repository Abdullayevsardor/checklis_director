import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'
import { Toaster } from "react-hot-toast";

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
    <Toaster
      position="top-center"
      toastOptions={{
        duration: 2500,
        style: {
          background: "#222",
          color: "#fff",
          borderRadius: "10px",
          padding: "12px 16px",
        },
  }}
/>
  </StrictMode>,
)
