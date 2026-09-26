'use client';

import { useState } from 'react';
import { savePlot } from '@/lib/offline-store';

export default function PlotForm({ onSave, onCancel }: { onSave: (id: string) => void, onCancel: () => void }) {
  const [formData, setFormData] = useState({
    plotCode: '',
    project: '',
    radius: 12.62,
    elevation: '',
    slope: '',
    aspect: ''
  });
  
  const [location, setLocation] = useState<{lat: number, lng: number, acc: number} | null>(null);
  const [locating, setLocating] = useState(false);
  const [error, setError] = useState('');

  const captureGPS = () => {
    setLocating(true);
    setError('');
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setLocation({
          lat: pos.coords.latitude,
          lng: pos.coords.longitude,
          acc: pos.coords.accuracy
        });
        setLocating(false);
      },
      (err) => {
        setError(err.message);
        setLocating(false);
      },
      { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
    );
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.plotCode || !formData.project || !location) {
      setError('Please fill required fields and capture GPS location.');
      return;
    }

    try {
      const id = await savePlot({
        plotCode: formData.plotCode,
        project: formData.project,
        radius: formData.radius,
        latitude: location.lat,
        longitude: location.lng,
        accuracy: location.acc,
        elevation: formData.elevation ? parseFloat(formData.elevation) : undefined,
        slope: formData.slope ? parseFloat(formData.slope) : undefined,
        aspect: formData.aspect ? parseFloat(formData.aspect) : undefined,
        synced: false,
        timestamp: Date.now()
      });
      onSave(id);
    } catch (err: any) {
      setError('Failed to save plot: ' + err.message);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-4 font-sans">
      <div className="max-w-md mx-auto bg-white rounded-xl shadow-sm p-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-6">New Plot Survey</h2>
        
        {error && <div className="mb-4 p-3 bg-red-100 text-red-700 rounded-lg text-sm">{error}</div>}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Plot Code *</label>
            <input 
              required
              type="text" 
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
              value={formData.plotCode}
              onChange={e => setFormData({...formData, plotCode: e.target.value})}
              placeholder="e.g. PLOT-001"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Project *</label>
            <select 
              required
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
              value={formData.project}
              onChange={e => setFormData({...formData, project: e.target.value})}
            >
              <option value="">Select Project...</option>
              <option value="PROJECT_A">Assam Afforestation</option>
              <option value="PROJECT_B">Meghalaya REDD+</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Plot Radius (m) *</label>
            <input 
              required
              type="number" 
              step="0.01"
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
              value={formData.radius}
              onChange={e => setFormData({...formData, radius: parseFloat(e.target.value)})}
            />
          </div>

          <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
            <h3 className="text-sm font-semibold text-gray-700 mb-2">GPS Location *</h3>
            <button 
              type="button"
              onClick={captureGPS}
              className="w-full py-2 bg-blue-100 text-blue-700 rounded font-medium hover:bg-blue-200"
            >
              {locating ? 'Acquiring...' : 'Capture GPS Coordinates'}
            </button>
            {location && (
              <div className="mt-3 text-sm text-gray-600">
                <p>Lat: {location.lat.toFixed(6)}</p>
                <p>Lon: {location.lng.toFixed(6)}</p>
                <p className={location.acc > 5 ? "text-red-500 font-bold" : "text-green-600"}>
                  Accuracy: {location.acc.toFixed(1)}m
                  {location.acc > 5 && ' (Warning: Accuracy > 5m)'}
                </p>
              </div>
            )}
          </div>

          <div className="grid grid-cols-3 gap-2">
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">Elev (m)</label>
              <input type="number" className="w-full p-2 border rounded" value={formData.elevation} onChange={e => setFormData({...formData, elevation: e.target.value})} />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">Slope (°)</label>
              <input type="number" className="w-full p-2 border rounded" value={formData.slope} onChange={e => setFormData({...formData, slope: e.target.value})} />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">Aspect (°)</label>
              <input type="number" className="w-full p-2 border rounded" value={formData.aspect} onChange={e => setFormData({...formData, aspect: e.target.value})} />
            </div>
          </div>

          <div className="flex gap-3 mt-8">
            <button type="button" onClick={onCancel} className="flex-1 py-3 bg-gray-200 text-gray-800 rounded-lg font-bold">
              Cancel
            </button>
            <button type="submit" className="flex-[2] py-3 bg-green-700 text-white rounded-lg font-bold hover:bg-green-800">
              Save & Add Trees
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
