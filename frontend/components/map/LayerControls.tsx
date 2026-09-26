"use client";

import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Layers } from "lucide-react";

interface Layer {
  id: string;
  name: string;
  visible: boolean;
  opacity?: number;
}

export function LayerControls() {
  const [layers, setLayers] = React.useState<Layer[]>([
    { id: 'satellite', name: 'Satellite Imagery (Sentinel-2)', visible: true },
    { id: 'ndvi', name: 'NDVI Index', visible: false },
    { id: 'agbd', name: 'Biomass (AGBD)', visible: false, opacity: 0.8 },
    { id: 'alerts', name: 'Forest Loss Alerts', visible: true },
    { id: 'plots', name: 'Sample Plots', visible: true },
    { id: 'boundary', name: 'Project Boundary', visible: true },
  ]);

  const toggleLayer = (id: string) => {
    setLayers(layers.map(l => l.id === id ? { ...l, visible: !l.visible } : l));
  };

  return (
    <Card className="w-64 shadow-lg border-0 ring-1 ring-black/5">
      <CardHeader className="py-3 px-4 border-b bg-slate-50/50">
        <CardTitle className="text-sm font-semibold flex items-center">
          <Layers className="w-4 h-4 mr-2" /> Layers
        </CardTitle>
      </CardHeader>
      <CardContent className="p-2">
        <ul className="space-y-1">
          {layers.map(layer => (
            <li key={layer.id} className="px-2 py-1.5 hover:bg-slate-50 rounded text-sm flex items-center">
              <input 
                type="checkbox" 
                checked={layer.visible}
                onChange={() => toggleLayer(layer.id)}
                className="mr-2.5 rounded border-slate-300 text-mrv-forest focus:ring-mrv-forest"
              />
              <span className="flex-1 truncate">{layer.name}</span>
            </li>
          ))}
        </ul>
      </CardContent>
    </Card>
  );
}
