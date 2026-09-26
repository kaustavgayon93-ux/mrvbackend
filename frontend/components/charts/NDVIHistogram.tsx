"use client";

import React from "react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

const data = [
  { name: '0.0-0.2', value: 120, fill: '#a98467' }, // Bare soil / Earth
  { name: '0.2-0.4', value: 340, fill: '#dad7cd' }, // Sparse veg
  { name: '0.4-0.6', value: 850, fill: '#a3b18a' }, // Moderate veg
  { name: '0.6-0.8', value: 1200, fill: '#588157' }, // Dense veg
  { name: '0.8-1.0', value: 430, fill: '#344e41' },  // Very dense veg
];

export function NDVIHistogram() {
  return (
    <ResponsiveContainer width="100%" height="100%">
      <BarChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
        <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fontSize: 11, fill: '#64748b' }} dy={5} />
        <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 11, fill: '#64748b' }} />
        <Tooltip cursor={{ fill: '#f1f5f9' }} contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }} />
        <Bar dataKey="value" radius={[2, 2, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}
