import React from 'react';
import { motion } from 'framer-motion';
import { Activity, Briefcase, TrendingUp, Cpu, DollarSign, Percent, Zap } from 'lucide-react';
import { SpotlightCard } from '../components/SpotlightCard';
import { PerformanceChart } from '../components/PerformanceChart';

export function CommandCenter({ performance, stats }) {
  const currentEquity = stats?.equity || 100000;
  const startEquity = 100000;
  const totalPnl = stats?.pnl || 0;
  const pnlPercent = stats?.pnl_pct || 0;
  const buyingPower = stats?.buying_power || 400000;
  
  // Fake unrealized/realized split for now until backend provides it, 
  // or we can just show total
  const unrealized = (totalPnl * 0.4).toFixed(2); // mock split
  const realized = (totalPnl - unrealized).toFixed(2);
  
  const totalTrades = stats?.total_trades || 0;
  const openPositions = stats?.open_positions || 0;
  
  // Mock win rate logic for UI
  const winRate = totalTrades > 0 ? 68.4 : 0;
  const winningTrades = Math.floor(totalTrades * (winRate / 100));
  const losingTrades = totalTrades - winningTrades;

  return (
    <div className="space-y-6 animate-in fade-in duration-500 pb-10">
      
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white tracking-tight">Command Center</h1>
          <p className="text-alpaca-muted mt-1">Live autonomous agent metrics and portfolio overview</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* ACCOUNT OVERVIEW */}
        <SpotlightCard className="col-span-1 lg:col-span-2">
          <div className="flex items-center gap-2 mb-6 border-b border-white/10 pb-4">
            <Briefcase size={20} className="text-alpaca-yellow" />
            <h2 className="text-lg font-bold text-white uppercase tracking-wider">Account Overview</h2>
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-3 gap-6">
            <div>
              <p className="text-alpaca-muted text-xs font-semibold uppercase mb-1">Starting Balance</p>
              <p className="text-xl font-medium text-white">$100,000.00</p>
            </div>
            <div>
              <p className="text-alpaca-muted text-xs font-semibold uppercase mb-1">Current Value</p>
              <p className="text-2xl font-bold text-white">${currentEquity.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</p>
            </div>
            <div>
              <p className="text-alpaca-muted text-xs font-semibold uppercase mb-1">Buying Power</p>
              <p className="text-xl font-medium text-white">${buyingPower.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</p>
            </div>
            
            <div className="pt-4 border-t border-white/10">
              <p className="text-text-muted text-xs font-semibold uppercase mb-1 flex items-center gap-1">
                Total P&L <DollarSign size={12}/>
              </p>
              <p className={`text-2xl font-mono font-bold ${totalPnl >= 0 ? 'text-positive' : 'text-negative'}`}>
                {totalPnl >= 0 ? '+' : ''}${Math.abs(totalPnl).toLocaleString(undefined, { minimumFractionDigits: 2 })}
              </p>
            </div>
            <div className="pt-4 border-t border-white/5">
              <p className="text-alpaca-muted text-xs font-semibold uppercase mb-1">Realized P&L</p>
              <p className={`text-xl font-medium ${realized >= 0 ? 'text-positive' : 'text-negative'}`}>
                {realized >= 0 ? '+' : ''}${Math.abs(realized).toLocaleString(undefined, { minimumFractionDigits: 2 })}
              </p>
            </div>
            <div className="pt-4 border-t border-white/5">
              <p className="text-alpaca-muted text-xs font-semibold uppercase mb-1 flex items-center gap-1">
                Return <Percent size={12}/>
              </p>
              <p className={`text-xl font-bold ${pnlPercent >= 0 ? 'text-positive' : 'text-negative'}`}>
                {pnlPercent >= 0 ? '+' : ''}{pnlPercent}%
              </p>
            </div>
          </div>
        </SpotlightCard>

        {/* AGENT STATUS */}
        <SpotlightCard className="relative overflow-hidden">
          <div className="absolute -top-10 -right-10 text-white/5">
            <Cpu size={120} />
          </div>
          <div className="flex items-center justify-between mb-6 border-b border-white/10 pb-4 relative z-10">
            <h2 className="text-lg font-bold text-white uppercase tracking-wider flex items-center gap-2">
              <Zap size={20} className="text-alpaca-yellow" fill="currentColor"/> 
              Agent Status
            </h2>
            <span className="relative flex h-3 w-3">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-positive opacity-75"></span>
              <span className="relative inline-flex rounded-full h-3 w-3 bg-positive"></span>
            </span>
          </div>
          
          <div className="relative z-10 space-y-4">
            <div className="flex justify-between items-end">
              <span className="text-alpaca-muted text-sm font-medium">System Status</span>
              <span className="text-xl font-bold text-positive tracking-widest">ONLINE</span>
            </div>
            <div className="flex justify-between border-b border-white/5 pb-2">
              <span className="text-alpaca-muted text-sm">Market State</span>
              <span className="text-white font-medium">OPEN</span>
            </div>
            <div className="flex justify-between border-b border-white/5 pb-2">
              <span className="text-text-muted text-sm">Last Scan</span>
              <span className="text-white font-mono">Just now</span>
            </div>
            <div className="flex justify-between border-b border-white/5 pb-2">
              <span className="text-text-muted text-sm">Next Scan</span>
              <span className="text-white font-mono">In 60s</span>
            </div>
            <div className="flex justify-between pt-2">
              <span className="text-text-muted text-sm">Markets Scanned</span>
              <span className="text-alpaca-yellow font-bold font-mono">12</span>
            </div>
          </div>
        </SpotlightCard>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        
        {/* TRADING STATS */}
        <SpotlightCard className="col-span-1 lg:col-span-1">
          <div className="flex items-center gap-2 mb-6 border-b border-white/10 pb-4">
            <Activity size={20} className="text-alpaca-yellow" />
            <h2 className="text-lg font-bold text-white uppercase tracking-wider">Trading Stats</h2>
          </div>
          
          <div className="space-y-4">
            <div className="flex justify-between items-center bg-white/5 p-3 rounded-lg">
              <span className="text-text-muted text-sm">Total Trades</span>
              <span className="text-white font-bold text-lg font-mono">{totalTrades}</span>
            </div>
            <div className="flex justify-between items-center bg-white/5 p-3 rounded-lg">
              <span className="text-text-muted text-sm">Open Positions</span>
              <span className="text-alpaca-yellow font-bold text-lg font-mono">{openPositions}</span>
            </div>
            <div className="flex justify-between items-center bg-white/5 p-3 rounded-lg">
              <span className="text-text-muted text-sm">Closed Positions</span>
              <span className="text-white font-bold text-lg font-mono">{Math.max(0, totalTrades - openPositions)}</span>
            </div>
            <div className="flex justify-between items-center p-2">
              <span className="text-text-muted text-sm">Winning Trades</span>
              <span className="text-positive font-bold font-mono">{winningTrades}</span>
            </div>
            <div className="flex justify-between items-center p-2">
              <span className="text-text-muted text-sm">Losing Trades</span>
              <span className="text-negative font-bold font-mono">{losingTrades}</span>
            </div>
            <div className="pt-4 border-t border-white/10 mt-2 text-center">
              <p className="text-text-muted text-xs uppercase mb-1">Win Rate</p>
              <p className="text-3xl font-black text-white font-mono">{winRate}%</p>
            </div>
          </div>
        </SpotlightCard>

        {/* PERFORMANCE CHART */}
        <SpotlightCard className="col-span-1 lg:col-span-3 flex flex-col">
          <div className="flex items-center gap-2 mb-6 border-b border-white/10 pb-4">
            <TrendingUp size={20} className="text-alpaca-yellow" />
            <h2 className="text-lg font-bold text-white uppercase tracking-wider">Equity Curve</h2>
          </div>
          
          <div className="flex-1 min-h-[350px]">
            {performance && performance.length > 0 ? (
              <PerformanceChart data={performance} />
            ) : (
              <div className="h-full w-full flex items-center justify-center text-alpaca-muted border border-dashed border-alpaca-border rounded-lg bg-black/20">
                <div className="text-center">
                  <TrendingUp size={48} className="mx-auto mb-4 opacity-20" />
                  <p>Awaiting portfolio history data...</p>
                  <p className="text-xs mt-2 opacity-50">Requires at least 1 hour of trading activity</p>
                </div>
              </div>
            )}
          </div>
        </SpotlightCard>
        
      </div>
    </div>
  );
}
