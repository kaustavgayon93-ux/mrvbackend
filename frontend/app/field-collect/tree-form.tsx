'use client';

import { useState, useEffect } from 'react';
import { saveTree, getPlotTrees } from '@/lib/offline-store';

export default function TreeForm({ plotId, onFinish }: { plotId: string, onFinish: () => void }) {
  const [treeCount, setTreeCount] = useState(0);
  const [surveyorId, setSurveyorId] = useState('');
  
  const initialData = {
    tagNumber: '',
    speciesScientific: '',
    speciesCommon: '',
    dbh: '',
    height: '',
    woodDensity: '0.58',
    isConifer: false,
    healthStatus: 'HEALTHY' as 'HEALTHY' | 'DAMAGED' | 'DEAD' | 'HARVESTED',
    photoAzimuth: ''
  };

  const [formData, setFormData] = useState(initialData);
  const [agbPreview, setAgbPreview] = useState<number | null>(null);

  useEffect(() => {
    // Load existing surveyor ID
    const saved = localStorage.getItem('surveyor_id');
    if (saved) setSurveyorId(saved);

    // Load tree count
    getPlotTrees(plotId).then(trees => setTreeCount(trees.length));
  }, [plotId]);

  useEffect(() => {
    // Calculate AGB using Chave formula (simplified for preview)
    // AGB = 0.0673 × (wood_density × DBH² × height)^0.976
    const d = parseFloat(formData.dbh);
    const h = parseFloat(formData.height) || 10; // default height if missing
    const wd = parseFloat(formData.woodDensity);
    
    if (d > 0 && h > 0 && wd > 0) {
      const agb = 0.0673 * Math.pow(wd * Math.pow(d, 2) * h, 0.976);
      setAgbPreview(agb);
    } else {
      setAgbPreview(null);
    }
  }, [formData.dbh, formData.height, formData.woodDensity]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.tagNumber || !formData.dbh) return;

    localStorage.setItem('surveyor_id', surveyorId);

    await saveTree({
      plotId,
      tagNumber: formData.tagNumber,
      speciesScientific: formData.speciesScientific,
      speciesCommon: formData.speciesCommon,
      dbh: parseFloat(formData.dbh),
      height: formData.height ? parseFloat(formData.height) : undefined,
      woodDensity: parseFloat(formData.woodDensity),
      isConifer: formData.isConifer,
      healthStatus: formData.healthStatus,
      photoAzimuth: formData.photoAzimuth ? parseFloat(formData.photoAzimuth) : undefined,
      surveyorId,
      timestamp: Date.now()
    });

    setTreeCount(prev => prev + 1);
    setFormData({ ...initialData, woodDensity: formData.woodDensity }); // keep some defaults
  };

  return (
    <div className="min-h-screen bg-gray-50 p-4 font-sans pb-24">
      <div className="max-w-md mx-auto bg-white rounded-xl shadow-sm p-6 mb-6">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-bold text-gray-800">Record Tree</h2>
          <span className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm font-bold">
            {treeCount} Trees Added
          </span>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Surveyor ID</label>
            <input 
              required
              type="text" 
              className="w-full p-2 border border-gray-300 rounded bg-gray-50"
              value={surveyorId}
              onChange={e => setSurveyorId(e.target.value)}
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Tag No. *</label>
              <input required type="text" className="w-full p-2 border border-gray-300 rounded" value={formData.tagNumber} onChange={e => setFormData({...formData, tagNumber: e.target.value})} />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Health Status</label>
              <select className="w-full p-2 border border-gray-300 rounded" value={formData.healthStatus} onChange={e => setFormData({...formData, healthStatus: e.target.value as any})}>
                <option value="HEALTHY">Healthy</option>
                <option value="DAMAGED">Damaged</option>
                <option value="DEAD">Dead</option>
                <option value="HARVESTED">Harvested</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Species (Scientific)</label>
            <input type="text" className="w-full p-2 border border-gray-300 rounded" value={formData.speciesScientific} onChange={e => setFormData({...formData, speciesScientific: e.target.value})} />
          </div>

          <div className="grid grid-cols-3 gap-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">DBH (cm) *</label>
              <input required type="number" step="0.1" min="1" className="w-full p-2 border border-gray-300 rounded" value={formData.dbh} onChange={e => setFormData({...formData, dbh: e.target.value})} />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Height (m)</label>
              <input type="number" step="0.1" className="w-full p-2 border border-gray-300 rounded" value={formData.height} onChange={e => setFormData({...formData, height: e.target.value})} />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Density</label>
              <input required type="number" step="0.01" className="w-full p-2 border border-gray-300 rounded" value={formData.woodDensity} onChange={e => setFormData({...formData, woodDensity: e.target.value})} />
            </div>
          </div>

          <div className="flex items-center gap-2 py-2">
            <input type="checkbox" id="conifer" checked={formData.isConifer} onChange={e => setFormData({...formData, isConifer: e.target.checked})} />
            <label htmlFor="conifer" className="text-sm font-medium text-gray-700">Is Conifer</label>
          </div>

          <div className="p-3 bg-blue-50 border border-blue-100 rounded text-sm text-blue-800">
            <strong>Est. Biomass (AGB):</strong> {agbPreview !== null ? `${agbPreview.toFixed(2)} kg` : '--'}
          </div>

          <div>
             <label className="block text-sm font-medium text-gray-700 mb-1">Tree Photo</label>
             <input type="file" accept="image/*" capture="environment" className="w-full p-2 border border-gray-300 rounded bg-white text-sm" />
          </div>

          <button type="submit" className="w-full py-4 bg-green-700 text-white rounded-xl font-bold text-lg hover:bg-green-800 mt-4 shadow-sm">
            Save Tree & Add Another
          </button>
        </form>
      </div>

      <div className="fixed bottom-0 left-0 right-0 p-4 bg-white border-t border-gray-200">
        <button onClick={onFinish} className="w-full max-w-md mx-auto block py-3 bg-gray-800 text-white rounded-xl font-bold hover:bg-gray-900">
          Finish Plot
        </button>
      </div>
    </div>
  );
}
