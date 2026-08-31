import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Terminal } from 'lucide-react';

export function ActivityLog() {
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    fetch('http://127.0.0.1:8080/api/activity_log')
      .then(res => res.json())
      .then(data => setLogs(data))
      .catch(console.error);

    // Simulated streaming update every 3 seconds for demo purposes
    const interval = setInterval(() => {
      fetch('http://127.0.0.1:8080/api/activity_log_stream')
        .then(res => res.json())
        .then(newLog => {
          if (newLog) setLogs(prev => [newLog, ...prev].slice(0, 50));
        })
        .catch(() => {});
    }, 3000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="animate-in fade-in duration-500 h-full flex flex-col">
      <div className="mb-4">
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <Terminal className="text-alpaca-yellow" /> Agent Decision Stream
        </h1>
        <p className="text-alpaca-muted mt-2">Real-time internal monologue and execution pipeline of the trading agent.</p>
      </div>

      <div className="bg-[#050505] border border-alpaca-border rounded-xl flex-1 overflow-hidden shadow-2xl relative font-mono text-sm">
        <div className="absolute inset-0 overflow-y-auto p-6 space-y-4">
          <AnimatePresence initial={false}>
            {logs.map((log, idx) => (
              <motion.div 
                key={log.id || idx}
                initial={{ opacity: 0, x: -20, height: 0 }}
                animate={{ opacity: 1, x: 0, height: 'auto' }}
                transition={{ duration: 0.3 }}
                className="flex gap-4 border-l-2 border-alpaca-border/30 pl-4 py-1"
              >
                <div className="text-alpaca-muted w-20 shrink-0">{log.time}</div>
                <div className="w-24 shrink-0 font-bold">{log.icon} {log.action}</div>
                <div className={`${log.highlight ? 'text-alpaca-yellow font-bold' : 'text-gray-300'}`}>
                  {log.message}
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
          {logs.length === 0 && (
            <div className="text-alpaca-muted animate-pulse">Waiting for agent activity...</div>
          )}
        </div>
      </div>
    </div>
  );
}
