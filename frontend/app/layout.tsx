import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { LayoutDashboard, Folder, Map, Satellite, BarChart3, Shield, Users, Leaf } from "lucide-react";
import Link from "next/link";
import { cn } from "@/lib/utils";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Ashtalakshmi MRV Platform",
  description: "Measurement, Reporting, and Verification Platform for Forest Monitoring",
};

const navItems = [
  { name: "Dashboard", href: "/", icon: LayoutDashboard },
  { name: "Projects", href: "/projects", icon: Folder },
  { name: "Field Data", href: "/field", icon: Users },
  { name: "Satellite", href: "/satellite", icon: Satellite },
  { name: "Carbon Assessments", href: "/carbon", icon: BarChart3 },
  { name: "Audit Trail", href: "/audit", icon: Shield },
];

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={cn(inter.className, "flex h-screen overflow-hidden bg-slate-50")}>
        
        {/* Sidebar */}
        <aside className="w-64 bg-slate-900 text-slate-300 flex flex-col hidden md:flex">
          <div className="h-16 flex items-center px-6 border-b border-slate-800">
            <Leaf className="w-6 h-6 text-mrv-forest-light mr-3" />
            <span className="text-white font-semibold text-lg tracking-tight">Ashtalakshmi MRV</span>
          </div>
          
          <nav className="flex-1 overflow-y-auto py-4">
            <ul className="space-y-1 px-3">
              {navItems.map((item) => (
                <li key={item.name}>
                  <Link href={item.href} className="flex items-center px-3 py-2.5 rounded-md hover:bg-slate-800 hover:text-white transition-colors group">
                    <item.icon className="w-5 h-5 mr-3 text-slate-400 group-hover:text-mrv-forest-light" />
                    <span className="font-medium text-sm">{item.name}</span>
                  </Link>
                </li>
              ))}
            </ul>
          </nav>
          
          <div className="p-4 border-t border-slate-800 text-xs text-slate-500">
            Govt. of India • MRV Portal v1.0
          </div>
        </aside>

        {/* Main Content */}
        <div className="flex-1 flex flex-col min-w-0">
          
          {/* Header */}
          <header className="h-16 bg-white border-b border-slate-200 flex items-center justify-between px-6 shadow-sm z-10">
            <div className="flex items-center md:hidden">
              <Leaf className="w-6 h-6 text-mrv-forest mr-2" />
              <span className="font-semibold text-slate-800">MRV Platform</span>
            </div>
            
            <div className="hidden md:flex items-center">
              <h1 className="text-xl font-semibold text-slate-800">Overview</h1>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="w-8 h-8 rounded-full bg-mrv-forest text-white flex items-center justify-center font-bold text-sm">
                A
              </div>
            </div>
          </header>

          {/* Page Content */}
          <main className="flex-1 overflow-auto bg-slate-50/50">
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}
