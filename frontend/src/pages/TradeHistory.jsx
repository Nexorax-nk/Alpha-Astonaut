import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Clock } from 'lucide-react';

export function TradeHistory() {
  const [history, setHistory] = useState([]);

  useEffect(() => {
    fetch('http://127.0.0.1:8080/api/trade_history')
      .then(res => res.json())
      .then(data => setHistory(data))
      .catch(console.error);
  }, []);

  return (
    <div className="animate-in fade-in duration-500">
      <div className="mb-8">
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <Clock className="text-alpaca-yellow" /> Trade History
        </h1>
        <p className="text-alpaca-muted mt-2">Audit trail of all closed positions.</p>
      </div>

      <div className="bg-alpaca-panel border border-alpaca-border rounded-xl overflow-hidden shadow-2xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-alpaca-border bg-black/40">
                <th className="p-4 text-alpaca-muted font-semibold text-sm uppercase">Time</th>
                <th className="p-4 text-alpaca-muted font-semibold text-sm uppercase">Symbol</th>
                <th className="p-4 text-alpaca-muted font-semibold text-sm uppercase">Strategy</th>
                <th className="p-4 text-alpaca-muted font-semibold text-sm uppercase">Entry</th>
                <th className="p-4 text-alpaca-muted font-semibold text-sm uppercase">Exit</th>
                <th className="p-4 text-alpaca-muted font-semibold text-sm uppercase">P&L</th>
                <th className="p-4 text-alpaca-muted font-semibold text-sm uppercase">ROI</th>
                <th className="p-4 text-alpaca-muted font-semibold text-sm uppercase">Result</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-alpaca-border">
              {history.map((trade, idx) => (
                <motion.tr 
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: idx * 0.05 }}
                  key={idx} 
                  className="hover:bg-white/5 transition-colors cursor-pointer group"
                >
                  <td className="p-4 text-alpaca-muted">{trade.time}</td>
                  <td className="p-4 font-bold">{trade.symbol}</td>
                  <td className="p-4 text-sm">{trade.strategy}</td>
                  <td className="p-4 text-sm">${trade.entry.toFixed(2)}</td>
                  <td className="p-4 text-sm">${trade.exit.toFixed(2)}</td>
                  <td className={`p-4 font-bold ${trade.pnl > 0 ? 'text-positive' : 'text-negative'}`}>
                    {trade.pnl > 0 ? '+' : ''}${Math.abs(trade.pnl).toLocaleString()}
                  </td>
                  <td className={`p-4 text-sm font-medium ${trade.roi > 0 ? 'text-positive' : 'text-negative'}`}>
                    {trade.roi > 0 ? '+' : ''}{trade.roi}%
                  </td>
                  <td className="p-4">
                    <span className={`px-2 py-1 rounded font-bold text-xs ${trade.pnl > 0 ? 'bg-positive/10 text-positive' : 'bg-negative/10 text-negative'}`}>
                      {trade.pnl > 0 ? 'WIN' : 'LOSS'}
                    </span>
                  </td>
                </motion.tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
