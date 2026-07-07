import { motion } from 'framer-motion'

export default function Avatar({ speaking, agentsActive }) {
  return (
    <div className="flex flex-col items-center">
      {/* Avatar Circle */}
      <div className="relative">
        {/* Glow ring when speaking */}
        {speaking && (
          <motion.div
            className="absolute inset-0 rounded-full bg-idbi-accent/30"
            animate={{ scale: [1, 1.2, 1], opacity: [0.5, 0.2, 0.5] }}
            transition={{ duration: 1.5, repeat: Infinity }}
          />
        )}

        {/* Avatar container */}
        <motion.div
          animate={speaking ? { scale: [1, 1.03, 1] } : {}}
          transition={{ duration: 0.8, repeat: speaking ? Infinity : 0 }}
          className="w-28 h-28 rounded-full overflow-hidden border-4 border-white shadow-xl avatar-glow relative"
        >
          {/* Animated avatar face */}
          <div className="w-full h-full bg-gradient-to-br from-idbi-primary to-idbi-secondary flex items-center justify-center">
            <div className="text-center">
              {/* Simple animated face */}
              <div className="relative">
                <span className="text-5xl">
                  {speaking ? '🗣️' : '👩‍💼'}
                </span>
              </div>
            </div>
          </div>

          {/* Speaking indicator overlay */}
          {speaking && (
            <div className="absolute bottom-0 left-0 right-0 h-8 bg-gradient-to-t from-idbi-accent/50 to-transparent flex items-end justify-center pb-1">
              <div className="flex gap-0.5 items-end">
                {[...Array(5)].map((_, i) => (
                  <motion.div
                    key={i}
                    className="w-1 bg-white rounded-full"
                    animate={{ height: ['4px', '16px', '4px'] }}
                    transition={{
                      duration: 0.6,
                      repeat: Infinity,
                      delay: i * 0.1,
                    }}
                  />
                ))}
              </div>
            </div>
          )}
        </motion.div>

        {/* Status dot */}
        <div className="absolute bottom-1 right-1 w-4 h-4 bg-green-500 rounded-full border-2 border-white" />
      </div>

      {/* Agent indicators */}
      {agentsActive.length > 0 && (
        <div className="mt-3 flex gap-1">
          {agentsActive.map((agent) => (
            <motion.div
              key={agent}
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              className="px-2 py-0.5 bg-idbi-light text-idbi-primary rounded-full text-[10px] font-medium"
            >
              {agent.replace('_agent', '').replace('_', ' ')}
            </motion.div>
          ))}
        </div>
      )}
    </div>
  )
}
