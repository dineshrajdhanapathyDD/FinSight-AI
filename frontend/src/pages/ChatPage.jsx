import { useState, useRef, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { Mic, MicOff, Send, BarChart3, Target, TrendingUp, ArrowLeft, Volume2, VolumeX } from 'lucide-react'
import { sendMessage } from '../api'
import Avatar from '../components/Avatar'
import ChatBubble from '../components/ChatBubble'

export default function ChatPage({ customer, language }) {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [isRecording, setIsRecording] = useState(false)
  const [sessionId, setSessionId] = useState(null)
  const [avatarSpeaking, setAvatarSpeaking] = useState(false)
  const [isMuted, setIsMuted] = useState(false)
  const [agentsActive, setAgentsActive] = useState([])
  const messagesEndRef = useRef(null)
  const recognitionRef = useRef(null)
  const navigate = useNavigate()

  useEffect(() => {
    if (!customer) {
      navigate('/')
      return
    }
    handleSend('hello')
  }, [])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSend = async (text) => {
    const messageText = text || input.trim()
    if (!messageText) return

    if (!text) setInput('')

    if (text !== 'hello') {
      setMessages((prev) => [...prev, { role: 'user', content: messageText }])
    }

    setIsLoading(true)
    setAgentsActive(['research_agent', 'compliance_agent', 'portfolio_agent'])

    try {
      const response = await sendMessage(customer.id, messageText, language, sessionId)
      setSessionId(response.session_id)
      setAgentsActive(response.agents_used || [])

      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: response.response, agents: response.agents_used },
      ])

      if (!isMuted) speakText(response.response)
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: 'I apologize, I encountered an issue. Please try again.' },
      ])
    } finally {
      setIsLoading(false)
      setTimeout(() => setAgentsActive([]), 2000)
    }
  }

  const speakText = (text) => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel() // Cancel any ongoing speech
      const utterance = new SpeechSynthesisUtterance(text)
      const langMap = { en: 'en-IN', hi: 'hi-IN', ta: 'ta-IN', te: 'te-IN', bn: 'bn-IN' }
      utterance.lang = langMap[language] || 'en-IN'
      utterance.rate = 0.9
      utterance.onstart = () => setAvatarSpeaking(true)
      utterance.onend = () => setAvatarSpeaking(false)
      window.speechSynthesis.speak(utterance)
    }
  }

  const toggleVoice = () => {
    if (isMuted) {
      setIsMuted(false)
    } else {
      setIsMuted(true)
      window.speechSynthesis.cancel()
      setAvatarSpeaking(false)
    }
  }

  const stopSpeaking = () => {
    window.speechSynthesis.cancel()
    setAvatarSpeaking(false)
  }

  const toggleRecording = () => {
    if (isRecording) {
      recognitionRef.current?.stop()
      setIsRecording(false)
      return
    }

    if (!('webkitSpeechRecognition' in window || 'SpeechRecognition' in window)) {
      alert('Speech recognition not supported in this browser. Use Chrome.')
      return
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
    const recognition = new SpeechRecognition()
    const langMap = { en: 'en-IN', hi: 'hi-IN', ta: 'ta-IN', te: 'te-IN', bn: 'bn-IN', mr: 'mr-IN' }
    recognition.lang = langMap[language] || 'en-IN'
    recognition.continuous = false
    recognition.interimResults = false

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript
      setInput(transcript)
      setIsRecording(false)
      setTimeout(() => handleSend(transcript), 300)
    }

    recognition.onerror = () => setIsRecording(false)
    recognition.onend = () => setIsRecording(false)

    recognition.start()
    recognitionRef.current = recognition
    setIsRecording(true)
  }

  const handleBack = () => {
    stopSpeaking()
    navigate('/')
  }

  const quickActions = [
    { icon: <BarChart3 size={16} />, label: 'Portfolio', msg: 'Show my portfolio' },
    { icon: <Target size={16} />, label: 'Goals', msg: 'Show my financial goals' },
    { icon: <TrendingUp size={16} />, label: 'Market', msg: 'Market update' },
  ]

  return (
    <div className="h-screen flex flex-col bg-gradient-to-b from-gray-50 to-gray-100">
      {/* Header with Back + Voice controls */}
      <div className="bg-gradient-to-r from-idbi-primary to-idbi-secondary px-4 py-3 flex items-center justify-between shadow-lg">
        <button onClick={handleBack} className="text-white/90 hover:text-white flex items-center gap-1 text-sm">
          <ArrowLeft size={18} />
          Back
        </button>
        <div className="text-center">
          <h1 className="text-white font-semibold text-sm">Dhan Sakhi</h1>
          <p className="text-blue-200 text-xs">AI Wealth Advisor</p>
        </div>
        <div className="flex items-center gap-2">
          {/* Voice Play/Pause */}
          <button
            onClick={toggleVoice}
            className={`w-8 h-8 rounded-full flex items-center justify-center transition-all ${
              isMuted ? 'bg-red-500/20 text-red-300' : 'bg-white/20 text-white'
            }`}
            title={isMuted ? 'Unmute voice' : 'Mute voice'}
          >
            {isMuted ? <VolumeX size={16} /> : <Volume2 size={16} />}
          </button>
          {/* Portfolio */}
          <button onClick={() => navigate('/portfolio')} className="text-white/80 hover:text-white">
            <BarChart3 size={20} />
          </button>
        </div>
      </div>

      {/* Avatar Section */}
      <div className="flex-shrink-0 py-3">
        <Avatar speaking={avatarSpeaking} agentsActive={agentsActive} />
        {/* Stop Speaking Button (visible when avatar is speaking) */}
        {avatarSpeaking && (
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            className="flex justify-center mt-2"
          >
            <button
              onClick={stopSpeaking}
              className="px-4 py-1.5 bg-red-50 border border-red-200 text-red-600 rounded-full text-xs font-medium hover:bg-red-100 transition-all"
            >
              Stop Speaking
            </button>
          </motion.div>
        )}
      </div>

      {/* Agent Activity */}
      <AnimatePresence>
        {agentsActive.length > 0 && isLoading && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="px-4 pb-2"
          >
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-2 flex items-center gap-2 text-xs text-blue-700">
              <div className="flex gap-1">
                <span className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" />
                <span className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                <span className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
              </div>
              Agents working: {agentsActive.map(a => a.replace('_', ' ')).join(', ')}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 space-y-3 pb-4">
        {messages.map((msg, i) => (
          <ChatBubble key={i} message={msg} />
        ))}
        {isLoading && (
          <div className="flex gap-2 items-center text-gray-400 text-sm pl-2">
            <div className="flex gap-1">
              <span className="w-2 h-2 bg-gray-300 rounded-full animate-bounce" />
              <span className="w-2 h-2 bg-gray-300 rounded-full animate-bounce" style={{ animationDelay: '0.15s' }} />
              <span className="w-2 h-2 bg-gray-300 rounded-full animate-bounce" style={{ animationDelay: '0.3s' }} />
            </div>
            Thinking...
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Quick Actions */}
      <div className="px-4 pb-2 flex gap-2">
        {quickActions.map((action) => (
          <button
            key={action.label}
            onClick={() => handleSend(action.msg)}
            className="flex items-center gap-1 px-3 py-1.5 bg-white border border-gray-200 rounded-full text-xs text-gray-600 hover:bg-idbi-light hover:border-idbi-accent transition-all"
          >
            {action.icon}
            {action.label}
          </button>
        ))}
      </div>

      {/* Input Area */}
      <div className="p-4 bg-white border-t border-gray-200 shadow-lg">
        <div className="flex items-center gap-3">
          <button
            onClick={toggleRecording}
            className={`w-12 h-12 rounded-full flex items-center justify-center transition-all ${
              isRecording
                ? 'bg-red-500 text-white recording-pulse'
                : 'bg-gray-100 text-gray-600 hover:bg-idbi-light hover:text-idbi-primary'
            }`}
          >
            {isRecording ? <MicOff size={20} /> : <Mic size={20} />}
          </button>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            placeholder={language === 'hi' ? 'टाइप करें या बोलें...' : 'Type or speak...'}
            className="flex-1 px-4 py-3 bg-gray-50 rounded-xl border border-gray-200 focus:border-idbi-accent focus:ring-2 focus:ring-idbi-accent/20 outline-none text-sm"
          />
          <button
            onClick={() => handleSend()}
            disabled={!input.trim() || isLoading}
            className="w-12 h-12 bg-idbi-primary text-white rounded-full flex items-center justify-center hover:bg-idbi-secondary transition-all disabled:opacity-50"
          >
            <Send size={18} />
          </button>
        </div>
      </div>
    </div>
  )
}
