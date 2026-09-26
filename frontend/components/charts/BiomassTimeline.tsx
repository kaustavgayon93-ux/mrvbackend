"use client";

import React from "react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Area, AreaChart, ComposedChart } from "recharts";

interface BiomassData {
  name: string;
  agbd: number;
  uncertainty: number;
}

interface Props {
  data: BiomassData[];
}

export function BiomassTimeline({ data }: Props) {
  // Transform data to ascending order for charts and calculate bounds
  const chartData = [...data].reverse().map(d => ({
    name: d.name.split(' ')[0], // 'Epoch 1', 'Baseline', etc.
    agbd: d.agbd,
    upper: d.agbd * (1 + d.uncertainty / 100),
    lower: d.agbd * (1 - d.uncertainty / 100)
  }));

  return (
    <ResponsiveContainer width="100%" height="100%">
      <ComposedChart data={chartData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
        <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#64748b' }} dy={10} />
        <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#64748b' }} dx={-10} />
        <Tooltip 
          contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
          labelStyle={{ fontWeight: 'bold', color: '#0f172a', marginBottom: '4px' }}
        />
        <Area type="monotone" dataKey="upper" fill="#a3b18a" stroke="none" fillOpacity={0.2} />
        <Area type="monotone" dataKey="lower" fill="#ffffff" stroke="none" fillOpacity={1} />
        <Line type="monotone" dataKey="agbd" stroke="#588157" strokeWidth={3} dot={{ r: 4, strokeWidth: 2 }} activeDot={{ r: 6 }} />
      </ComposedChart>
    </ResponsiveContainer>
  );
}
