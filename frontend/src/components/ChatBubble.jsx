import { motion } from 'framer-motion'

export default function ChatBubble({ message }) {
  const isUser = message.role === 'user'

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}
    >
      <div
        className={`max-w-[85%] px-4 py-3 rounded-2xl text-sm leading-relaxed whitespace-pre-line ${
          isUser
            ? 'bg-idbi-primary text-white rounded-br-sm'
            : 'bg-white text-gray-800 border border-gray-100 shadow-sm rounded-bl-sm'
        }`}
      >
        {message.content}

        {/* Agent badges for assistant messages */}
        {!isUser && message.agents && message.agents.length > 0 && (
          <div className="mt-2 pt-2 border-t border-gray-100 flex flex-wrap gap-1">
            {message.agents.map((agent) => (
              <span
                key={agent}
                className="px-2 py-0.5 bg-green-50 text-green-700 rounded-full text-[10px] font-medium"
              >
                ✓ {agent.replace('_', ' ')}
              </span>
            ))}
          </div>
        )}
      </div>
    </motion.div>
  )
}
