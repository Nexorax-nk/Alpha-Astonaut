import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Search } from 'lucide-react';

export function MarketScanner() {
  const [scans, setScans] = useState([]);

  useEffect(() => {
    // Fetch mock scanner data
    fetch('http://127.0.0.1:8080/api/scanner')
      .then(res => res.json())
      .then(data => setScans(data))
      .catch(console.error);
  }, []);

  return (
    <div className="animate-in fade-in duration-500">
      <div className="mb-8">
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <Search className="text-alpaca-yellow" /> Live Market Scanner
        </h1>
        <p className="text-alpaca-muted mt-2">Real-time quantitative analysis of market breadth, momentum, and volume anomalies.</p>
      </div>

      <div className="bg-alpaca-panel border border-alpaca-border rounded-xl overflow-hidden shadow-2xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-alpaca-border bg-black/40">
                <th className="p-4 text-alpaca-muted font-semibold text-sm uppercase">Symbol</th>
                <th className="p-4 text-alpaca-muted font-semibold text-sm uppercase">Price</th>
                <th className="p-4 text-alpaca-muted font-semibold text-sm uppercase">Change</th>
                <th className="p-4 text-alpaca-muted font-semibold text-sm uppercase">RVOL</th>
                <th className="p-4 text-alpaca-muted font-semibold text-sm uppercase">VWAP</th>
                <th className="p-4 text-alpaca-muted font-semibold text-sm uppercase">ATR</th>
                <th className="p-4 text-alpaca-muted font-semibold text-sm uppercase">Signal</th>
                <th className="p-4 text-alpaca-muted font-semibold text-sm uppercase">Score</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-alpaca-border">
              {scans.map((scan, idx) => (
                <motion.tr 
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: idx * 0.05 }}
                  key={idx} 
                  className="hover:bg-white/5 transition-colors"
                >
                  <td className="p-4 font-bold text-lg">{scan.symbol}</td>
                  <td className="p-4">${scan.price.toFixed(2)}</td>
                  <td className={`p-4 font-medium ${scan.change > 0 ? 'text-positive' : 'text-negative'}`}>
                    {scan.change > 0 ? '+' : ''}{scan.change}%
                  </td>
                  <td className="p-4">{scan.rvol}x</td>
                  <td className="p-4 text-alpaca-muted">{scan.vwap}</td>
                  <td className="p-4 text-alpaca-muted">{scan.atr}</td>
                  <td className="p-4">
                    {scan.signal === 'CALL' && <span className="bg-positive/10 text-positive px-2 py-1 rounded font-bold text-xs">🟢 CALL</span>}
                    {scan.signal === 'PUT' && <span className="bg-negative/10 text-negative px-2 py-1 rounded font-bold text-xs">🔴 PUT</span>}
                    {scan.signal === 'WAIT' && <span className="bg-alpaca-muted/10 text-alpaca-muted px-2 py-1 rounded font-bold text-xs">⚪ WAIT</span>}
                  </td>
                  <td className="p-4">
                    <div className="flex items-center gap-2">
                      <div className="flex-1 h-2 bg-black rounded-full overflow-hidden w-16">
                        <div 
                          className={`h-full ${scan.score > 80 ? 'bg-positive' : scan.score > 50 ? 'bg-alpaca-yellow' : 'bg-alpaca-muted'}`} 
                          style={{ width: `${scan.score}%` }}
                        />
                      </div>
                      <span className="font-bold text-sm">{scan.score}</span>
                    </div>
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
