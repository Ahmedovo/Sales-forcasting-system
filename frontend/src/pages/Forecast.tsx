import React, { useMemo } from "react";
import Navbar from "../components/Navbar";
import Sidebar from "../components/Sidebar";
import ChartCard from "../components/ChartCard";

export default function Forecast(): React.ReactElement {
  const forecast = useMemo(() => Array.from({ length: 7 }).map((_, i) => ({ label: `D+${i + 1}`, value: Math.round(60 + Math.random() * 40) })), []);
  const alerts = useMemo(() => [
    { product: "Eggs", daysLeft: 3 },
    { product: "Rice", daysLeft: 5 },
  ], []);

  return (
    <div className="min-h-screen">
      <Navbar />
      <div className="mx-auto grid max-w-7xl grid-cols-1 gap-6 p-4 md:grid-cols-[16rem_1fr]">
        <Sidebar />
        <main className="space-y-6">
          <ChartCard title="7-day Sales Forecast" data={forecast} />
          <div className="card p-4">
            <h3 className="mb-2 text-sm font-semibold">Stock Sufficiency Alerts</h3>
            <ul className="list-disc space-y-1 pl-6 text-sm text-amber-800">
              {alerts.map((a) => (
                <li key={a.product}>{a.product} may run out in {a.daysLeft} days</li>
              ))}
            </ul>
          </div>
        </main>
      </div>
    </div>
  );
}


