import { useState } from 'react'
import { motion } from 'framer-motion'

export default function LoginPage({ onLogin }) {
  const [step, setStep] = useState('email') // email | otp
  const [email, setEmail] = useState('')
  const [otp, setOtp] = useState('')
  const [generatedOtp, setGeneratedOtp] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSendOtp = (e) => {
    e.preventDefault()
    setError('')
    if (!email || !email.includes('@')) {
      setError('Please enter a valid email address')
      return
    }
    setLoading(true)
    // Generate 6-digit OTP (demo - in production use SES/SNS)
    const code = Math.floor(100000 + Math.random() * 900000).toString()
    setGeneratedOtp(code)
    // Simulate sending delay
    setTimeout(() => {
      setLoading(false)
      setStep('otp')
    }, 1000)
  }

  const handleVerifyOtp = (e) => {
    e.preventDefault()
    setError('')
    if (otp.length !== 6) {
      setError('Please enter 6-digit OTP')
      return
    }
    if (otp === generatedOtp || otp === '123456') {
      // Demo: accept generated OTP or 123456 as universal
      onLogin(email)
    } else {
      setError('Invalid OTP. Try again or use 123456 for demo.')
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-idbi-primary via-idbi-secondary to-blue-900 flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white rounded-3xl shadow-2xl max-w-md w-full overflow-hidden"
      >
        {/* Header */}
        <div className="bg-gradient-to-r from-idbi-primary to-idbi-secondary p-6 text-center">
          <div className="w-20 h-20 bg-white/20 rounded-full mx-auto mb-4 flex items-center justify-center">
            <span className="text-4xl">🧠</span>
          </div>
          <h1 className="text-2xl font-bold text-white">FinSight AI</h1>
          <p className="text-blue-200 text-sm mt-1">Dhan Sakhi - Your AI Wealth Advisor</p>
          <p className="text-blue-300 text-xs mt-2">IDBI Bank | Digital Wealth Management</p>
        </div>

        <div className="p-6">
          {step === 'email' && (
            <motion.form
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              onSubmit={handleSendOtp}
            >
              <h2 className="text-lg font-semibold text-gray-800 mb-2">Welcome Back</h2>
              <p className="text-sm text-gray-500 mb-6">Enter your email to receive a one-time password</p>

              <label className="block text-sm font-medium text-gray-700 mb-1">Email Address</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                className="w-full px-4 py-3 bg-gray-50 rounded-xl border border-gray-200 focus:border-idbi-accent focus:ring-2 focus:ring-idbi-accent/20 outline-none text-sm mb-4"
                autoFocus
              />

              {error && (
                <p className="text-red-500 text-xs mb-3">{error}</p>
              )}

              <button
                type="submit"
                disabled={loading}
                className="btn-primary w-full disabled:opacity-50"
              >
                {loading ? 'Sending OTP...' : 'Send OTP'}
              </button>

              <p className="text-xs text-gray-400 text-center mt-4">
                Demo: Any email works. Use OTP <span className="font-mono font-bold">123456</span>
              </p>
            </motion.form>
          )}

          {step === 'otp' && (
            <motion.form
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              onSubmit={handleVerifyOtp}
            >
              <h2 className="text-lg font-semibold text-gray-800 mb-2">Verify OTP</h2>
              <p className="text-sm text-gray-500 mb-1">
                Enter the 6-digit code sent to
              </p>
              <p className="text-sm font-medium text-idbi-primary mb-6">{email}</p>

              <label className="block text-sm font-medium text-gray-700 mb-1">One-Time Password</label>
              <input
                type="text"
                value={otp}
                onChange={(e) => setOtp(e.target.value.replace(/\D/g, '').slice(0, 6))}
                placeholder="Enter 6-digit OTP"
                className="w-full px-4 py-3 bg-gray-50 rounded-xl border border-gray-200 focus:border-idbi-accent focus:ring-2 focus:ring-idbi-accent/20 outline-none text-sm text-center text-xl tracking-widest mb-4"
                maxLength={6}
                autoFocus
              />

              {/* Show OTP for demo purposes */}
              <div className="bg-green-50 border border-green-200 rounded-lg p-2 mb-4">
                <p className="text-xs text-green-700 text-center">
                  Demo OTP: <span className="font-mono font-bold text-lg">{generatedOtp}</span>
                </p>
              </div>

              {error && (
                <p className="text-red-500 text-xs mb-3">{error}</p>
              )}

              <button type="submit" className="btn-primary w-full">
                Verify & Login
              </button>

              <button
                type="button"
                onClick={() => { setStep('email'); setOtp(''); setError(''); }}
                className="w-full text-center text-sm text-idbi-primary mt-3 hover:underline"
              >
                Change email
              </button>
            </motion.form>
          )}
        </div>
      </motion.div>
    </div>
  )
}
