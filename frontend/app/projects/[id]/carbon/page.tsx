"use client";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { formatNumber, formatCarbon } from "@/lib/utils";
import { BiomassTimeline } from "@/components/charts/BiomassTimeline";

export default function CarbonAssessmentPage() {
  const epochs = [
    { id: 'ep4', name: 'Epoch 4 (2023)', date: '2023-10-15', agbd: 45.2, carbon: 345600, uncertainty: 8.5 },
    { id: 'ep3', name: 'Epoch 3 (2022)', date: '2022-10-10', agbd: 41.5, carbon: 315400, uncertainty: 8.7 },
    { id: 'ep2', name: 'Epoch 2 (2021)', date: '2021-10-12', agbd: 38.1, carbon: 289500, uncertainty: 9.1 },
    { id: 'ep1', name: 'Baseline (2020)', date: '2020-10-05', agbd: 35.0, carbon: 265000, uncertainty: 9.5 }
  ];

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Carbon Assessments</h2>
          <p className="text-muted-foreground mt-1">Biomass and carbon stock calculations over time.</p>
        </div>
        <Button>Generate Verification Report</Button>
      </div>

      <div className="grid gap-6 md:grid-cols-3">
        <Card className="md:col-span-2">
          <CardHeader>
            <CardTitle>Aboveground Biomass Density Trend (Mg/ha)</CardTitle>
          </CardHeader>
          <CardContent className="h-[300px]">
            <BiomassTimeline data={epochs} />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Latest Assessment Summary</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <p className="text-sm text-muted-foreground">Total Gross Removals</p>
              <p className="text-2xl font-bold">{formatNumber(345600)} tCO₂e</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Uncertainty Deduction (8.5%)</p>
              <p className="text-lg text-amber-600">-{formatNumber(29376)} tCO₂e</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Buffer Pool (15%)</p>
              <p className="text-lg text-amber-600">-{formatNumber(47433)} tCO₂e</p>
            </div>
            <div className="pt-4 border-t">
              <p className="text-sm font-semibold">Net Tradable Credits</p>
              <p className="text-3xl font-bold text-mrv-forest">{formatNumber(268791)}</p>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Monitoring Epochs</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Epoch</TableHead>
                <TableHead>Assessment Date</TableHead>
                <TableHead className="text-right">Mean AGBD (Mg/ha)</TableHead>
                <TableHead className="text-right">Total Carbon (tCO₂e)</TableHead>
                <TableHead className="text-right">Uncertainty (%)</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {epochs.map((ep) => (
                <TableRow key={ep.id}>
                  <TableCell className="font-medium">{ep.name}</TableCell>
                  <TableCell>{ep.date}</TableCell>
                  <TableCell className="text-right">{ep.agbd}</TableCell>
                  <TableCell className="text-right">{formatNumber(ep.carbon)}</TableCell>
                  <TableCell className="text-right">{ep.uncertainty}%</TableCell>
                  <TableCell className="text-right">
                    <Button variant="ghost" size="sm">Details</Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
