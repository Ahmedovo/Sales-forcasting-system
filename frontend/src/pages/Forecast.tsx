import React, { useEffect, useMemo, useState } from "react";
import Navbar from "../components/Navbar";
import Sidebar from "../components/Sidebar";
import ChartCard from "../components/ChartCard";
import api from "../lib/api";

export default function Forecast(): React.ReactElement {
  const [productId, setProductId] = useState<string>("");
  const [forecast, setForecast] = useState<{ label: string; value: number }[]>([]);
  const [products, setProducts] = useState<{ id: string; name: string }[]>([]);

  useEffect(() => {
    (async () => {
      try {
        const res = await api.get<{ items: { id: string; name: string }[] }>("/products");
        const list = res.data.items ?? [];
        setProducts(list);
        if (list.length) setProductId(list[0].id);
      } catch {}
    })();
  }, []);

  useEffect(() => {
    if (!productId) return;
    (async () => {
      try {
        const res = await api.get<{ forecast: number[] }>("/forecast", { params: { product_id: productId, horizon_days: 7 } });
        const arr = (res.data.forecast ?? []).map((v, i) => ({ label: `D+${i + 1}`, value: v as number }));
        setForecast(arr);
      } catch {}
    })();
  }, [productId]);

  return (
    <div className="min-h-screen">
      <Navbar />
      <div className="mx-auto grid max-w-7xl grid-cols-1 gap-6 p-4 md:grid-cols-[16rem_1fr]">
        <Sidebar />
        <main className="space-y-6">
          <div className="card p-4">
            <div className="mb-3 flex items-center justify-between">
              <h3 className="text-sm font-semibold">7-day Sales Forecast</h3>
              <select className="input" value={productId} onChange={(e) => setProductId(e.target.value)}>
                {products.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}
              </select>
            </div>
            <ChartCard title="" data={forecast} />
          </div>
        </main>
      </div>
    </div>
  );
}


