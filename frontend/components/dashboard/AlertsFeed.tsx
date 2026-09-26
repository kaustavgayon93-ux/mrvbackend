"use client";

import { AlertTriangle, Flame, Scissors, Eye } from "lucide-react";
import { formatTimeAgo } from "@/lib/utils";

interface Alert {
  id: string;
  type: 'DEFORESTATION' | 'FIRE' | 'ANOMALY';
  severity: 'HIGH' | 'MEDIUM' | 'LOW';
  date: string;
  location: string;
}

const mockAlerts: Alert[] = [
  { id: '1', type: 'DEFORESTATION', severity: 'HIGH', date: '2023-10-24T08:00:00Z', location: 'Kaziranga Sector B' },
  { id: '2', type: 'FIRE', severity: 'HIGH', date: '2023-10-23T14:30:00Z', location: 'Manas Boundary' },
  { id: '3', type: 'ANOMALY', severity: 'MEDIUM', date: '2023-10-20T09:15:00Z', location: 'Garo Hills Plot 42' },
];

export function AlertsFeed() {
  const getIcon = (type: string) => {
    switch(type) {
      case 'DEFORESTATION': return <Scissors className="w-4 h-4" />;
      case 'FIRE': return <Flame className="w-4 h-4" />;
      case 'ANOMALY': return <AlertTriangle className="w-4 h-4" />;
      default: return <AlertTriangle className="w-4 h-4" />;
    }
  };

  const getColors = (severity: string) => {
    switch(severity) {
      case 'HIGH': return 'bg-red-50 text-red-700 border-red-200 icon-red';
      case 'MEDIUM': return 'bg-amber-50 text-amber-700 border-amber-200 icon-amber';
      case 'LOW': return 'bg-blue-50 text-blue-700 border-blue-200 icon-blue';
      default: return 'bg-slate-50 text-slate-700 border-slate-200 icon-slate';
    }
  };

  return (
    <div className="space-y-3">
      {mockAlerts.map(alert => {
        const colors = getColors(alert.severity);
        return (
          <div key={alert.id} className={`p-3 border rounded-lg flex items-start space-x-3 transition-colors hover:bg-slate-50 cursor-pointer ${colors.split(' ').slice(0,3).join(' ')}`}>
            <div className={`p-2 rounded-full bg-white shadow-sm flex-shrink-0 ${alert.severity === 'HIGH' ? 'text-red-600' : alert.severity === 'MEDIUM' ? 'text-amber-600' : 'text-blue-600'}`}>
              {getIcon(alert.type)}
            </div>
            <div className="flex-1 min-w-0">
              <p className="font-semibold text-sm capitalize truncate">
                {alert.type.toLowerCase()} Detected
              </p>
              <p className="text-xs mt-0.5 opacity-80 truncate">{alert.location}</p>
              <p className="text-[10px] mt-1 opacity-70 font-medium uppercase tracking-wider">
                {formatTimeAgo(alert.date)}
              </p>
            </div>
            <button className="p-1.5 hover:bg-white rounded text-slate-400 hover:text-slate-700 transition-colors">
              <Eye className="w-4 h-4" />
            </button>
          </div>
        );
      })}
    </div>
  );
}
