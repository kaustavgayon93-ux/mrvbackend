"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ArrowUpRight, ArrowDownRight } from "lucide-react";
import { formatNumber } from "@/lib/utils";

interface CarbonSummaryProps {
  totalCarbon: number;
  previousCarbon: number;
  grossRemovals: number;
  uncertainty: number;
  buffer: number;
}

export function CarbonSummary({ totalCarbon, previousCarbon, grossRemovals, uncertainty, buffer }: CarbonSummaryProps) {
  const percentChange = ((totalCarbon - previousCarbon) / previousCarbon) * 100;
  const isPositive = percentChange >= 0;

  return (
    <Card className="border-2 border-mrv-forest/20">
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground">Net Tradable Credits</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex items-end justify-between mb-4">
          <div className="text-4xl font-bold text-slate-900">{formatNumber(totalCarbon)}</div>
          <div className={`flex items-center text-sm font-semibold ${isPositive ? 'text-green-600' : 'text-red-600'}`}>
            {isPositive ? <ArrowUpRight className="w-4 h-4 mr-1" /> : <ArrowDownRight className="w-4 h-4 mr-1" />}
            {Math.abs(percentChange).toFixed(1)}%
          </div>
        </div>

        <div className="space-y-2 text-sm pt-4 border-t border-slate-100">
          <div className="flex justify-between">
            <span className="text-muted-foreground">Gross Removals</span>
            <span className="font-medium">{formatNumber(grossRemovals)} tCO₂e</span>
          </div>
          <div className="flex justify-between">
            <span className="text-muted-foreground">Uncertainty Deduction</span>
            <span className="text-amber-600 font-medium">-{formatNumber(uncertainty)} tCO₂e</span>
          </div>
          <div className="flex justify-between">
            <span className="text-muted-foreground">Buffer Pool Contribution</span>
            <span className="text-amber-600 font-medium">-{formatNumber(buffer)} tCO₂e</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
