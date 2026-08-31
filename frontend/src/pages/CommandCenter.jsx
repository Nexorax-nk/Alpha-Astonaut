import React from 'react';
import { motion } from 'framer-motion';
import { Activity, Briefcase, TrendingUp, Cpu } from 'lucide-react';
import { SpotlightCard } from '../components/SpotlightCard';
import { PerformanceChart } from '../components/PerformanceChart';

export function CommandCenter({ performance, stats }) {
  const currentEquity = performance.length > 0 ? performance[performance.length - 1].pnl : 100000;
  const startEquity = performance.length > 0 ? performance[0].pnl : 100000;
  const pnlPercent = (((currentEquity - startEquity) / startEquity) * 100).toFixed(2);
  const realizedPnl = currentEquity - startEquity;

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      {/* HERO METRICS */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <SpotlightCard>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-alpaca-muted text-sm font-semibold uppercase tracking-wider">Account Value</h3>
            <Briefcase size={20} className="text-alpaca-yellow" />
          </div>
          <p className="text-4xl font-bold mb-2">${currentEquity.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</p>
          <p className={`text-sm font-medium ${realizedPnl >= 0 ? 'text-positive' : 'text-negative'}`}>
            {realizedPnl >= 0 ? '+' : ''}${Math.abs(realizedPnl).toLocaleString()} ({pnlPercent}%)
          </p>
        </SpotlightCard>

        <SpotlightCard>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-alpaca-muted text-sm font-semibold uppercase tracking-wider">Win Rate</h3>
            <Activity size={20} className="text-alpaca-yellow" />
          </div>
          <p className="text-4xl font-bold mb-2">61.4%</p>
          <p className="text-sm font-medium text-alpaca-muted">Profit Factor: 1.63</p>
        </SpotlightCard>

        <SpotlightCard>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-alpaca-muted text-sm font-semibold uppercase tracking-wider">Active Trades</h3>
            <TrendingUp size={20} className="text-alpaca-yellow" />
          </div>
          <p className="text-4xl font-bold mb-2">4</p>
          <p className="text-sm font-medium text-alpaca-muted">Unrealized: <span className="text-positive">+$412</span></p>
        </SpotlightCard>

        <SpotlightCard className="bg-black border-alpaca-yellow/30">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-alpaca-yellow text-sm font-semibold uppercase tracking-wider">Agent Status</h3>
            <span className="relative flex h-3 w-3">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-positive opacity-75"></span>
              <span className="relative inline-flex rounded-full h-3 w-3 bg-positive"></span>
            </span>
          </div>
          <p className="text-2xl font-bold mb-2 text-white">ONLINE</p>
          <div className="space-y-1 text-xs text-alpaca-muted">
            <p>Market: <span className="text-white">OPEN</span></p>
            <p>Last scan: <span className="text-white">14:32:18</span></p>
            <p>Next scan: <span className="text-white">14:33:18</span></p>
          </div>
        </SpotlightCard>
      </div>

      {/* PERFORMANCE CHART */}
      <div className="bg-alpaca-panel border border-alpaca-border rounded-xl p-6 shadow-2xl">
        <div className="mb-6">
          <h2 className="text-xl font-bold">Equity Curve</h2>
          <p className="text-alpaca-muted text-sm mt-1">Real-time portfolio value pulled directly from Brokerage API.</p>
        </div>
        {performance.length > 0 ? (
          <PerformanceChart data={performance} />
        ) : (
          <div className="h-[300px] flex items-center justify-center text-alpaca-muted border border-dashed border-alpaca-border rounded-lg">
            Awaiting portfolio data...
          </div>
        )}
      </div>
    </div>
  );
}
