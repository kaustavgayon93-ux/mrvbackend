"use client";

import React from "react";
import { Play, Pause } from "lucide-react";

export function TimeSlider() {
  const epochs = ['2020 (Baseline)', '2021', '2022', '2023'];
  const [currentIndex, setCurrentIndex] = React.useState(epochs.length - 1);
  const [isPlaying, setIsPlaying] = React.useState(false);

  return (
    <div className="bg-white rounded-lg shadow-lg p-4 flex items-center space-x-6">
      <button 
        onClick={() => setIsPlaying(!isPlaying)}
        className="w-10 h-10 rounded-full bg-slate-100 hover:bg-slate-200 flex items-center justify-center text-slate-700 transition-colors"
      >
        {isPlaying ? <Pause className="w-5 h-5" /> : <Play className="w-5 h-5 ml-1" />}
      </button>

      <div className="flex-1 relative">
        <input 
          type="range" 
          min="0" 
          max={epochs.length - 1} 
          step="1"
          value={currentIndex}
          onChange={(e) => setCurrentIndex(parseInt(e.target.value))}
          className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-mrv-forest"
        />
        <div className="flex justify-between mt-2 px-1">
          {epochs.map((epoch, idx) => (
            <span 
              key={epoch} 
              className={`text-xs font-medium ${idx === currentIndex ? 'text-mrv-forest' : 'text-slate-400'}`}
              onClick={() => setCurrentIndex(idx)}
            >
              {epoch}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}
