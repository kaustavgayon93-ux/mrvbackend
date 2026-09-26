"use client";

import { Button } from "@/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Input } from "@/components/ui/input";
import { Search, Upload, Plus } from "lucide-react";
import { MapView } from "@/components/map/MapView";

export default function FieldDataPage() {
  const plots = [
    { code: 'PLT-001', project: 'Kaziranga Buffer', lat: 26.5, lng: 93.1, trees: 45, carbon: 12.4 },
    { code: 'PLT-002', project: 'Kaziranga Buffer', lat: 26.51, lng: 93.12, trees: 38, carbon: 9.8 },
    { code: 'PLT-003', project: 'Manas Community', lat: 26.7, lng: 90.9, trees: 52, carbon: 15.1 },
  ];

  return (
    <div className="flex flex-col h-full">
      <div className="p-6 pb-0 flex justify-between items-center bg-white border-b flex-shrink-0">
        <div className="mb-6">
          <h2 className="text-3xl font-bold tracking-tight">Field Data</h2>
          <p className="text-muted-foreground mt-1">Ground truth measurements and sample plots.</p>
        </div>
        <div className="space-x-3 mb-6">
          <Button variant="outline"><Upload className="mr-2 h-4 w-4" /> Bulk Import CSV</Button>
          <Button><Plus className="mr-2 h-4 w-4" /> Add Plot</Button>
        </div>
      </div>

      <div className="flex-1 flex flex-col md:flex-row overflow-hidden">
        {/* Plot List */}
        <div className="w-full md:w-1/2 flex flex-col border-r bg-white overflow-hidden">
          <div className="p-4 border-b">
            <div className="relative">
              <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input type="search" placeholder="Search plot codes or projects..." className="pl-8" />
            </div>
          </div>
          <div className="flex-1 overflow-auto p-4">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Plot Code</TableHead>
                  <TableHead>Project</TableHead>
                  <TableHead className="text-right">Trees</TableHead>
                  <TableHead className="text-right">Carbon (t)</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {plots.map((plot) => (
                  <TableRow key={plot.code} className="cursor-pointer hover:bg-slate-50">
                    <TableCell className="font-medium">{plot.code}</TableCell>
                    <TableCell>{plot.project}</TableCell>
                    <TableCell className="text-right">{plot.trees}</TableCell>
                    <TableCell className="text-right">{plot.carbon}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </div>

        {/* Map View */}
        <div className="w-full md:w-1/2 h-[400px] md:h-auto bg-slate-100">
          <MapView />
        </div>
      </div>
    </div>
  );
}
