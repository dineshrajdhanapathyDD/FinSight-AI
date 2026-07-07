import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { ArrowLeft, TrendingUp, PieChart, Target, AlertCircle, CheckCircle } from 'lucide-react'
import { getPortfolio, getPortfolioAnalysis } from '../api'

export default function PortfolioPage({ customer }) {
  const [portfolio, setPortfolio] = useState(null)
  const [analysis, setAnalysis] = useState(null)
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    if (!customer) {
      navigate('/')
      return
    }
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const [portData, analysisData] = await Promise.all([
        getPortfolio(customer.id),
        getPortfolioAnalysis(customer.id),
      ])
      setPortfolio(portData)
      setAnalysis(analysisData.analysis)
    } catch (error) {
      console.error('Failed to load portfolio:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-idbi-primary border-t-transparent rounded-full animate-spin mx-auto" />
          <p className="mt-4 text-gray-500">Loading portfolio...</p>
        </div>
      </div>
    )
  }

  if (!portfolio) return null

  const { portfolio: p, goals } = portfolio

  return (
    <div className="min-h-screen bg-gray-50 pb-8">
      {/* Header */}
      <div className="bg-gradient-to-r from-idbi-primary to-idbi-secondary px-4 py-4">
        <div className="flex items-center justify-between mb-4">
          <button onClick={() => navigate('/chat')} className="text-white/80 hover:text-white">
            <ArrowLeft size={20} />
          </button>
          <h1 className="text-white font-semibold">Portfolio Dashboard</h1>
          <div />
        </div>

        {/* Portfolio Value Card */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white/10 backdrop-blur-sm rounded-2xl p-4 text-white"
        >
          <p className="text-blue-200 text-sm">Total Portfolio Value</p>
          <h2 className="text-3xl font-bold mt-1">₹{p.total_value.toLocaleString('en-IN')}</h2>
          <div className="flex items-center gap-2 mt-2">
            <TrendingUp size={16} className="text-green-300" />
            <span className="text-green-300 font-medium">+{p.returns_pct}%</span>
            <span className="text-blue-200 text-sm">(₹{p.returns_abs.toLocaleString('en-IN')})</span>
          </div>
        </motion.div>
      </div>

      <div className="px-4 -mt-2 space-y-4">
        {/* Asset Allocation */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="card"
        >
          <div className="flex items-center gap-2 mb-4">
            <PieChart size={18} className="text-idbi-primary" />
            <h3 className="font-semibold text-gray-800">Asset Allocation</h3>
          </div>
          <div className="space-y-3">
            {Object.entries(p.allocation).map(([asset, pct]) => (
              <div key={asset} className="flex items-center gap-3">
                <span className="text-sm text-gray-600 w-16 capitalize">{asset}</span>
                <div className="flex-1 bg-gray-100 rounded-full h-4 overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${pct}%` }}
                    transition={{ duration: 1, delay: 0.3 }}
                    className={`h-full rounded-full ${
                      asset === 'equity' ? 'bg-blue-500' :
                      asset === 'debt' ? 'bg-green-500' : 'bg-yellow-500'
                    }`}
                  />
                </div>
                <span className="text-sm font-medium text-gray-700 w-10">{pct}%</span>
              </div>
            ))}
          </div>
        </motion.div>

        {/* Holdings */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="card"
        >
          <h3 className="font-semibold text-gray-800 mb-4">Holdings</h3>
          <div className="space-y-3">
            {p.holdings.map((holding, i) => (
              <div key={i} className="flex items-center justify-between py-2 border-b border-gray-50 last:border-0">
                <div>
                  <p className="text-sm font-medium text-gray-800">{holding.name}</p>
                  <p className="text-xs text-gray-500">{holding.category}</p>
                </div>
                <div className="text-right">
                  <p className="text-sm font-medium">₹{holding.value.toLocaleString('en-IN')}</p>
                  <p className={`text-xs font-medium ${holding.returns_pct > 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {holding.returns_pct > 0 ? '+' : ''}{holding.returns_pct}%
                  </p>
                </div>
              </div>
            ))}
          </div>
        </motion.div>

        {/* AI Analysis */}
        {analysis && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="card"
          >
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-gray-800">AI Health Score</h3>
              <div className={`px-3 py-1 rounded-full text-sm font-bold ${
                analysis.health_score >= 80 ? 'bg-green-100 text-green-700' :
                analysis.health_score >= 60 ? 'bg-yellow-100 text-yellow-700' :
                'bg-red-100 text-red-700'
              }`}>
                {analysis.health_score}/100
              </div>
            </div>

            {analysis.strengths.length > 0 && (
              <div className="mb-3">
                <p className="text-xs font-medium text-green-700 mb-1">Strengths</p>
                {analysis.strengths.map((s, i) => (
                  <div key={i} className="flex items-start gap-2 text-sm text-gray-600 mb-1">
                    <CheckCircle size={14} className="text-green-500 mt-0.5 flex-shrink-0" />
                    {s}
                  </div>
                ))}
              </div>
            )}

            {analysis.concerns.length > 0 && (
              <div className="mb-3">
                <p className="text-xs font-medium text-orange-700 mb-1">Concerns</p>
                {analysis.concerns.map((c, i) => (
                  <div key={i} className="flex items-start gap-2 text-sm text-gray-600 mb-1">
                    <AlertCircle size={14} className="text-orange-500 mt-0.5 flex-shrink-0" />
                    {c}
                  </div>
                ))}
              </div>
            )}

            {analysis.suggestions.length > 0 && (
              <div>
                <p className="text-xs font-medium text-blue-700 mb-1">Suggestions</p>
                {analysis.suggestions.map((s, i) => (
                  <div key={i} className="flex items-start gap-2 text-sm text-gray-600 mb-1">
                    <Target size={14} className="text-blue-500 mt-0.5 flex-shrink-0" />
                    {s}
                  </div>
                ))}
              </div>
            )}
          </motion.div>
        )}

        {/* Goals */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="card"
        >
          <div className="flex items-center gap-2 mb-4">
            <Target size={18} className="text-idbi-primary" />
            <h3 className="font-semibold text-gray-800">Financial Goals</h3>
          </div>
          <div className="space-y-3">
            {goals.map((goal, i) => (
              <div key={i} className="p-3 bg-gray-50 rounded-xl">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-800">{goal.name}</span>
                  <span className="text-xs text-gray-500">{goal.timeline_years} years</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-idbi-primary font-semibold">
                    ₹{goal.target.toLocaleString('en-IN')}
                  </span>
                  <div className="w-24 bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-idbi-accent rounded-full h-2"
                      style={{ width: `${Math.min(100, Math.random() * 60 + 20)}%` }}
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </motion.div>
      </div>
    </div>
  )
}
