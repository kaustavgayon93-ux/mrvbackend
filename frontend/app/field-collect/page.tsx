'use client';

import { useEffect, useState } from 'react';
import { Plot, getPendingSubmissions, getAllPlots } from '@/lib/offline-store';
import PlotForm from './plot-form';
import TreeForm from './tree-form';

export default function FieldCollectPage() {
  const [view, setView] = useState<'list' | 'plot-form' | 'tree-form'>('list');
  const [plots, setPlots] = useState<Plot[]>([]);
  const [pendingCount, setPendingCount] = useState(0);
  const [isOnline, setIsOnline] = useState(true);
  const [lastSynced, setLastSynced] = useState<Date | null>(null);
  const [currentPlotId, setCurrentPlotId] = useState<string | null>(null);

  useEffect(() => {
    setIsOnline(navigator.onLine);
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    
    loadData();

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  const loadData = async () => {
    try {
      const allPlots = await getAllPlots();
      const pending = await getPendingSubmissions();
      setPlots(allPlots);
      setPendingCount(pending.length);
    } catch (e) {
      console.error('Error loading data:', e);
    }
  };

  const handleSync = async () => {
    if (!isOnline) {
      alert("Cannot sync offline");
      return;
    }
    try {
      const pending = await getPendingSubmissions();
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Mark all as synced (mock)
      const { markSynced } = await import('@/lib/offline-store');
      for (const p of pending) {
        if (p.plot.id) await markSynced(p.plot.id);
      }
      setLastSynced(new Date());
      loadData();
      alert("Sync complete!");
    } catch (e) {
      console.error('Sync failed', e);
      alert("Sync failed");
    }
  };

  if (view === 'plot-form') {
    return (
      <PlotForm 
        onSave={(plotId) => {
          setCurrentPlotId(plotId);
          setView('tree-form');
        }}
        onCancel={() => setView('list')}
      />
    );
  }

  if (view === 'tree-form' && currentPlotId) {
    return (
      <TreeForm 
        plotId={currentPlotId}
        onFinish={() => {
          setView('list');
          loadData();
        }}
      />
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-4 font-sans">
      <header className="mb-6 bg-white p-4 rounded-xl shadow-sm">
        <h1 className="text-2xl font-bold text-green-800">MRV Field Data</h1>
        <div className="flex items-center justify-between mt-2 text-sm text-gray-600">
          <div className="flex items-center gap-2">
            <div className={`w-3 h-3 rounded-full ${isOnline ? 'bg-green-500' : 'bg-red-500'}`}></div>
            {isOnline ? 'Online' : 'Offline'}
          </div>
          {lastSynced && <span>Last synced: {lastSynced.toLocaleTimeString()}</span>}
        </div>
      </header>

      <div className="grid gap-4 mb-8">
        <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-100 flex justify-between items-center">
          <div>
            <h2 className="text-lg font-semibold text-gray-800">Pending Submissions</h2>
            <p className="text-3xl font-bold text-green-700 mt-1">{pendingCount}</p>
          </div>
          <button 
            onClick={handleSync}
            disabled={!isOnline || pendingCount === 0}
            className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed text-white px-6 py-3 rounded-lg font-medium transition-colors"
          >
            Sync Now
          </button>
        </div>
      </div>

      <button 
        onClick={() => setView('plot-form')}
        className="w-full bg-green-700 hover:bg-green-800 text-white p-4 rounded-xl font-bold text-lg shadow-md transition-colors"
      >
        + New Plot Survey
      </button>

      <div className="mt-8">
        <h3 className="text-gray-500 font-semibold mb-3">RECENT PLOTS</h3>
        <div className="space-y-3">
          {plots.sort((a, b) => b.timestamp - a.timestamp).map(plot => (
            <div key={plot.id} className="bg-white p-4 rounded-lg shadow-sm border border-gray-100 flex justify-between items-center">
              <div>
                <p className="font-bold text-gray-800">{plot.plotCode}</p>
                <p className="text-sm text-gray-500">{new Date(plot.timestamp).toLocaleDateString()}</p>
              </div>
              <span className={`text-xs px-2 py-1 rounded-full font-medium ${plot.synced ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'}`}>
                {plot.synced ? 'Synced' : 'Pending'}
              </span>
            </div>
          ))}
          {plots.length === 0 && (
            <p className="text-gray-400 text-center py-8">No plots recorded yet.</p>
          )}
        </div>
      </div>
    </div>
  );
}
