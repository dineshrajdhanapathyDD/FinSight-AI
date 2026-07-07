import { useState } from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import LandingPage from './pages/LandingPage'
import ChatPage from './pages/ChatPage'
import PortfolioPage from './pages/PortfolioPage'

function App() {
  const [customer, setCustomer] = useState(null)
  const [language, setLanguage] = useState('en')

  return (
    <BrowserRouter>
      <Routes>
        <Route
          path="/"
          element={
            <LandingPage
              onSelectCustomer={setCustomer}
              onSelectLanguage={setLanguage}
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
      </Routes>
    </BrowserRouter>
  )
}

export default App
