import { useState } from 'react'
import { motion } from 'framer-motion'
import { sendOtp, verifyOtp } from '../api'

export default function LoginPage({ onLogin }) {
  const [step, setStep] = useState('email')
  const [email, setEmail] = useState('')
  const [otp, setOtp] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const [demoMode, setDemoMode] = useState(false)

  const handleSendOtp = async (e) => {
    e.preventDefault()
    setError('')
    if (!email || !email.includes('@')) {
      setError('Please enter a valid email address')
      return
    }
    setLoading(true)
    try {
      const result = await sendOtp(email)
      setDemoMode(result.demo_mode || false)
      setStep('otp')
    } catch (err) {
      setError('Failed to send OTP. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleVerifyOtp = async (e) => {
    e.preventDefault()
    setError('')
    if (otp.length !== 6) {
      setError('Please enter 6-digit OTP')
      return
    }
    setLoading(true)
    try {
      const result = await verifyOtp(email, otp)
      if (result.verified) {
        onLogin(email)
      } else {
        setError('Invalid OTP. Please try again.')
      }
    } catch (err) {
      setError('Verification failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-idbi-primary via-idbi-secondary to-idbi-teal-dark flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white rounded-3xl shadow-2xl max-w-md w-full overflow-hidden"
      >
        {/* Header - Orange + Teal gradient */}
        <div className="bg-gradient-to-r from-idbi-accent to-idbi-primary p-6 text-center">
          <div className="w-20 h-20 bg-white/20 rounded-full mx-auto mb-4 flex items-center justify-center backdrop-blur-sm">
            <span className="text-4xl">🧠</span>
          </div>
          <h1 className="text-2xl font-bold text-white">FinSight AI</h1>
          <p className="text-white/80 text-sm mt-1">Dhan Sakhi - Your AI Wealth Advisor</p>
          <p className="text-white/60 text-xs mt-2">IDBI Bank | Digital Wealth Management</p>
        </div>

        <div className="p-6">
          {step === 'email' && (
            <motion.form
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              onSubmit={handleSendOtp}
            >
              <h2 className="text-lg font-semibold text-gray-800 mb-2">Welcome Back</h2>
              <p className="text-sm text-gray-500 mb-6">Enter your email to receive a secure one-time password</p>

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
                {loading ? (
                  <span className="flex items-center justify-center gap-2">
                    <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    Sending OTP...
                  </span>
                ) : 'Send OTP'}
              </button>

              <div className="mt-4 p-3 bg-idbi-teal-light rounded-lg">
                <p className="text-xs text-idbi-primary text-center">
                  🔒 Secured with email-based OTP authentication
                </p>
              </div>
            </motion.form>
          )}

          {step === 'otp' && (
            <motion.form
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              onSubmit={handleVerifyOtp}
            >
              <h2 className="text-lg font-semibold text-gray-800 mb-2">Verify OTP</h2>
              <p className="text-sm text-gray-500 mb-1">Enter the 6-digit code sent to</p>
              <p className="text-sm font-medium text-idbi-primary mb-4">{email}</p>

              <input
                type="text"
                value={otp}
                onChange={(e) => setOtp(e.target.value.replace(/\D/g, '').slice(0, 6))}
                placeholder="------"
                className="w-full px-4 py-4 bg-gray-50 rounded-xl border border-gray-200 focus:border-idbi-accent focus:ring-2 focus:ring-idbi-accent/20 outline-none text-center text-2xl tracking-[0.5em] font-mono mb-4"
                maxLength={6}
                autoFocus
              />

              {/* Security notice */}
              <div className="bg-idbi-teal-light border border-idbi-primary/20 rounded-lg p-3 mb-4">
                {demoMode ? (
                  <div className="text-center">
                    <p className="text-xs text-idbi-primary font-medium">
                      Demo Mode - Use OTP: <span className="font-mono font-bold text-idbi-accent text-sm">123456</span>
                    </p>
                    <p className="text-xs text-gray-500 mt-1">
                      For hackathon demo. Real OTP also sent if email is verified.
                    </p>
                  </div>
                ) : (
                  <p className="text-xs text-idbi-primary text-center">
                    A 6-digit OTP has been sent to your email. Check inbox/spam.
                  </p>
                )}
              </div>

              {error && (
                <p className="text-red-500 text-xs mb-3">{error}</p>
              )}

              <button
                type="submit"
                disabled={loading || otp.length < 6}
                className="btn-primary w-full disabled:opacity-50"
              >
                {loading ? 'Verifying...' : 'Verify & Login'}
              </button>

              <div className="flex items-center justify-between mt-4">
                <button
                  type="button"
                  onClick={() => { setStep('email'); setOtp(''); setError(''); }}
                  className="text-sm text-idbi-primary hover:underline"
                >
                  Change email
                </button>
                <button
                  type="button"
                  onClick={handleSendOtp}
                  className="text-sm text-idbi-accent hover:underline"
                >
                  Resend OTP
                </button>
              </div>
            </motion.form>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 pb-4">
          <div className="border-t border-gray-100 pt-3 flex items-center justify-center gap-2">
            <div className="w-2 h-2 bg-idbi-accent rounded-full" />
            <div className="w-2 h-2 bg-idbi-primary rounded-full" />
            <span className="text-xs text-gray-400 ml-2">IDBI Innovate 2026</span>
          </div>
        </div>
      </motion.div>
    </div>
  )
}
