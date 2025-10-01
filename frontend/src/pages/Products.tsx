import React, { useEffect, useState } from "react";
import Navbar from "../components/Navbar";
import Sidebar from "../components/Sidebar";
import ProductForm, { ProductInput } from "../components/ProductForm";
import api, { ApiListResponse } from "../lib/api";

type Product = { id: string; name: string; price: number; stock: number };

export default function Products(): React.ReactElement {
  const [items, setItems] = useState<Product[]>([]);
  const [loading, setLoading] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [editing, setEditing] = useState<Product | null>(null);

  async function load() {
    setLoading(true);
    try {
      const res = await api.get<ApiListResponse<Product>>("/products");
      setItems(res.data.items);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, []);

  async function create(data: ProductInput) {
    await api.post<Product>("/products", data);
    setShowModal(false);
    await load();
  }

  async function update(id: string, data: ProductInput) {
    await api.put<Product>(`/products/${id}`, data);
    setEditing(null);
    await load();
  }

  async function remove(id: string) {
    await api.delete<void>(`/products/${id}`);
    await load();
  }

  return (
    <div className="min-h-screen">
      <Navbar />
      <div className="mx-auto grid max-w-7xl grid-cols-1 gap-6 p-4 md:grid-cols-[16rem_1fr]">
        <Sidebar />
        <main className="space-y-4">
          <div className="flex items-center justify-between">
            <h1 className="text-lg font-semibold">Products</h1>
            <button className="btn btn-primary" onClick={() => setShowModal(true)}>Add Product</button>
          </div>
          <div className="card overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200 text-sm">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-2 text-left font-medium text-gray-600">Name</th>
                  <th className="px-4 py-2 text-left font-medium text-gray-600">Price</th>
                  <th className="px-4 py-2 text-left font-medium text-gray-600">Stock</th>
                  <th className="px-4 py-2" />
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100 bg-white">
                {items.map((p) => (
                  <tr key={p.id}>
                    <td className="px-4 py-2">{p.name}</td>
                    <td className="px-4 py-2">${p.price.toFixed(2)}</td>
                    <td className="px-4 py-2">{p.stock}</td>
                    <td className="px-4 py-2 text-right">
                      <div className="inline-flex gap-2">
                        <button className="btn border border-gray-300" onClick={() => setEditing(p)}>Edit</button>
                        <button className="btn border border-red-200 text-red-700" onClick={() => remove(p.id)}>Delete</button>
                      </div>
                    </td>
                  </tr>
                ))}
                {!loading && items.length === 0 && (
                  <tr>
                    <td className="px-4 py-8 text-center text-gray-500" colSpan={4}>No products</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>

          {(showModal || editing) && (
            <div className="fixed inset-0 z-50 grid place-items-center bg-black/40 p-4">
              <div className="card w-full max-w-lg p-4">
                <div className="mb-3 flex items-center justify-between">
                  <h3 className="text-sm font-semibold">{editing ? "Edit" : "Add"} Product</h3>
                  <button onClick={() => { setShowModal(false); setEditing(null); }} className="text-gray-500">✕</button>
                </div>
                <ProductForm
                  initial={editing ? { name: editing.name, price: editing.price, stock: editing.stock } : undefined}
                  onSubmit={(data) => editing ? update(editing.id, data) : create(data)}
                  onCancel={() => { setShowModal(false); setEditing(null); }}
                />
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}


