import React from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export function PerformanceChart({ data }) {
  return (
    <div className="h-[300px] w-full">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
          <defs>
            <linearGradient id="colorPnL" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#FFCE00" stopOpacity={0.4}/>
              <stop offset="95%" stopColor="#FFCE00" stopOpacity={0}/>
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} opacity={0.5} />
          <XAxis dataKey="time" stroke="#94A3B8" fontSize={12} tickLine={false} axisLine={false} />
          <YAxis stroke="#94A3B8" fontSize={12} tickLine={false} axisLine={false} tickFormatter={(value) => `$${value}`} />
          <Tooltip 
            contentStyle={{ backgroundColor: '#1C1917', borderColor: '#334155', borderRadius: '8px', color: '#fff' }}
            itemStyle={{ color: '#FFCE00', fontWeight: 'bold' }}
          />
          <Area type="monotone" dataKey="pnl" stroke="#FFCE00" strokeWidth={3} fillOpacity={1} fill="url(#colorPnL)" />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
