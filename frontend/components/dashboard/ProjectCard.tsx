"use client";

import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { statusColor, formatArea } from "@/lib/utils";
import { MapView } from "@/components/map/MapView";
import { useRouter } from "next/navigation";

interface ProjectCardProps {
  id: string;
  name: string;
  status: string;
  area: number;
  latestAGBD?: number;
  plotsCount?: number;
}

export function ProjectCard({ id, name, status, area, latestAGBD = 45.2, plotsCount = 145 }: ProjectCardProps) {
  const router = useRouter();

  return (
    <Card 
      className="overflow-hidden cursor-pointer hover:shadow-md transition-all border-slate-200 hover:border-slate-300"
      onClick={() => router.push(`/projects/${id}`)}
    >
      <div className="h-32 bg-slate-100 relative pointer-events-none">
        <MapView zoom={10} />
      </div>
      <CardContent className="p-4">
        <div className="flex justify-between items-start mb-2">
          <h3 className="font-semibold text-lg leading-tight line-clamp-1 flex-1 pr-2" title={name}>{name}</h3>
          <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider ${statusColor(status)}`}>
            {status}
          </span>
        </div>
        
        <div className="grid grid-cols-3 gap-2 mt-4 pt-4 border-t border-slate-100">
          <div>
            <p className="text-[10px] text-muted-foreground uppercase tracking-wider">Area</p>
            <p className="font-medium text-sm">{formatArea(area)}</p>
          </div>
          <div>
            <p className="text-[10px] text-muted-foreground uppercase tracking-wider">AGBD</p>
            <p className="font-medium text-sm">{latestAGBD} <span className="text-xs text-muted-foreground">Mg/ha</span></p>
          </div>
          <div>
            <p className="text-[10px] text-muted-foreground uppercase tracking-wider">Plots</p>
            <p className="font-medium text-sm">{plotsCount}</p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
