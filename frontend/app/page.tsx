"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Leaf, Map, AlertTriangle, Activity } from "lucide-react";
import { formatNumber } from "@/lib/utils";
import { Button } from "@/components/ui/button";

export default function DashboardPage() {
  // Mock data for initial render
  const stats = {
    totalProjects: 24,
    totalArea: 145000,
    totalCarbon: 3200000,
    activeAlerts: 12
  };

  const recentProjects = [
    { id: '1', name: 'Kaziranga Buffer Zone Afforestation', status: 'MONITORING', area: 12000, method: 'AR-ACM0003' },
    { id: '2', name: 'Manas Community Forestry', status: 'ACTIVE', area: 8500, method: 'AR-AMS0007' },
    { id: '3', name: 'Garo Hills Bamboo Plantation', status: 'VERIFIED', area: 5400, method: 'AR-ACM0003' }
  ];

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      
      <div className="flex justify-between items-center">
        <h2 className="text-3xl font-bold tracking-tight text-slate-900">Dashboard</h2>
        <div className="space-x-3">
          <Button variant="outline">View Reports</Button>
          <Button>New Project</Button>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Projects</CardTitle>
            <Map className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalProjects}</div>
            <p className="text-xs text-muted-foreground">+2 from last month</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Area Monitored</CardTitle>
            <Map className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatNumber(stats.totalArea)} ha</div>
            <p className="text-xs text-muted-foreground">Across 8 states</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Carbon Stock</CardTitle>
            <Leaf className="h-4 w-4 text-mrv-forest" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatNumber(stats.totalCarbon)}</div>
            <p className="text-xs text-muted-foreground">tCO₂e estimated</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Alerts</CardTitle>
            <AlertTriangle className="h-4 w-4 text-amber-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.activeAlerts}</div>
            <p className="text-xs text-muted-foreground">Disturbance alerts pending review</p>
          </CardContent>
        </Card>
      </div>

      {/* Main Content Area */}
      <div className="grid gap-6 md:grid-cols-3">
        
        {/* Recent Projects */}
        <div className="md:col-span-2 space-y-4">
          <h3 className="text-xl font-semibold">Recent Projects</h3>
          <div className="grid gap-4">
            {recentProjects.map(project => (
              <Card key={project.id} className="hover:shadow-md transition-shadow cursor-pointer">
                <CardContent className="p-4 flex justify-between items-center">
                  <div>
                    <h4 className="font-semibold text-lg">{project.name}</h4>
                    <p className="text-sm text-muted-foreground">Methodology: {project.method}</p>
                  </div>
                  <div className="text-right">
                    <div className="font-medium">{formatNumber(project.area)} ha</div>
                    <div className="text-xs mt-1 px-2 py-1 bg-slate-100 rounded-full inline-block text-slate-700">
                      {project.status}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* Alerts Feed */}
        <div className="space-y-4">
          <h3 className="text-xl font-semibold">Recent Alerts</h3>
          <Card>
            <CardContent className="p-4 space-y-4">
              <div className="flex items-start space-x-3">
                <div className="p-2 bg-red-100 rounded-full"><AlertTriangle className="h-4 w-4 text-red-600" /></div>
                <div>
                  <p className="font-medium text-sm">Potential Deforestation</p>
                  <p className="text-xs text-muted-foreground">Kaziranga Buffer Zone • 2 days ago</p>
                </div>
              </div>
              <div className="flex items-start space-x-3">
                <div className="p-2 bg-amber-100 rounded-full"><Activity className="h-4 w-4 text-amber-600" /></div>
                <div>
                  <p className="font-medium text-sm">NDVI Anomaly Detected</p>
                  <p className="text-xs text-muted-foreground">Manas Community • 5 days ago</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
      
    </div>
  );
}
