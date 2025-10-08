import React, { useState } from "react";
import Navbar from "../components/Navbar";
import Sidebar from "../components/Sidebar";
import api from "../lib/api";


export default function Admin(): React.ReactElement {
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function uploadCsv() {
    if (!file) {
      setStatus("Please choose a CSV file first.");
      return;
    }
    setLoading(true);
    setStatus(null);
    try {
      const form = new FormData();
      form.append("file", file);
      const res = await api.post("/admin/upload-csv", form, { headers: { "Content-Type": "multipart/form-data" } });
      setStatus(`Imported products: ${res.data.inserted_products ?? 0}, sales: ${res.data.inserted_sales ?? 0}`);
    } catch (e: any) {
      setStatus(e?.response?.data?.error || "Upload failed");
    } finally {
      setLoading(false);
    }
  }

  async function trainNow() {
    setLoading(true);
    setStatus(null);
    try {
      await api.post("/admin/train-now", {});
      setStatus("Training triggered successfully.");
    } catch (e: any) {
      setStatus(e?.response?.data?.error || "Failed to trigger training");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen">
      <Navbar />
      <div className="mx-auto grid max-w-7xl grid-cols-1 gap-6 p-4 md:grid-cols-[16rem_1fr]">
        <Sidebar />
        <main className="space-y-4">
          <div className="flex items-center justify-between">
            <h1 className="text-lg font-semibold">Admin</h1>
          </div>
          <div className="card p-4 space-y-4">
            <div>
              <h2 className="text-sm font-semibold">CSV Import</h2>
              <p className="text-xs text-gray-600">Required CSV columns: name, sku, product price, stock, quantity sale, date of sale (YYYY-MM-DD)</p>
              <div className="mt-2 flex items-center gap-3">
                <input type="file" accept=".csv" onChange={(e) => setFile(e.target.files?.[0] ?? null)} />
                <button className="btn btn-primary" disabled={loading} onClick={uploadCsv}>Upload CSV</button>
              </div>
            </div>
            <div className="pt-2">
              <h2 className="text-sm font-semibold">Model Training</h2>
              <button className="btn border border-gray-300" disabled={loading} onClick={trainNow}>Train now</button>
            </div>
            {status && <p className="text-sm text-gray-700">{status}</p>}
          </div>
        </main>
      </div>
    </div>
  );
}


