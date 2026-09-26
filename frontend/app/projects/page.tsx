"use client";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { statusColor, formatArea, formatDate } from "@/lib/utils";
import Link from "next/link";
import { Search, Plus } from "lucide-react";

export default function ProjectsPage() {
  const projects = [
    { id: '1', name: 'Kaziranga Buffer Zone Afforestation', status: 'MONITORING', methodology: 'AR-ACM0003', area: 12000, startDate: '2023-01-15' },
    { id: '2', name: 'Manas Community Forestry', status: 'ACTIVE', methodology: 'AR-AMS0007', area: 8500, startDate: '2023-06-10' },
    { id: '3', name: 'Garo Hills Bamboo Plantation', status: 'VERIFIED', methodology: 'AR-ACM0003', area: 5400, startDate: '2022-11-20' },
    { id: '4', name: 'Nameri Eco-Restoration', status: 'DRAFT', methodology: 'AR-AMS0007', area: 3200, startDate: '2024-02-01' }
  ];

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Projects</h2>
          <p className="text-muted-foreground mt-1">Manage afforestation and restoration projects.</p>
        </div>
        <Button>
          <Plus className="mr-2 h-4 w-4" /> New Project
        </Button>
      </div>

      <div className="flex items-center space-x-2">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input type="search" placeholder="Search projects..." className="pl-8" />
        </div>
      </div>

      <div className="border rounded-md bg-white">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Name</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Methodology</TableHead>
              <TableHead className="text-right">Area (ha)</TableHead>
              <TableHead>Start Date</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {projects.map((project) => (
              <TableRow key={project.id}>
                <TableCell className="font-medium">
                  <Link href={`/projects/${project.id}`} className="hover:underline text-primary">
                    {project.name}
                  </Link>
                </TableCell>
                <TableCell>
                  <span className={`px-2.5 py-0.5 rounded-full text-xs font-semibold ${statusColor(project.status)}`}>
                    {project.status}
                  </span>
                </TableCell>
                <TableCell>{project.methodology}</TableCell>
                <TableCell className="text-right">{formatArea(project.area)}</TableCell>
                <TableCell>{formatDate(project.startDate)}</TableCell>
                <TableCell className="text-right">
                  <Button variant="ghost" size="sm" asChild>
                    <Link href={`/projects/${project.id}`}>View</Link>
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
