import React, { useEffect, useState } from "react";
import Navbar from "../components/Navbar";
import Sidebar from "../components/Sidebar";
import SalesForm, { ProductOption, SaleInput } from "../components/SalesForm";
import api, { ApiListResponse } from "../lib/api";

type Sale = { id: string; productName: string; quantity: number; date: string };

export default function Sales(): React.ReactElement {
  const [items, setItems] = useState<Sale[]>([]);
  const [products, setProducts] = useState<ProductOption[]>([]);
  const [loading, setLoading] = useState(false);
  const [showModal, setShowModal] = useState(false);

  async function load() {
    setLoading(true);
    try {
      const [salesRes, prodRes] = await Promise.all([
        api.get<ApiListResponse<Sale>>("/sales"),
        api.get<ApiListResponse<{ id: string; name: string }>>("/products"),
      ]);
      setItems(salesRes.data.items || (salesRes.data as any));
      setProducts(prodRes.data.items);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, []);

  async function create(data: SaleInput) {
    await api.post("/sales", data);
    setShowModal(false);
    await load();
  }

  return (
    <div className="min-h-screen">
      <Navbar />
      <div className="mx-auto grid max-w-7xl grid-cols-1 gap-6 p-4 md:grid-cols-[16rem_1fr]">
        <Sidebar />
        <main className="space-y-4">
          <div className="flex items-center justify-between">
            <h1 className="text-lg font-semibold">Sales</h1>
            <button className="btn btn-primary" onClick={() => setShowModal(true)}>Add Sale</button>
          </div>
          <div className="card overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200 text-sm">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-2 text-left font-medium text-gray-600">Product</th>
                  <th className="px-4 py-2 text-left font-medium text-gray-600">Quantity</th>
                  <th className="px-4 py-2 text-left font-medium text-gray-600">Date</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100 bg-white">
                {items.map((s) => (
                  <tr key={s.id}>
                    <td className="px-4 py-2">{s.productName}</td>
                    <td className="px-4 py-2">{s.quantity}</td>
                    <td className="px-4 py-2">{new Date(s.date).toLocaleDateString()}</td>
                  </tr>
                ))}
                {!loading && items.length === 0 && (
                  <tr>
                    <td className="px-4 py-8 text-center text-gray-500" colSpan={3}>No sales</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>

          {showModal && (
            <div className="fixed inset-0 z-50 grid place-items-center bg-black/40 p-4">
              <div className="card w-full max-w-lg p-4">
                <div className="mb-3 flex items-center justify-between">
                  <h3 className="text-sm font-semibold">Add Sale</h3>
                  <button onClick={() => setShowModal(false)} className="text-gray-500">✕</button>
                </div>
                <SalesForm
                  products={products}
                  onSubmit={create}
                  onCancel={() => setShowModal(false)}
                />
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}


