"use client";

import React, { useState } from "react";
import Map from "react-map-gl";
import maplibregl from "maplibre-gl";

interface SwipeCompareProps {
  leftLayerUrl: string;
  rightLayerUrl: string;
  leftLabel?: string;
  rightLabel?: string;
}

export function SwipeCompare({ leftLayerUrl, rightLayerUrl, leftLabel = "Baseline", rightLabel = "Current" }: SwipeCompareProps) {
  const [swipeX, setSwipeX] = useState(50);
  const [isDragging, setIsDragging] = useState(false);

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement> | React.TouchEvent<HTMLDivElement>) => {
    if (!isDragging) return;
    const bounds = e.currentTarget.getBoundingClientRect();
    let clientX = 0;
    
    if ('touches' in e) {
      clientX = e.touches[0].clientX;
    } else {
      clientX = e.clientX;
    }
    
    let newX = ((clientX - bounds.left) / bounds.width) * 100;
    newX = Math.max(0, Math.min(100, newX));
    setSwipeX(newX);
  };

  return (
    <div 
      className="relative w-full h-full overflow-hidden select-none"
      onMouseMove={handleMouseMove}
      onMouseUp={() => setIsDragging(false)}
      onMouseLeave={() => setIsDragging(false)}
      onTouchMove={handleMouseMove}
      onTouchEnd={() => setIsDragging(false)}
    >
      {/* Container for Maps to sync view states (simplified for UI demonstration) */}
      <div className="absolute inset-0 bg-slate-200 flex items-center justify-center text-slate-400">
        Map Synchronization Logic Goes Here
      </div>

      {/* Swipe Divider */}
      <div 
        className="absolute top-0 bottom-0 w-1 bg-white cursor-ew-resize z-10 shadow-[0_0_10px_rgba(0,0,0,0.5)]"
        style={{ left: `${swipeX}%` }}
        onMouseDown={() => setIsDragging(true)}
        onTouchStart={() => setIsDragging(true)}
      >
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-8 h-8 bg-white rounded-full flex items-center justify-center shadow-md">
          <div className="w-1 h-4 border-l-2 border-r-2 border-slate-400"></div>
        </div>
      </div>

      {/* Labels */}
      <div className="absolute top-4 left-4 bg-white/90 px-3 py-1 rounded text-sm font-semibold z-10 shadow">
        {leftLabel}
      </div>
      <div className="absolute top-4 right-4 bg-white/90 px-3 py-1 rounded text-sm font-semibold z-10 shadow">
        {rightLabel}
      </div>
    </div>
  );
}
