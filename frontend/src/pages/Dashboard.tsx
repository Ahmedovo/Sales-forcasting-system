import React from "react";
import Navbar from "../components/Navbar";
import Sidebar from "../components/Sidebar";
import ChartCard from "../components/ChartCard";

const mockSales = Array.from({ length: 14 }).map((_, i) => ({ label: `D${i + 1}`, value: Math.round(50 + Math.random() * 50) }));
const mockForecast = Array.from({ length: 7 }).map((_, i) => ({ label: `D+${i + 1}`, value: Math.round(60 + Math.random() * 40) }));

export default function Dashboard(): React.ReactElement {
  return (
    <div className="min-h-screen">
      <Navbar />
      <div className="mx-auto grid max-w-7xl grid-cols-1 gap-6 p-4 md:grid-cols-[16rem_1fr]">
        <Sidebar />
        <main className="space-y-6">
          <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
            <ChartCard title="Recent Sales" data={mockSales} />
            <ChartCard title="7-day Forecast" data={mockForecast} />
          </div>
          <div className="card p-4">
            <h3 className="mb-2 text-sm font-semibold">Stock Alerts</h3>
            <ul className="list-disc space-y-1 pl-6 text-sm text-red-700">
              <li>Milk 1L is low (8 left)</li>
              <li>Bananas are low (5 left)</li>
            </ul>
          </div>
        </main>
      </div>
    </div>
  );
}


