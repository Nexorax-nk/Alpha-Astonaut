import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Layers } from 'lucide-react';
import { SpotlightCard } from '../components/SpotlightCard';

export function LivePositions() {
  const [positions, setPositions] = useState([]);

  useEffect(() => {
    fetch('http://127.0.0.1:8080/api/live_positions')
      .then(res => res.json())
      .then(data => setPositions(data))
      .catch(console.error);
  }, []);

  return (
    <div className="animate-in fade-in duration-500">
      <div className="mb-8">
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <Layers className="text-alpaca-yellow" /> Live Positions
        </h1>
        <p className="text-alpaca-muted mt-2">Active trades currently being managed by the risk engine.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {positions.map((pos, idx) => (
          <motion.div 
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: idx * 0.1 }}
            key={idx}
          >
            <SpotlightCard className="h-full flex flex-col">
              <div className="flex justify-between items-start mb-6">
                <div>
                  <h2 className="text-2xl font-bold">{pos.symbol}</h2>
                  <p className="text-alpaca-yellow font-medium text-sm">{pos.strike}</p>
                </div>
                <span className={`px-2 py-1 rounded text-xs font-bold bg-positive/10 text-positive`}>
                  🟢 HOLD
                </span>
              </div>

              <div className="space-y-4 mb-6 flex-1">
                <div className="flex justify-between">
                  <span className="text-alpaca-muted text-sm">Entry:</span>
                  <span className="font-medium">${pos.entry.toFixed(2)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-alpaca-muted text-sm">Current:</span>
                  <span className="font-bold">${pos.current.toFixed(2)}</span>
                </div>
                <div className="flex justify-between border-b border-alpaca-border/50 pb-4">
                  <span className="text-alpaca-muted text-sm">P&L:</span>
                  <span className={`font-bold ${pos.pnl > 0 ? 'text-positive' : 'text-negative'}`}>
                    {pos.pnl > 0 ? '+' : ''}${Math.abs(pos.pnl).toLocaleString()} ({pos.roi}%)
                  </span>
                </div>
                
                <div className="flex justify-between">
                  <span className="text-alpaca-muted text-sm">Risk (Max Loss):</span>
                  <span className="font-medium">${pos.risk.toLocaleString()}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-alpaca-muted text-sm">Max Profit (Target):</span>
                  <span className="font-medium text-positive">${pos.maxProfit.toLocaleString()}</span>
                </div>
              </div>

              <div className="bg-black/40 rounded p-3 flex justify-between items-center mt-auto">
                <span className="text-alpaca-muted text-xs">Time Held:</span>
                <span className="text-sm font-bold text-white">{pos.timeHeld}</span>
              </div>
            </SpotlightCard>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
