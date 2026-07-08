import axios from 'axios'

// Use environment variable for production (Lambda), fallback to proxy for local dev
const API_BASE = import.meta.env.VITE_API_URL
  ? `${import.meta.env.VITE_API_URL}/api`
  : '/api'

const api = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
})

export async function sendMessage(customerId, message, language, sessionId) {
  const response = await api.post('/chat/message', {
    customer_id: customerId,
    message,
    language,
    session_id: sessionId,
  })
  return response.data
}

export async function getPortfolio(customerId) {
  const response = await api.get(`/portfolio/${customerId}`)
  return response.data
}

export async function getPortfolioAnalysis(customerId) {
  const response = await api.get(`/portfolio/${customerId}/analysis`)
  return response.data
}

export async function getMarketData() {
  const response = await api.get('/portfolio/market')
  return response.data
}

export async function getRecommendations(customerId, goal, amount, duration) {
  const response = await api.post('/recommendations/generate', {
    customer_id: customerId,
    goal,
    amount,
    duration_months: duration,
  })
  return response.data
}

export async function textToSpeech(text, language) {
  const response = await api.post('/speech/tts', { text, language })
  return response.data
}

export async function sendOtp(email) {
  const response = await api.post('/auth/send-otp', { email })
  return response.data
}

export async function verifyOtp(email, otp) {
  const response = await api.post('/auth/verify-otp', { email, otp })
  return response.data
}

export default api
