import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { FlaskConical, CheckCircle2, XCircle } from 'lucide-react';
import { SpotlightCard } from '../components/SpotlightCard';

export function ResearchLab() {
  const [backtests, setBacktests] = useState([]);

  useEffect(() => {
    fetch('http://127.0.0.1:8080/api/backtests')
      .then(res => res.json())
      .then(data => setBacktests(data))
      .catch(console.error);
  }, []);

  return (
    <div className="animate-in fade-in duration-500">
      <div className="mb-8">
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <FlaskConical className="text-alpaca-yellow" /> Backtest & Research Lab
        </h1>
        <p className="text-alpaca-muted mt-2">Data-driven strategy selection. Showing 4 evaluated algorithms.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Rejected Strategies List */}
        <div className="lg:col-span-1 space-y-4">
          <h2 className="text-xl font-bold mb-4 border-b border-alpaca-border pb-2">Evaluated Strategies</h2>
          {backtests.map((strat, idx) => (
            <motion.div 
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: idx * 0.1 }}
              key={idx}
            >
              <div className={`p-4 rounded-lg border ${strat.selected ? 'bg-alpaca-yellow/10 border-alpaca-yellow' : 'bg-alpaca-panel border-alpaca-border opacity-70'}`}>
                <div className="flex justify-between items-center mb-2">
                  <h3 className={`font-bold ${strat.selected ? 'text-alpaca-yellow' : 'text-white'}`}>{strat.name}</h3>
                  {strat.selected ? <CheckCircle2 className="text-alpaca-yellow" size={18} /> : <XCircle className="text-negative" size={18} />}
                </div>
                <div className="text-sm font-medium">
                  {strat.selected ? (
                    <span className="text-positive">Deployed to Production</span>
                  ) : (
                    <span className="text-negative">Rejected: Underperformed target metrics</span>
                  )}
                </div>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Strategy Comparison Table */}
        <div className="lg:col-span-2">
          <SpotlightCard className="h-full">
            <h2 className="text-xl font-bold mb-6">Performance Comparison Matrix</h2>
            <div className="overflow-x-auto">
              <table className="w-full text-left">
                <thead>
                  <tr className="border-b border-alpaca-border text-alpaca-muted text-sm uppercase">
                    <th className="pb-3">Strategy</th>
                    <th className="pb-3">Win Rate</th>
                    <th className="pb-3">Profit Factor</th>
                    <th className="pb-3">Expectancy</th>
                    <th className="pb-3">Total Return</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-alpaca-border/50">
                  {backtests.map((strat, idx) => (
                    <tr key={idx} className={strat.selected ? 'bg-white/5' : ''}>
                      <td className={`py-4 font-bold ${strat.selected ? 'text-alpaca-yellow' : ''}`}>{strat.name}</td>
                      <td className="py-4">{strat.winRate}%</td>
                      <td className="py-4">{strat.profitFactor}</td>
                      <td className={`py-4 font-medium ${strat.expectancy > 0 ? 'text-positive' : 'text-negative'}`}>
                        {strat.expectancy > 0 ? '+' : ''}${strat.expectancy}
                      </td>
                      <td className={`py-4 font-bold ${strat.return > 0 ? 'text-positive' : 'text-negative'}`}>
                        {strat.return > 0 ? '+' : ''}{strat.return}%
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="mt-8 pt-6 border-t border-alpaca-border text-sm text-alpaca-muted">
              <p><span className="text-white font-medium">Dataset:</span> Jan 1, 2024 — Aug 25, 2026</p>
              <p><span className="text-white font-medium">Symbols:</span> SPY, QQQ, NVDA, AAPL, TSLA</p>
              <p><span className="text-white font-medium">Timeframe:</span> 5-Minute Candles</p>
            </div>
          </SpotlightCard>
        </div>
        
      </div>
    </div>
  );
}
