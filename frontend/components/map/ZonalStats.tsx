"use client";

import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { X, Hexagon } from "lucide-react";

export function ZonalStats() {
  const [active, setActive] = React.useState(false);

  if (!active) {
    return (
      <Button 
        variant="secondary" 
        size="sm" 
        className="shadow-md font-semibold"
        onClick={() => setActive(true)}
      >
        <Hexagon className="w-4 h-4 mr-2" /> Draw Area for Stats
      </Button>
    );
  }

  return (
    <Card className="w-72 shadow-lg border-0 ring-1 ring-black/5 relative">
      <button 
        onClick={() => setActive(false)}
        className="absolute top-3 right-3 text-slate-400 hover:text-slate-600"
      >
        <X className="w-4 h-4" />
      </button>
      <CardHeader className="py-3 px-4 border-b bg-slate-50/50">
        <CardTitle className="text-sm font-semibold">Zonal Statistics</CardTitle>
      </CardHeader>
      <CardContent className="p-4 space-y-3">
        <div className="flex justify-between text-sm">
          <span className="text-muted-foreground">Area</span>
          <span className="font-medium">14.5 ha</span>
        </div>
        <div className="flex justify-between text-sm">
          <span className="text-muted-foreground">Mean NDVI</span>
          <span className="font-medium">0.72</span>
        </div>
        <div className="flex justify-between text-sm">
          <span className="text-muted-foreground">Mean AGBD</span>
          <span className="font-medium">45.2 Mg/ha</span>
        </div>
        <div className="pt-2 border-t flex justify-between text-sm font-semibold">
          <span>Est. Carbon</span>
          <span className="text-mrv-forest">324 tCO₂e</span>
        </div>
      </CardContent>
    </Card>
  );
}
