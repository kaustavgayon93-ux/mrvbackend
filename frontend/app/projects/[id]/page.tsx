"use client";

import { useParams } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { MapView } from "@/components/map/MapView";
import { statusColor, formatArea } from "@/lib/utils";
import Link from "next/link";
import { ChevronRight } from "lucide-react";

export default function ProjectDetailPage() {
  const params = useParams();
  const id = params.id;

  // Mock project data
  const project = {
    id: id,
    name: 'Kaziranga Buffer Zone Afforestation',
    status: 'MONITORING',
    methodology: 'AR-ACM0003',
    area: 12000,
    startDate: '2023-01-15'
  };

  const tabs = [
    { name: 'Overview', href: `/projects/${id}`, current: true },
    { name: 'Strata', href: `/projects/${id}/strata`, current: false },
    { name: 'Field Data', href: `/projects/${id}/field`, current: false },
    { name: 'Satellite', href: `/projects/${id}/satellite`, current: false },
    { name: 'Carbon', href: `/projects/${id}/carbon`, current: false },
    { name: 'Audit', href: `/projects/${id}/audit`, current: false },
  ];

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="bg-white border-b px-6 py-4 flex-shrink-0">
        <div className="flex items-center text-sm text-muted-foreground mb-2">
          <Link href="/projects" className="hover:text-primary">Projects</Link>
          <ChevronRight className="h-4 w-4 mx-1" />
          <span className="text-slate-900">{project.name}</span>
        </div>
        
        <div className="flex justify-between items-end">
          <div>
            <h1 className="text-3xl font-bold text-slate-900">{project.name}</h1>
            <div className="flex items-center mt-2 space-x-4">
              <span className={`px-2.5 py-0.5 rounded-full text-xs font-semibold ${statusColor(project.status)}`}>
                {project.status}
              </span>
              <span className="text-sm text-muted-foreground">Methodology: {project.methodology}</span>
              <span className="text-sm text-muted-foreground">Area: {formatArea(project.area)}</span>
            </div>
          </div>
          <div className="space-x-3">
            <Button variant="outline">Edit Details</Button>
            <Button>Run Assessment</Button>
          </div>
        </div>

        {/* Tabs */}
        <nav className="flex space-x-6 mt-6 border-b border-transparent">
          {tabs.map((tab) => (
            <Link
              key={tab.name}
              href={tab.href}
              className={`pb-3 text-sm font-medium border-b-2 ${
                tab.current 
                  ? 'border-mrv-forest text-mrv-forest' 
                  : 'border-transparent text-muted-foreground hover:text-slate-700 hover:border-slate-300'
              }`}
            >
              {tab.name}
            </Link>
          ))}
        </nav>
      </div>

      {/* Content Area - Map and Details */}
      <div className="flex-1 flex flex-col md:flex-row overflow-hidden">
        
        <div className="w-full md:w-1/3 p-6 overflow-y-auto bg-slate-50 border-r">
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Project Overview</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4 text-sm">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-muted-foreground">Start Date</p>
                    <p className="font-medium">{project.startDate}</p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">Crediting Period</p>
                    <p className="font-medium">20 Years</p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">Last Assessment</p>
                    <p className="font-medium">Oct 10, 2023</p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">Total Plots</p>
                    <p className="font-medium">145</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Latest Carbon Stock</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-mrv-forest">345,600</div>
                <p className="text-sm text-muted-foreground">tCO₂e total (Epoch 3)</p>
              </CardContent>
            </Card>
          </div>
        </div>

        <div className="w-full md:w-2/3 h-[400px] md:h-auto bg-slate-200 relative">
          <MapView />
        </div>
      </div>
    </div>
  );
}
