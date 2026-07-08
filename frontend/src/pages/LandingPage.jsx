import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'

const LANGUAGES = [
  { code: 'en', name: 'English', native: 'English' },
  { code: 'hi', name: 'Hindi', native: 'हिन्दी' },
  { code: 'ta', name: 'Tamil', native: 'தமிழ்' },
  { code: 'te', name: 'Telugu', native: 'తెలుగు' },
  { code: 'bn', name: 'Bengali', native: 'বাংলা' },
  { code: 'mr', name: 'Marathi', native: 'मराठी' },
  { code: 'gu', name: 'Gujarati', native: 'ગુજરાતી' },
  { code: 'kn', name: 'Kannada', native: 'ಕನ್ನಡ' },
  { code: 'ml', name: 'Malayalam', native: 'മലയാളം' },
]

const DEMO_CUSTOMERS = [
  { id: 'CUST001', name: 'Rajesh Kumar', profile: 'Moderate Risk | IT Professional' },
  { id: 'CUST002', name: 'Priya Sharma', profile: 'Aggressive | Marketing Manager' },
  { id: 'CUST003', name: 'Venkatesh Iyer', profile: 'Conservative | Business Owner' },
]

export default function LandingPage({ user, onSelectCustomer, onSelectLanguage, onLogout }) {
  const [step, setStep] = useState(1)
  const [selectedLang, setSelectedLang] = useState('en')
  const [selectedCustomer, setSelectedCustomer] = useState(null)
  const navigate = useNavigate()

  const handleStart = () => {
    if (selectedCustomer) {
      onSelectCustomer(selectedCustomer)
      onSelectLanguage(selectedLang)
      navigate('/chat')
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-idbi-primary via-idbi-secondary to-blue-900 flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white rounded-3xl shadow-2xl max-w-lg w-full overflow-hidden"
      >
        {/* Header */}
        <div className="bg-gradient-to-r from-idbi-primary to-idbi-secondary p-6 text-center relative">
          {/* Logout button */}
          <button
            onClick={onLogout}
            className="absolute top-4 right-4 text-white/70 hover:text-white text-xs bg-white/10 px-2 py-1 rounded-full"
          >
            Logout
          </button>
          <div className="w-20 h-20 bg-white/20 rounded-full mx-auto mb-4 flex items-center justify-center">
            <span className="text-4xl">🧠</span>
          </div>
          <h1 className="text-2xl font-bold text-white">FinSight AI</h1>
          <p className="text-blue-200 text-sm mt-1">Dhan Sakhi - Your AI Wealth Advisor</p>
          {user && <p className="text-blue-300 text-xs mt-2">Logged in as: {user}</p>}
        </div>

        <div className="p-6">
          {step === 1 && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
              <h2 className="text-lg font-semibold text-gray-800 mb-4">Select Your Language</h2>
              <div className="grid grid-cols-3 gap-2">
                {LANGUAGES.map((lang) => (
                  <button
                    key={lang.code}
                    onClick={() => setSelectedLang(lang.code)}
                    className={`p-3 rounded-xl border-2 text-center transition-all ${
                      selectedLang === lang.code
                        ? 'border-idbi-primary bg-idbi-light text-idbi-primary font-semibold'
                        : 'border-gray-200 hover:border-idbi-accent'
                    }`}
                  >
                    <div className="text-sm font-medium">{lang.native}</div>
                    <div className="text-xs text-gray-500">{lang.name}</div>
                  </button>
                ))}
              </div>
              <button
                onClick={() => setStep(2)}
                className="btn-primary w-full mt-6"
              >
                Continue
              </button>
            </motion.div>
          )}

          {step === 2 && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
              <h2 className="text-lg font-semibold text-gray-800 mb-4">Select Demo Profile</h2>
              <div className="space-y-3">
                {DEMO_CUSTOMERS.map((cust) => (
                  <button
                    key={cust.id}
                    onClick={() => setSelectedCustomer(cust)}
                    className={`w-full p-4 rounded-xl border-2 text-left transition-all ${
                      selectedCustomer?.id === cust.id
                        ? 'border-idbi-primary bg-idbi-light'
                        : 'border-gray-200 hover:border-idbi-accent'
                    }`}
                  >
                    <div className="font-semibold text-gray-800">{cust.name}</div>
                    <div className="text-sm text-gray-500">{cust.profile}</div>
                  </button>
                ))}
              </div>
              <div className="flex gap-3 mt-6">
                <button onClick={() => setStep(1)} className="btn-secondary flex-1">
                  Back
                </button>
                <button
                  onClick={handleStart}
                  disabled={!selectedCustomer}
                  className="btn-primary flex-1 disabled:opacity-50"
                >
                  Start Conversation
                </button>
              </div>
            </motion.div>
          )}
        </div>
      </motion.div>
    </div>
  )
}
