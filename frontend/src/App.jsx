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
    <div className="flex h-screen bg-app-bg text-black font-sans overflow-hidden selection:bg-alpaca-yellow selection:text-black">
      
      {/* SIDEBAR NAVIGATION */}
      <nav className="w-64 bg-card-bg text-white flex flex-col">
        <div className="p-6 mb-2 flex items-center gap-3">
          <div className="bg-alpaca-yellow text-black p-2 rounded-lg">
            <Rocket size={24} strokeWidth={2.5} />
          </div>
          <div>
            <h1 className="font-bold text-lg leading-tight tracking-tight">Alpha Astronaut</h1>
            <div className="flex items-center gap-2 mt-1">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-positive opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-positive"></span>
              </span>
              <span className="text-[10px] uppercase tracking-widest text-text-muted font-bold">Systems Online</span>
            </div>
          </div>
        </div>

        <div className="flex-1 px-4 space-y-1">
          {navItems.map(item => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-colors ${
                  isActive 
                    ? 'bg-white/10 text-white' 
                    : 'text-text-muted hover:text-white hover:bg-white/5'
                }`}
              >
                <Icon size={18} className={isActive ? 'text-alpaca-yellow' : ''} />
                {item.label}
              </button>
            )
          })}
        </div>
        
        <div className="p-6">
          <div className="bg-white/5 rounded p-3 text-xs text-center text-text-muted">
            Hackathon Build v2.0
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
