import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Home, Search, Layers, Clock, FlaskConical, Terminal, Rocket } from 'lucide-react';
import { CommandCenter } from './pages/CommandCenter';
import { MarketScanner } from './pages/MarketScanner';
import { LivePositions } from './pages/LivePositions';
import { TradeHistory } from './pages/TradeHistory';
import { ResearchLab } from './pages/ResearchLab';
import { ActivityLog } from './pages/ActivityLog';

function App() {
  const [activeTab, setActiveTab] = useState('command');
  const [performance, setPerformance] = useState([]);
  const [stats, setStats] = useState({ total_trades: 0, status: 'Active' });

  useEffect(() => {
    // Only fetch global data needed for layout/header here
    Promise.all([
      fetch('http://127.0.0.1:8080/api/stats'),
      fetch('http://127.0.0.1:8080/api/performance')
    ])
    .then(async ([resStats, resPerf]) => {
      setStats(await resStats.json());
      setPerformance(await resPerf.json());
    })
    .catch(console.error);
  }, []);

  const navItems = [
    { id: 'command', label: 'Command Center', icon: Home },
    { id: 'scanner', label: 'Market Scanner', icon: Search },
    { id: 'positions', label: 'Live Positions', icon: Layers },
    { id: 'history', label: 'Trade History', icon: Clock },
    { id: 'research', label: 'Research Lab', icon: FlaskConical },
    { id: 'activity', label: 'Agent Log', icon: Terminal },
  ];

  return (
    <div 
      className="flex h-screen text-black font-sans overflow-hidden selection:bg-alpaca-yellow selection:text-black bg-app-bg"
      style={{
        backgroundImage: 'url(/bg-candles.jpg)',
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        backgroundRepeat: 'no-repeat',
        backgroundBlendMode: 'multiply'
      }}
    >
      
      {/* SIDEBAR NAVIGATION */}
      <nav className="w-72 bg-card-bg text-white flex flex-col shadow-2xl relative z-20">
        <div className="p-8 pb-6 flex items-center gap-4 border-b border-white/10 mb-4">
          <div className="bg-alpaca-yellow text-black p-2.5 rounded-xl shadow-[0_0_15px_rgba(255,206,0,0.3)]">
            <Rocket size={26} strokeWidth={2.5} />
          </div>
          <div>
            <h1 className="font-extrabold text-xl leading-tight tracking-tight">Alpha Astronaut</h1>
            <div className="flex items-center gap-2 mt-1.5">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-positive opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-positive"></span>
              </span>
              <span className="text-[10px] uppercase tracking-widest text-text-muted font-bold">Systems Online</span>
            </div>
          </div>
        </div>

        <div className="flex-1 px-4 py-2 space-y-1.5 overflow-y-auto">
          {navItems.map(item => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`w-full flex items-center gap-3.5 px-4 py-3.5 rounded-xl text-[15px] font-semibold transition-all duration-200 ${
                  isActive 
                    ? 'bg-white/10 text-white shadow-inner translate-x-1' 
                    : 'text-text-muted hover:text-white hover:bg-white/5 hover:translate-x-1'
                }`}
              >
                <Icon size={20} className={isActive ? 'text-alpaca-yellow' : 'opacity-70'} />
                {item.label}
              </button>
            )
          })}
        </div>
        
        <div className="p-6 mt-auto border-t border-white/5">
          <div className="bg-white/5 border border-white/10 rounded-xl p-4 text-center">
            <p className="text-xs font-bold text-white mb-1">Hackathon Build v2.0</p>
            <p className="text-[10px] text-text-muted">High-Frequency Mode</p>
          </div>
        </div>
      </nav>

      {/* MAIN CONTENT AREA */}
      <main className="flex-1 overflow-y-auto p-8 relative">
        <AnimatePresence mode="wait">
          <motion.div
            key={activeTab}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.2 }}
            className="h-full"
          >
            {activeTab === 'command' && <CommandCenter performance={performance} stats={stats} />}
            {activeTab === 'scanner' && <MarketScanner />}
            {activeTab === 'positions' && <LivePositions />}
            {activeTab === 'history' && <TradeHistory />}
            {activeTab === 'research' && <ResearchLab />}
            {activeTab === 'activity' && <ActivityLog />}
          </motion.div>
        </AnimatePresence>
      </main>
      
    </div>
  )
}

export default App;
