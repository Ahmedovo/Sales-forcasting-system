import React, { useEffect, useState } from "react";
import Navbar from "../components/Navbar";
import Sidebar from "../components/Sidebar";
import ChartCard from "../components/ChartCard";
import api from "../lib/api";

type Point = { label: string; value: number };

export default function Dashboard(): React.ReactElement {
  const [salesSeries, setSalesSeries] = useState<Point[]>([]);
  const [forecastSeries, setForecastSeries] = useState<Point[]>([]);
  const [alerts, setAlerts] = useState<{ id: string; name: string; stock: number }[]>([]);
  const [productId, setProductId] = useState<string>("");

  useEffect(() => {
    (async () => {
      try {
        const [salesRes, alertsRes, productsRes] = await Promise.all([
          api.get<{ items: Point[] }>("/sales/series", { params: { days: 14 } }),
          api.get<{ items: { id: string; name: string; stock: number }[] }>("/products/alerts", { params: { threshold: 10 } }),
          api.get<{ items: { id: string; name: string }[] }>("/products"),
        ]);
        setSalesSeries(salesRes.data.items ?? []);
        setAlerts(alertsRes.data.items ?? []);
        const prods = productsRes.data.items ?? [];
        if (prods.length) setProductId(prods[0]!.id as unknown as string);
      } catch {}
    })();
  }, []);

  useEffect(() => {
    if (!productId) return;
    (async () => {
      try {
        const res = await api.get<{ forecast: number[] }>("/forecast", { params: { product_id: productId, horizon_days: 7 } });
        const arr = (res.data.forecast ?? []).map((v, i) => ({ label: `D+${i + 1}`, value: v as number }));
        setForecastSeries(arr);
      } catch {}
    })();
  }, [productId]);

  return (
    <div className="min-h-screen">
      <Navbar />
      <div className="mx-auto grid max-w-7xl grid-cols-1 gap-6 p-4 md:grid-cols-[16rem_1fr]">
        <Sidebar />
        <main className="space-y-6">
          <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
            <ChartCard title="Recent Sales" data={salesSeries} />
            <ChartCard title="7-day Forecast" data={forecastSeries} />
          </div>
          <div className="card p-4">
            <h3 className="mb-2 text-sm font-semibold">Stock Alerts</h3>
            <ul className="list-disc space-y-1 pl-6 text-sm text-red-700">
              {alerts.map(a => (
                <li key={a.id}>{a.name} is low ({a.stock} left)</li>
              ))}
            </ul>
          </div>
        </main>
      </div>
    </div>
  );
}


