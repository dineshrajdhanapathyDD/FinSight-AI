import { useState } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import LoginPage from './pages/LoginPage'
import LandingPage from './pages/LandingPage'
import ChatPage from './pages/ChatPage'
import PortfolioPage from './pages/PortfolioPage'

function App() {
  const [user, setUser] = useState(null) // logged in email
  const [customer, setCustomer] = useState(null)
  const [language, setLanguage] = useState('en')

  const handleLogin = (email) => {
    setUser(email)
  }

  const handleLogout = () => {
    setUser(null)
    setCustomer(null)
  }

  // Require login
  if (!user) {
    return (
      <BrowserRouter>
        <LoginPage onLogin={handleLogin} />
      </BrowserRouter>
    )
  }

  return (
    <BrowserRouter>
      <Routes>
        <Route
          path="/"
          element={
            <LandingPage
              user={user}
              onSelectCustomer={setCustomer}
              onSelectLanguage={setLanguage}
              onLogout={handleLogout}
            />
          }
        />
        <Route
          path="/chat"
          element={<ChatPage customer={customer} language={language} />}
        />
        <Route
          path="/portfolio"
          element={<PortfolioPage customer={customer} />}
        />
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
